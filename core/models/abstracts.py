from django.db import models

from core.utils import validar_pontos


__all__ = ['PremioAbstrato', 'ResultadoAbstrato']


class PremioAbstrato(models.Model):
    """Campos comuns a um prêmio (de sorteio ou de aposta): pontuação premiada e valor pago."""

    pontos = models.PositiveIntegerField(default=0, validators=[validar_pontos])
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:

        abstract = True


class ResultadoAbstrato(models.Model):
    """Campos comuns a um resultado de conferência: acertos normais e acertos considerando o espelho."""

    acertos = models.PositiveIntegerField()
    acertos_espelhados = models.PositiveIntegerField()

    class Meta:

        abstract = True
