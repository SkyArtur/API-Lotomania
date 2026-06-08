from typing import Optional

from config.settings import BASE_DIR
from .parsers import parse_number, parse_date, parse_contest, parse_bet
from .readers import csv_reader

__all__ = ['extract_contests', 'extract_bets']

CONTEST_CSV = BASE_DIR / 'core/data/lotomania.csv'
BETS_CSV = BASE_DIR / 'core/data/apostas.csv'

def extract_numbers(data: dict, target: str) -> list:
    """Extrai números de um dicionário a partir de uma chave-alvo.

    Args:
        data: Dicionário com os dados que serão analisados.
        target: Texto usado para identificar as chaves que contêm números.

    Returns:
        Lista com os números convertidos para inteiro quando possível.
    """
    numbers = [parse_number(value, integer=True) for key, value in data.items() if target in key]
    return numbers

def extract_basic_data_lotomania(datas: dict) -> dict:
    """Extrai os dados básicos de um concurso da Lotomania.

    Args:
        datas: Dicionário com os dados normalizados de um concurso.

    Returns:
        Dicionário com a referência do concurso e a data do sorteio.
    """
    return {
        'reference': parse_number(datas['concurso'], integer=True),
        'date': parse_date(datas['data sorteio']),
    }

def extract_prizes_lotomania(datas: dict) -> list[dict]:
    """Extrai as faixas de premiação de um concurso da Lotomania.

    Args:
        datas: Dicionário com os dados normalizados de um concurso.

    Returns:
        Lista de dicionários com pontuação, quantidade de ganhadores e valor
        de rateio por faixa de premiação.
    """
    prizes = []
    for _index in [0, *(n for n in range(15, 21))]:
        prizes.append(
            {
                'points': _index,
                'winners': parse_number(datas[f'ganhadores_{_index}'], integer=True),
                'value': parse_number(datas[f'rateio_{_index}'], money=True)
            }
        )
    return prizes

def extract_contests() -> Optional[list[dict]]:
    """Extrai os concursos da Lotomania a partir do arquivo CSV local.

    Returns:
        Lista de dicionários com dados do concurso, números sorteados e
        premiações. Retorna `None` quando o arquivo CSV não existe ou quando o
        conteúdo não pode ser processado.
    """
    contests = []
    if not CONTEST_CSV.exists():
        return None
    content = csv_reader(CONTEST_CSV)
    parser = parse_contest(content)
    if parser:
        for item in parser:
            contests.append(
                {
                    'contest': extract_basic_data_lotomania(item),
                    'numbers': extract_numbers(item, 'bola'),
                    'prizes': extract_prizes_lotomania(item),
                }
            )
    return contests

def extract_bets() -> Optional[list[dict]]:
    """Extrai apostas da Lotomania a partir do arquivo CSV local.

    Returns:
        Lista de dicionários com os dados das apostas. Retorna `None` quando o
        arquivo CSV não existe ou quando o conteúdo não pode ser processado.
    """
    bets = []
    if not BETS_CSV.exists():
        return None
    content = csv_reader(BETS_CSV)
    parsed = parse_bet(content)
    if parsed:
        for item in parsed:
            bets.append(
                {
                    'id': parse_number(item['id'], integer=True),
                    'date': parse_date(item['data']),
                    'value': parse_number(item['valor'], money=True),
                    'initial': parse_number(item['inicial'], integer=True),
                    'final': parse_number(item['final'], integer=True),
                    'numbers': extract_numbers(item, 'num'),
                }
            )
    return bets
