import logging

from celery import shared_task

from core.services import atualizar_sorteios

__all__ = ['atualizar_sorteios_task']

logger = logging.getLogger(__name__)


@shared_task(name='core.tasks.atualizar_sorteios_task')
def atualizar_sorteios_task() -> dict:
    """
    Tarefa agendada do Celery (terça, quinta e sábado às 21h) que sincroniza
    os sorteios a partir do `lotomania.csv`, registra o resultado no log e o
    devolve em um formato simples (serializável), já que o retorno de uma
    task Celery precisa poder ser serializado.
    """
    resultado = atualizar_sorteios()

    for sorteio in resultado.criado:
        logger.info('Sorteio %04d importado.', sorteio.referencia)
    for referencia, erro in resultado.falhou:
        logger.error('Sorteio %04d falhou: %s', referencia, erro)

    return {
        'criado': [
            sorteio.referencia
            for sorteio in resultado.criado
        ],
        'falhou': resultado.falhou,
    }
