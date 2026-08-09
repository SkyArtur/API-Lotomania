from typing import Optional

from .analisar_numeros import analisar_numeros


__all__ = ['analisar_pontos']


def analisar_pontos(valor: str | int) -> Optional[int | float]:
    """
    Valida e normaliza uma pontuação de prêmio da Lotomania.

    Aceita apenas os valores possíveis de pontos (0 ou de 15 a 20); qualquer
    outro valor, ou um texto que não possa ser convertido para número,
    resulta em `None`.
    """
    try:

        referencias = {0, 15, 16, 17, 18, 19, 20}
        pontos = analisar_numeros(valor, inteiro=True) if isinstance(valor, str) else valor

        if pontos not in referencias:
            return None

        return pontos

    except (ValueError, TypeError):
        return None