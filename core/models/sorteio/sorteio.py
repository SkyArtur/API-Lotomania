from django.db import models

__all__ = ['Sorteio']


class Sorteio(models.Model):
    """Um concurso oficial da Lotomania: referência, data, os 20 números sorteados e a tabela de prêmios."""

    referencia = models.PositiveIntegerField(primary_key=True)
    data = models.DateField()
    numeros = models.ManyToManyField('Numero', related_name='sorteios', through='SorteioNumero')

    class Meta:

        db_table = 'sorteio'
        verbose_name = 'Sorteio'
        verbose_name_plural = 'Sorteios'
        ordering = ['-referencia', '-data']

    def __str__(self):
        return f'{self.referencia:04d}'

    def __repr__(self):
        return f'<Sorteio: {self.__str__()}>'
