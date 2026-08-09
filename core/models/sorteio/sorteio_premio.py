from django.db import models

from core.models.abstracts import PremioAbstrato


__all__ = ['SorteioPremio']


class SorteioPremio(PremioAbstrato):
    """Faixa de premiação de um sorteio: quantos ganhadores e quanto foi pago para uma pontuação."""

    sorteio = models.ForeignKey(to='Sorteio', on_delete=models.CASCADE, related_name='premios')
    ganhadores = models.PositiveIntegerField(default=0)

    class Meta:

        db_table = 'sorteio_premio'
        verbose_name = 'Prêmio do sorteio'
        verbose_name_plural = 'Prêmios dos sorteios'

    def __str__(self):
        return f'{self.sorteio.referencia:04d}: {self.pontos:02d} pontos - R$ {self.valor:.2f}'

    def __repr__(self):
        return f'<SorteioPremio: {self.sorteio.referencia:04d}>'
