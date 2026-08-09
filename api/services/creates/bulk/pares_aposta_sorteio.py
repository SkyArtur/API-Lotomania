from core.models import Aposta, Sorteio


__all__ = ['obter_pares_aposta_sorteio']


def obter_pares_aposta_sorteio(obj: Aposta | Sorteio) -> list[tuple]:
    """
    Monta os pares (aposta, sorteio) relevantes para conferência de resultado.

    Recebe uma ``Aposta`` recém-criada e retorna um par para cada sorteio já
    cadastrado que ela cobre, ou recebe um ``Sorteio`` recém-criado e retorna
    um par para cada aposta que o cobre. É esse par que ``bulk_create_aposta_resultado``
    e ``bulk_create_aposta_premio`` usam para calcular acertos e prêmios.
    """

    if isinstance(obj, Aposta):
        return [(obj, sorteio) for sorteio in obj.sorteios.prefetch_related('numeros', 'premios')]

    elif isinstance(obj, Sorteio):
        return [(aposta, obj) for aposta in obj.apostas.prefetch_related('numeros')]

    else:
        raise TypeError('Tipo inválido de objeto.')
