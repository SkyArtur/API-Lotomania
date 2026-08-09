from django.db import models


__all__ = ['SorteioNumero']


class SorteioNumero(models.Model):
    """Tabela de associação entre `Sorteio` e `Numero`: um dos 20 números sorteados em um concurso."""

    numero = models.ForeignKey(to='Numero', on_delete=models.PROTECT)
    sorteio = models.ForeignKey(to='Sorteio', on_delete=models.CASCADE)

    class Meta:

        db_table = 'sorteio_numero'
        verbose_name = 'Número sorteado'
        verbose_name_plural = 'Números sorteados'
        constraints = [
            models.UniqueConstraint(fields=['sorteio', 'numero'], name='unique_sorteio_numero')
        ]
