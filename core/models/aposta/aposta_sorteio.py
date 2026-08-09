from django.db import models


__all__ = ['ApostaSorteio']


class ApostaSorteio(models.Model):
    """Vínculo entre uma aposta e um sorteio já conferido por ela (referência dentro do intervalo `inicial`-`final`)."""

    aposta = models.ForeignKey(to='Aposta', on_delete=models.CASCADE)
    sorteio = models.ForeignKey(to='Sorteio', on_delete=models.PROTECT)

    class Meta:
        db_table = 'aposta_sorteio'
        verbose_name = 'Sorteio apostado'
        verbose_name_plural = 'Sorteios apostados'
        constraints = [
            models.UniqueConstraint(fields=['aposta', 'sorteio'], name='unique_aposta_sorteio')
        ]
