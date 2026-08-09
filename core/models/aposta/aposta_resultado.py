from django.db import models

from core.models.abstracts import ResultadoAbstrato


__all__ = ['ApostaResultado']


class ApostaResultado(ResultadoAbstrato):
    """Resultado da conferência de uma aposta contra um sorteio específico: quantos números ela acertou."""

    aposta = models.ForeignKey(to='Aposta', on_delete=models.CASCADE, related_name='resultados')
    sorteio = models.ForeignKey(to='Sorteio', on_delete=models.CASCADE, related_name='aposta_resultado')

    class Meta:

        db_table = 'aposta_resultado'
        verbose_name = 'Resultado da aposta'
        verbose_name_plural = 'Resultados das apostas'
        constraints = [
            models.UniqueConstraint(fields=['aposta', 'sorteio'], name='unique_aposta_resultado')
        ]
