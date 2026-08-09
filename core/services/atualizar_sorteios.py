from typing import NamedTuple

from django.db import IntegrityError, transaction

from core.models import Sorteio
from core.data import dados_sorteios_lotomania
from api.services.creates import (
    create_sorteio,
    bulk_create_numero_qualquer,
    bulk_create_sorteio_premio,
    bulk_create_aposta_sorteio,
    bulk_create_aposta_resultado,
    bulk_create_aposta_premio,
)


__all__ = ['atualizar_sorteios', 'AtualizarResultadosSorteios']


class AtualizarResultadosSorteios(NamedTuple):
    """Resultado de uma sincronização: sorteios criados e sorteios que falharam ao importar."""

    criado: list[Sorteio]
    falhou: list[tuple[int, str]]


def atualizar_sorteios() -> AtualizarResultadosSorteios:
    """
    Sincroniza os sorteios ainda não cadastrados a partir do `lotomania.csv`.

    Compara as referências já existentes no banco com as referências lidas
    do CSV, e cria (em ordem crescente) somente os sorteios novos — a
    operação é idempotente. Cada sorteio é criado em sua própria transação:
    uma falha isolada não impede os demais de serem processados, e é
    reportada em `falhou` ao final. Usado tanto pela sincronização agendada
    do Celery (`core.tasks.atualizar_sorteios_task`) quanto pelo comando
    `manage.py atualizar_sorteios`.
    """
    dados_sorteios = dados_sorteios_lotomania()
    if not dados_sorteios:
        return AtualizarResultadosSorteios(criado=[], falhou=[])

    sorteios_registrados = set(Sorteio.objects.values_list('referencia', flat=True))
    novos_sorteios = sorted(
        (
            item
            for item in dados_sorteios
            if item['sorteio']['referencia'] not in sorteios_registrados
        ),
        key=lambda item: item['sorteio']['referencia']
    )

    criado, falhou = [], []
    for item in novos_sorteios:
        referencia = item['sorteio']['referencia']
        try:
            with transaction.atomic():
                sorteio = create_sorteio(item['sorteio'])
                bulk_create_numero_qualquer(sorteio, item['numeros'])
                bulk_create_sorteio_premio(sorteio, item['premios'])
                bulk_create_aposta_sorteio(sorteio)
                bulk_create_aposta_resultado(sorteio)
                bulk_create_aposta_premio(sorteio)
            criado.append(sorteio)
        except (IntegrityError, KeyError, TypeError) as error:
            falhou.append((referencia, str(error)))

    return AtualizarResultadosSorteios(criado=criado, falhou=falhou)
