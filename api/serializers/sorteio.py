from decimal import Decimal
from rest_framework import serializers
from core.models import Sorteio, Numero


__all__ = [
    'SorteioModelSerializer',
    'SorteioSerializer',
    'SorteioPremioSerializer',
    'SorteioListSerializer',
    'SorteioDetalheModelSerializer',
    'SorteioCreateSerializer',
    'SorteioNumeroListSerializer',
]


class SorteioPremioSerializer(serializers.Serializer):
    """Faixa de premiação de um sorteio: pontuação, quantidade de ganhadores e valor pago."""

    pontos = serializers.IntegerField()
    ganhadores = serializers.IntegerField(min_value=0)
    valor = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.00'))


class SorteioModelSerializer(serializers.ModelSerializer):
    """Serializer base com todos os campos do model `Sorteio`; ponto de partida para as variações abaixo."""

    class Meta:

        model = Sorteio
        fields = '__all__'


class SorteioSerializer(serializers.Serializer):
    """Campos de entrada comuns a um sorteio: referência, data, números sorteados e tabela de prêmios."""

    referencia = serializers.IntegerField(min_value=1)
    data = serializers.DateField(format="%Y-%m-%d")
    numeros = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=99))
    premios = SorteioPremioSerializer(many=True)


class SorteioNumeroListSerializer(serializers.ModelSerializer):
    """Representação enxuta de um sorteio: apenas a referência e os números sorteados."""

    numeros = serializers.SlugRelatedField(many=True, read_only=True, slug_field='valor')

    class Meta:

        model = Sorteio
        fields = ['referencia', 'numeros']


class SorteioListSerializer(SorteioModelSerializer):
    """Representação resumida de um sorteio, usada na listagem (`GET sorteios/`)."""

    class Meta:

        model = Sorteio
        fields = ['referencia', 'data']


class SorteioDetalheModelSerializer(SorteioModelSerializer):
    """Representação completa de um sorteio: números sorteados e tabela de prêmios."""

    numeros = serializers.SlugRelatedField(many=True, read_only=True, slug_field='valor')
    premios = SorteioPremioSerializer(many=True, read_only=True)

    class Meta:

        model = Sorteio
        fields = ['referencia', 'data', 'numeros', 'premios']


class SorteioCreateSerializer(SorteioSerializer):
    """Valida os dados de entrada para o cadastro manual de um novo sorteio (`POST sorteios/`)."""

    def validate_referencia(self, referencia):
        """Garante que a referência do concurso ainda não esteja cadastrada."""

        if Sorteio.objects.filter(referencia=referencia).exists():
            raise serializers.ValidationError('Sorteio já registrado.')

        return referencia

    def validate_numeros(self, numeros):
        """Garante exatamente 20 números, todos distintos e todos números válidos (0-99)."""

        map_numeros = {
            numero.valor: numero
            for numero in Numero.objects.all()
        }

        if len(numeros) != 20:
            raise serializers.ValidationError('Quantidade de números inválida.')

        if len(set(numeros)) != len(numeros):
            raise serializers.ValidationError('Número duplicado: cada número deve ser informado uma única vez.')

        if any(num not in map_numeros for num in numeros):
            raise serializers.ValidationError('Um ou mais números informados não existem.')
        return numeros

    def validate_premios(self, premios):
        """Garante que cada faixa de pontos seja válida (0 ou 15-20) e informada uma única vez."""

        pontos_validos = {0, 15, 16, 17, 18, 19, 20}

        if any(premio['pontos'] not in pontos_validos for premio in premios):
            raise serializers.ValidationError('Pontuação de prêmio inválida: utilize 0 ou um valor entre 15 e 20.')

        pontos = [premio['pontos'] for premio in premios]

        if len(set(pontos)) != len(pontos):
            raise serializers.ValidationError('Pontos de prêmios devem ser únicos.')

        return premios
