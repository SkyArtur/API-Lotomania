from django.db import models

__all__ = ['BetNumber']


class BetNumber(models.Model):
    bet = models.ForeignKey(to='Bet', on_delete=models.CASCADE)
    number = models.ForeignKey(to='Number', on_delete=models.PROTECT)

    class Meta:
        db_table = 'bet_number'
        verbose_name = 'Número de aposta'
        verbose_name_plural = 'Números de apostas'
        constraints = [
            models.UniqueConstraint(fields=['number', 'bet'], name='unique_number_bet')
        ]
