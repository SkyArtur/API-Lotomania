from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


__all__ = ['Numero']


class Numero(models.Model):
    """Um dos 100 números válidos (0 a 99) para apostas e sorteios da Lotomania."""

    valor = models.SmallIntegerField(primary_key=True, validators=[MinValueValidator(0), MaxValueValidator(99)])

    class Meta:

        db_table = 'numero'
        verbose_name = 'Número'
        verbose_name_plural = 'Números'
        ordering = ['valor']

    def __str__(self):
        return f'{self.valor:02d}'

    def __repr__(self):
        return f'<Numero: {self.__str__()}>'

    @property
    def vezes_sorteado(self):
        """Quantidade de sorteios em que esse número já saiu."""
        return self.sorteios.count()

    @property
    def vezes_apostado(self):
        """Quantidade de apostas que já incluíram esse número."""
        return self.apostas.count()
