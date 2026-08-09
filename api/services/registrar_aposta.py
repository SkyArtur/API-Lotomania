from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from .creates import (
    create_aposta,
    bulk_create_numero_qualquer,
    bulk_create_aposta_sorteio,
    bulk_create_aposta_resultado,
    bulk_create_aposta_premio
)


__all__ = ['registrar_aposta']


def registrar_aposta(request, aposta: dict) -> bool:
    """
    Orquestra o registro completo de uma nova aposta.

    Além de criar o registro da ``Aposta``, associa os 50 números escolhidos,
    vincula a aposta a todos os sorteios já cadastrados cuja referência esteja
    dentro do intervalo ``inicial``/``final`` e calcula, para cada um desses
    sorteios, os acertos e os prêmios correspondentes. Toda a operação roda em
    uma única transação: se qualquer etapa falhar, nada é persistido.
    """
    try:
        with transaction.atomic():
            nova_aposta = create_aposta(request, aposta)
            bulk_create_numero_qualquer(nova_aposta, aposta['numeros'])
            bulk_create_aposta_sorteio(nova_aposta)
            bulk_create_aposta_resultado(nova_aposta)
            bulk_create_aposta_premio(nova_aposta)
            return True
    except (IntegrityError, KeyError) as error:
        raise ValidationError({'detail': 'Erro ao criar uma nova aposta.'}) from error
