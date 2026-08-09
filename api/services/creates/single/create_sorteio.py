from core.models import Sorteio


__all__ = ['create_sorteio']


def create_sorteio(dados_sorteio: dict) -> Sorteio:
    """Cria o registro base de um `Sorteio` (sem números sorteados ou prêmios)."""

    sorteio = Sorteio.objects.create(
        referencia=dados_sorteio['referencia'],
        data=dados_sorteio['data']
    )

    return sorteio
