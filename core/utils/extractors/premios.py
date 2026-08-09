from core.utils.parsers import analisar_numeros

__all__ = ['extrair_premios_sorteio_lotomania']


def extrair_premios_sorteio_lotomania(dados: dict) -> list[dict]:
    """
    Monta a tabela de prêmios de um sorteio a partir de uma linha já
    normalizada do CSV, lendo as colunas `ganhadores_<pontos>` e
    `rateio_<pontos>` para cada faixa de pontuação válida (0 e 15 a 20).
    """
    premios = []

    for _index in [0, *(n for n in range(15, 21))]:

        premios.append(
            {
                'pontos': _index,
                'ganhadores': analisar_numeros(dados[f'ganhadores_{_index}'], inteiro=True),
                'valor': analisar_numeros(dados[f'rateio_{_index}'], brl=True)
            }
        )

    return premios
