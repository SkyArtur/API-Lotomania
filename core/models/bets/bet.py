from django.db import models
from django.utils.timezone import localdate

__all__ = ['Bet']


class Bet(models.Model):
    date = models.DateField(default=localdate)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    initial = models.PositiveSmallIntegerField()
    final = models.PositiveSmallIntegerField()
    mirror = models.BooleanField(default=True)
    numbers = models.ManyToManyField('Number', related_name='bets', through='BetNumber')
    contests = models.ManyToManyField('Contest', related_name='bets', through='BetContest')

    class Meta:
        db_table = 'bet'
        verbose_name = 'Aposta'
        verbose_name_plural = 'Apostas'
        ordering = ['-date']

    def __str__(self):
        return f'{self.id:03d}'

    def __repr__(self):
        return f'<Bet: {self.__str__()}>'
