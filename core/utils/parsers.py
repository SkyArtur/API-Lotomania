import re
from datetime import date
from typing import Optional


__all__ = ['parse_date', 'parse_number' , 'parse_points', 'parse_contest', 'parse_bet']

def parse_date(date_str: str, *, iso_format: bool = False) -> Optional[date]:
    """Converte uma string de data em um objeto `date`.

    Args:
        date_str: Texto com a data que será convertida.
        iso_format: Indica se a data está no formato ISO, com ano antes do mês
            e do dia.

    Returns:
        Data convertida. Retorna `None` quando o valor não corresponde ao
        formato esperado.
    """
    try:
        pattern = r'^(\d{4})[/-]?(\d{2})[/-](\d{2})$' if iso_format else r'^(\d{2})[/-]?(\d{2})[/-](\d{4})$'
        match = re.match(pattern, date_str)
        if not match:
            return None
        return date.fromisoformat(''.join(match.groups() if iso_format else match.groups()[::-1]))
    except (TypeError, AttributeError, ValueError, Exception):
        return None

def parse_number(value: str, *, money: bool = False, decimal: bool = False, integer: bool = False) -> Optional[float | int]:
    """Converte uma string numérica em número.

    Args:
        value: Texto com o valor numérico que será convertido.
        money: Indica se o valor deve ser tratado como moeda brasileira.
        decimal: Indica se o valor deve ser tratado como número decimal.
        integer: Indica se o retorno deve ser convertido para inteiro.

    Returns:
        Número convertido como `float` ou `int`. Retorna `None` quando o valor
        não pode ser convertido.
    """
    try:
        if money:
            num = value.replace('R$', '').replace('.', '').replace(',', '.')
        elif decimal:
            num = value.replace('.', '').replace(',', '.')
        else:
            num = value.replace(',', '')
        return float(num) if not integer else int(num)
    except (ValueError, TypeError):
        return None

def parse_points(value: str | int, references: set[int]) -> Optional[int | float]:
    """Valida e converte uma pontuação com base em referências permitidas.

    Args:
        value: Pontuação informada como texto ou inteiro.
        references: Conjunto com as pontuações aceitas.

    Returns:
        Pontuação validada. Retorna `None` quando o valor não pode ser
        convertido ou não está entre as referências permitidas.
    """
    try:
        point = parse_number(value, integer=True) if isinstance(value, str) else value
        if point not in references:
            return None
        return point
    except (ValueError, TypeError):
        return None

def parse_contest(content: list[dict]) -> Optional[list[dict]]:
    """Normaliza os dados brutos dos concursos da Lotomania.

    Args:
        content: Lista de dicionários lidos do arquivo CSV de concursos.

    Returns:
        Lista de dicionários com chaves normalizadas. Retorna `None` quando o
        conteúdo não pode ser processado.
    """
    try:
        data_contest = []
        for contest in content:
            parser = {}
            for key, value in contest.items():
                if 'Ganhadores' in key or 'Rateio' in key:
                    _key = key.split(' ')
                    parser[f'{_key[0].lower()}_{_key[1] if _key[1] != "Nenhum" else "0"}'] = value
                else:
                    parser[key.lower()] = value
            data_contest.append(parser)
        return data_contest
    except (TypeError, AttributeError, ValueError, Exception) as error:
        return None

def parse_bet(content: list[dict]) -> Optional[list[dict]]:
    """Normaliza os dados brutos das apostas da Lotomania.

    Args:
        content: Lista de dicionários lidos do arquivo CSV de apostas.

    Returns:
        Lista de dicionários com chaves normalizadas em letras minúsculas.
        Retorna `None` quando o conteúdo não pode ser processado.
    """
    try:
        data_bets = []
        for bet in content:
            parser = {}
            for key, value in bet.items():
                parser[key.lower()] = value
            data_bets.append(parser)
        return data_bets
    except (TypeError, AttributeError, ValueError, Exception):
        return None
