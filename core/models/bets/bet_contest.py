from django.db import models

__all__ = ['BetContest']


class BetContest(models.Model):
    bet = models.ForeignKey(to='Bet', on_delete=models.CASCADE)
    contest = models.ForeignKey(to='Contest', on_delete=models.PROTECT)

    class Meta:
        db_table = 'bet_contest'
        verbose_name = 'Concurso apostado'
        verbose_name_plural = 'Concursos apostados'
        constraints = [
            models.UniqueConstraint(fields=['contest', 'bet'], name='unique_contest_bet')
        ]
