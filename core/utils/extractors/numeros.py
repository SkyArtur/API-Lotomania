from core.utils.parsers import analisar_numeros

__all__ = ['extrair_numeros_sorteio_lotomania']


def extrair_numeros_sorteio_lotomania(dados: dict, alvo: str) -> list:
    """
    Extrai, de uma linha já normalizada do CSV, os valores das colunas cujo
    nome contém `alvo` (por exemplo, `'bola'`, já que a planilha da Caixa
    tem uma coluna por bola sorteada), convertendo cada um para inteiro.
    """
    numeros = [analisar_numeros(valor, inteiro=True) for chave, valor in dados.items() if alvo in chave]

    return numeros
