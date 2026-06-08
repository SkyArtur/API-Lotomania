from django.db import models

from core.models.abstracts import Prize

__all__ = ['BetPrize']


class BetPrize(Prize):
    bet = models.ForeignKey(to='Bet', on_delete=models.CASCADE, related_name='prizes')
    contest = models.ForeignKey(to='Contest', on_delete=models.CASCADE, related_name='bets_prizes', null=True, blank=True)

    class Meta:
        db_table = 'bet_prize'
        verbose_name = 'Prêmio de Aposta'
        verbose_name_plural = 'Prêmios de Apostas'
        ordering = ['-bet__date', '-points']
        constraints = [
            models.UniqueConstraint(fields=['bet', 'contest', 'points'], name='unique_bet_prize_contest_points')
        ]

    def __str__(self):
        return f'{self.bet.id:03d}: {self.points:02d} pontos - R$ {self.value:.2f}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.bet.id}>'
