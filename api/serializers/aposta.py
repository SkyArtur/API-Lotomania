from decimal import Decimal

from rest_framework import serializers

from core.models import Numero, Aposta


__all__ = [
    'ApostaResultadoSerializer',
    'ApostaPremioSerializer',
    'ApostaModelSerializer',
    'ApostaSerializer',
    'ApostaNumeroListSerializer',
    'ApostaListSerializer',
    'ApostaDetalheSerializer',
    'ApostaCreateSerializer',
]


class ApostaResultadoSerializer(serializers.Serializer):
    """Resultado da conferência de uma aposta contra um sorteio: acertos normais e espelhados."""

    sorteio = serializers.IntegerField(source='sorteio.referencia', read_only=True)
    acertos = serializers.IntegerField()
    acertos_espelhados = serializers.IntegerField()


class ApostaPremioSerializer(serializers.Serializer):
    """Prêmio recebido por uma aposta em um sorteio, para uma faixa de pontos."""

    sorteio = serializers.IntegerField(source='sorteio.referencia', read_only=True)
    pontos = serializers.IntegerField()
    valor = serializers.DecimalField(max_digits=12, decimal_places=2)


class ApostaModelSerializer(serializers.ModelSerializer):
    """Serializer base com todos os campos do model `Aposta`; ponto de partida para as variações abaixo."""

    class Meta:

        model = Aposta
        fields = '__all__'


class ApostaSerializer(serializers.Serializer):
    """Campos de entrada comuns a uma aposta: data, valor, intervalo de concursos, espelho e números."""

    data = serializers.DateField(format="%Y-%m-%d")
    valor = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.00'))
    inicial = serializers.IntegerField(min_value=1)
    final = serializers.IntegerField(min_value=1)
    espelho = serializers.BooleanField(default=True)
    numeros = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=99))


class ApostaNumeroListSerializer(serializers.ModelSerializer):
    """Representação enxuta de uma aposta: apenas o `id` e os números escolhidos."""

    numeros = serializers.SlugRelatedField(many=True, read_only=True, slug_field='valor')

    class Meta:

        model = Aposta
        fields = ['id', 'numeros']


class ApostaListSerializer(ApostaModelSerializer):
    """Representação resumida de uma aposta, usada na listagem (`GET apostas/`)."""

    class Meta:

        model = Aposta
        fields = ['id', 'data', 'valor', 'inicial', 'final', 'espelho']


class ApostaDetalheSerializer(serializers.ModelSerializer):
    """Representação completa de uma aposta: números, sorteios já conferidos, acertos e prêmios."""

    sorteios = serializers.SlugRelatedField(many=True, read_only=True, slug_field='referencia')
    numeros = serializers.SlugRelatedField(many=True, read_only=True, slug_field='valor')
    resultados = ApostaResultadoSerializer(many=True, read_only=True)
    premios = ApostaPremioSerializer(many=True, read_only=True)

    class Meta:

        model = Aposta
        fields = ['id', 'data', 'valor', 'inicial', 'final', 'espelho', 'sorteios', 'numeros', 'resultados', 'premios']


class ApostaCreateSerializer(ApostaSerializer):
    """Valida os dados de entrada para o cadastro de uma nova aposta (`POST apostas/`)."""

    def validate(self, attrs):
        """Garante que o intervalo de concursos (`inicial`/`final`) seja válido."""

        if attrs['inicial'] > attrs['final']:
            raise serializers.ValidationError({
                'final': 'O sorteio final deve ser maior ou igual ao sorteio inicial.'
            })

        return attrs

    def validate_numeros(self, numeros):
        """Garante exatamente 50 números, todos distintos e todos números válidos (0-99)."""

        map_numeros = {
            numero.valor: numero
            for numero in Numero.objects.all()
        }

        if len(numeros) != 50:
            raise serializers.ValidationError('Quantidade de números inválida.')

        if len(set(numeros)) != len(numeros):
            raise serializers.ValidationError('Número duplicado: cada número deve ser informado uma única vez.')

        if any(num not in map_numeros for num in numeros):
            raise serializers.ValidationError('Um ou mais números informados não existem.')

        return numeros
