from typing import Optional


__all__ = ['analisar_numeros']


def analisar_numeros(valor: str, *, brl: bool = False, decimal: bool = False, inteiro: bool = False) -> Optional[float | int]:
    """
    Converte um número em texto (como vem do CSV da Caixa) para `float` ou `int`.

    Use `brl=True` para valores monetários (`'R$ 1.234,56'`), `decimal=True`
    para números com separador decimal em vírgula (`'1.234,56'`) ou nenhum
    dos dois para inteiros com separador de milhar (`'1.234'`). Retorna
    `None` se o texto não puder ser convertido.
    """
    try:

        if brl:
            numero = valor.replace('R$', '').replace('.', '').replace(',', '.')
        elif decimal:
            numero = valor.replace('.', '').replace(',', '.')
        else:
            numero = valor.replace(',', '')

        return float(numero) if not inteiro else int(numero)

    except (ValueError, TypeError):
        return None