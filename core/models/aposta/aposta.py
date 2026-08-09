from django.db import models
from django.utils.timezone import localdate


__all__ = ['Aposta']


class Aposta(models.Model):
    """
    Uma aposta da Lotomania: 50 números escolhidos por um apostador, válidos
    para o intervalo de concursos `inicial`-`final`. Quando `espelho` é
    verdadeiro, os acertos também são conferidos pelo espelho dos números
    sorteados (complementar a 20 pontos).
    """

    data = models.DateField(default=localdate)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    inicial = models.PositiveIntegerField()
    final = models.PositiveIntegerField()
    espelho = models.BooleanField(default=True)
    numeros = models.ManyToManyField('Numero', related_name='apostas', through='ApostaNumero')
    sorteios = models.ManyToManyField('Sorteio', related_name='apostas', through='ApostaSorteio')
    apostador = models.ForeignKey('Apostador', on_delete=models.CASCADE, related_name='apostas')

    class Meta:

        db_table = 'aposta'
        verbose_name = 'Aposta'
        verbose_name_plural = 'Apostas'
        ordering = ['-data']

    def __str__(self):
        return f'{self.id:03d}'

    def __repr__(self):
        return f'<Aposta: {self.__str__()}>'
