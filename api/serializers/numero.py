from rest_framework import serializers

from core.models import Numero


__all__ = ['NumeroSerializer']


class NumeroSerializer(serializers.ModelSerializer):
    """Um número válido (0-99), com quantas vezes já foi sorteado e quantas vezes já foi apostado."""

    vezes_sorteado = serializers.SerializerMethodField()
    vezes_apostado = serializers.SerializerMethodField()

    class Meta:
        model = Numero
        fields = ['valor', 'vezes_sorteado', 'vezes_apostado']

    def get_vezes_sorteado(self, obj):
        """Quantidade de sorteios em que esse número já saiu."""
        return obj.vezes_sorteado

    def get_vezes_apostado(self, obj):
        """Quantidade de apostas que já incluíram esse número."""
        return obj.vezes_apostado
