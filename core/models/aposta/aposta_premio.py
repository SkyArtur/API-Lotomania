from django.db import models

from core.models.abstracts import PremioAbstrato


__all__ = ['ApostaPremio']


class ApostaPremio(PremioAbstrato):
    """Prêmio recebido por uma aposta em um sorteio específico, para uma faixa de pontos."""

    aposta = models.ForeignKey(to='Aposta', on_delete=models.CASCADE, related_name='premios')
    sorteio = models.ForeignKey(to='Sorteio', on_delete=models.CASCADE, related_name='aposta_premio', null=True, blank=True)

    class Meta:

        db_table = 'aposta_premio'
        verbose_name = 'Prêmio de Aposta'
        verbose_name_plural = 'Prêmios de Apostas'
        ordering = ['-aposta__data', '-pontos']
        constraints = [
            models.UniqueConstraint(fields=['aposta', 'sorteio', 'pontos'], name='unique_aposta_premio')
        ]

    def __str__(self):
        return f'{self.aposta.id:03d}: {self.pontos:02d} pontos - R$ {self.valor:.2f}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.aposta.id}>'
