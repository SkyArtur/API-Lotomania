from decimal import Decimal

from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.models import Apostador, ApostaPremio


__all__ = [
    'ApostadorSerializer',
    'ApostadorRegistroSerializer',
    'ApostadorPerfilSerializer',
    'ApostadorAlterarSenhaSerializer',
    'ApostadorLogoutSerializer',
]


class ApostadorSerializer(serializers.ModelSerializer):
    """Representação básica de um apostador: `id` e `username`."""

    class Meta:
        model = Apostador
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class ApostadorPerfilSerializer(ApostadorSerializer):
    """Perfil do apostador autenticado, com o total apostado e o total já recebido em prêmios."""

    total_apostado = serializers.SerializerMethodField()
    total_premios = serializers.SerializerMethodField()

    class Meta(ApostadorSerializer.Meta):
        fields = ApostadorSerializer.Meta.fields + ['total_apostado', 'total_premios']

    def get_total_apostado(self, obj):
        """Soma do valor de todas as apostas do apostador."""
        total = obj.apostas.aggregate(total=Sum('valor'))['total']
        return total or Decimal('0.00')

    def get_total_premios(self, obj):
        """Soma do valor de todos os prêmios já recebidos pelo apostador."""
        total = ApostaPremio.objects.filter(aposta__apostador=obj).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0.00')


class ApostadorRegistroSerializer(serializers.ModelSerializer):
    """Valida os dados de entrada para o cadastro de um novo apostador (`POST apostador/`)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Apostador
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Cria o apostador usando `create_user`, para que a senha seja hasheada corretamente."""
        return Apostador.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )


class ApostadorAlterarSenhaSerializer(serializers.Serializer):
    """
    Valida a troca de senha do apostador autenticado (`instance` deve ser o
    próprio `request.user`, nunca um apostador informado pelo cliente): exige
    a senha atual para confirmar a identidade e valida a força da nova senha.
    """

    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)

    def validate_senha_atual(self, valor):
        """Garante que a senha atual informada confere com a senha já cadastrada do apostador."""

        if not self.instance.check_password(valor):
            raise serializers.ValidationError('Senha atual incorreta.')

        return valor

    def validate_nova_senha(self, valor):
        """
        Garante que a nova senha atenda aos validadores de força de senha do
        Django. Passa `user=self.instance` (diferente do `password` em
        `ApostadorRegistroSerializer`, onde ainda não existe um apostador
        para comparar) para que validadores como o de similaridade com o
        username também sejam aplicados.
        """

        validate_password(valor, user=self.instance)

        return valor

    def validate(self, attrs):
        """Garante que a nova senha seja diferente da senha atual."""

        if attrs['senha_atual'] == attrs['nova_senha']:
            raise serializers.ValidationError({'nova_senha': 'A nova senha deve ser diferente da senha atual.'})

        return attrs

    def update(self, instance, validated_data):
        """Define a nova senha via `set_password` (garante o hash) e salva apenas o campo alterado."""

        instance.set_password(validated_data['nova_senha'])
        instance.save(update_fields=['password'])

        return instance


class ApostadorLogoutSerializer(serializers.Serializer):
    """Valida o refresh token informado no logout e o invalida (blacklist) ao ser salvo."""

    refresh = serializers.CharField(write_only=True)

    def validate_refresh(self, valor):
        """Garante que o refresh token é válido (assinatura, expiração, ainda não invalidado)."""

        try:
            self.token = RefreshToken(valor)
        except TokenError as erro:
            raise serializers.ValidationError(str(erro))

        return valor

    def save(self, **kwargs):
        """Adiciona o refresh token à blacklist, encerrando a sessão associada a ele."""

        self.token.blacklist()
