from django.db import models

from core.models.abstracts import Prize

__all__ = ['ContestPrize']


class ContestPrize(Prize):
    contest = models.ForeignKey(to='Contest', on_delete=models.CASCADE, related_name='prizes')
    winners = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'contest_prize'
        verbose_name = 'Prêmio de concurso'
        verbose_name_plural = 'Prêmios de concursos'

    def __str__(self):
        return f'{self.contest.reference:04d}: {self.points:02d} pontos - R$ {self.value:.2f}'

    def __repr__(self):
        return f'<ContestPrize {self.contest.reference:04d}>'
