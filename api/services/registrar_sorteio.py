from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from .creates import (
    create_sorteio,
    bulk_create_numero_qualquer,
    bulk_create_sorteio_premio,
    bulk_create_aposta_sorteio,
    bulk_create_aposta_resultado,
    bulk_create_aposta_premio
)


__all__ = ['registrar_sorteio']


def registrar_sorteio(sorteio: dict) -> bool:
    """
    Orquestra o registro completo de um novo sorteio cadastrado manualmente.

    Cria o registro do ``Sorteio``, associa os 20 números sorteados e a
    tabela de prêmios e, em seguida, confere automaticamente todas as
    apostas cujo intervalo (``inicial``/``final``) cobre a referência desse
    sorteio, calculando acertos e premiações. Toda a operação roda em uma
    única transação: se qualquer etapa falhar, nada é persistido.
    """
    try:
        with transaction.atomic():
            novo_sorteio = create_sorteio(sorteio)
            bulk_create_numero_qualquer(novo_sorteio, sorteio['numeros'])
            bulk_create_sorteio_premio(novo_sorteio, sorteio['premios'])
            bulk_create_aposta_sorteio(novo_sorteio)
            bulk_create_aposta_resultado(novo_sorteio)
            bulk_create_aposta_premio(novo_sorteio)
            return True
    except (IntegrityError, KeyError, TypeError) as error:
        raise ValidationError({'detail': 'Erro ao criar um novo sorteio.'}) from error
