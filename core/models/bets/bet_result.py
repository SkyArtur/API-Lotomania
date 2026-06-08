from django.db import models
from core.models.abstracts import Result

__all__ = ['BetResult']


class BetResult(Result):
    contest = models.ForeignKey(to='Contest', on_delete=models.CASCADE, related_name='bet_results')
    bet = models.ForeignKey(to='Bet', on_delete=models.CASCADE,related_name='results')

    class Meta:
        db_table = 'bet_result'
        verbose_name = 'Resultado da aposta'
        verbose_name_plural = 'Resultados das apostas'
        constraints = [
            models.UniqueConstraint(fields=['contest', 'bet'], name='unique_result_contest_bet')
        ]
