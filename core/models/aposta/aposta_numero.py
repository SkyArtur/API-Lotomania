from django.db import models


__all__ = ['ApostaNumero']


class ApostaNumero(models.Model):
    """Tabela de associação entre `Aposta` e `Numero`: um dos 50 números escolhidos em uma aposta."""

    aposta = models.ForeignKey(to='Aposta', on_delete=models.CASCADE)
    numero = models.ForeignKey(to='Numero', on_delete=models.PROTECT)

    class Meta:

        db_table = 'aposta_numero'
        verbose_name = 'Número da aposta'
        verbose_name_plural = 'Números das apostas'
        constraints = [
            models.UniqueConstraint(fields=['aposta', 'numero'], name='unique_aposta_numero')
        ]
