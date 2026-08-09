from core.utils.parsers import analisar_numeros, analisar_datas

__all__ = ['extrair_referencias_sorteio_lotomania']


def extrair_referencias_sorteio_lotomania(dados: dict) -> dict:
    """
    Extrai a referência (número do concurso) e a data do sorteio a partir de
    uma linha já normalizada do CSV.
    """
    return {
        'referencia': analisar_numeros(dados['concurso'], inteiro=True),
        'data': analisar_datas(dados['data sorteio']),
    }
