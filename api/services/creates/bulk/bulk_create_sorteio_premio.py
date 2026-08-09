from core.models import Sorteio, SorteioPremio


__all__ = ['bulk_create_sorteio_premio']


def bulk_create_sorteio_premio(sorteio: Sorteio, lista_premios: list[dict]) -> None:
    """Cria em lote a tabela de prêmios de um sorteio, ignorando as faixas de pontos sem ganhadores."""
    premios = []

    for premio in lista_premios:

        if premio['ganhadores'] > 0:
            premios.append(SorteioPremio(sorteio=sorteio, **premio))

    SorteioPremio.objects.bulk_create(premios)
    return None
