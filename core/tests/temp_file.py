import csv
import tempfile
from pathlib import Path


__all__ = ['TEMP_FILE']

_campos = [
    'Concurso',
    'Data Sorteio',
    'Bola1',
    'Bola2',
    'Bola3',
    'Ganhadores 20 acertos',
    'Rateio 20 acertos',
    'Ganhadores 20 acertos',
    'Rateio 20 acertos',
    'Ganhadores 19 acertos',
    'Rateio 19 acertos',
    'Ganhadores 18 acertos',
    'Rateio 18 acertos',
    'Ganhadores 17 acertos',
    'Rateio 17 acertos',
    'Ganhadores 16 acertos',
    'Rateio 16 acertos',
    'Ganhadores 15 acertos',
    'Rateio 15 acertos',
    'Ganhadores Nenhum Número',
    'Rateio Nenhum Número',
]

fake_dados_lotomania = [
    {
        'Concurso': '0211',
        'Data Sorteio': '21/10/1999',
        'Bola1': '82',
        'Bola2': '45',
        'Bola3': '36',
        'Ganhadores 20 acertos': 0,
        'Rateio 20 acertos': "R$0,00",
        'Ganhadores 19 acertos': 2,
        'Rateio 19 acertos': "R$21.500,00",
        'Ganhadores 18 acertos': 10,
        'Rateio 18 acertos': "R$2.150,00",
        'Ganhadores 17 acertos': 100,
        'Rateio 17 acertos': "R$250,00",
        'Ganhadores 16 acertos': 1000,
        'Rateio 16 acertos': "R$21,50",
        'Ganhadores 15 acertos': 10000,
        'Rateio 15 acertos': "R$2,15",
        'Ganhadores Nenhum Número': 0,
        'Rateio Nenhum Número': "R$0,00",
    },
    {
        'Concurso': '0212',
        'Data Sorteio': '12/11/1999',
        'Bola1': '11',
        'Bola2': '10',
        'Bola3': '25',
        'Ganhadores 20 acertos': 1,
        'Rateio 20 acertos': "R$1.150.000,00",
        'Ganhadores 19 acertos': 2,
        'Rateio 19 acertos': "R$11.500,00",
        'Ganhadores 18 acertos': 10,
        'Rateio 18 acertos': "R$1.150,00",
        'Ganhadores 17 acertos': 100,
        'Rateio 17 acertos': "R$150,00",
        'Ganhadores 16 acertos': 1000,
        'Rateio 16 acertos': "R$11,50",
        'Ganhadores 15 acertos': 10000,
        'Rateio 15 acertos': "R$1,15",
        'Ganhadores Nenhum Número': 1,
        'Rateio Nenhum Número': "R$150.000,00",
    },
]


with tempfile.NamedTemporaryFile(mode='w+', newline='', encoding='utf-8', delete=False) as arquivo_csv:
    escrever = csv.DictWriter(arquivo_csv, fieldnames=_campos)
    escrever.writeheader()

    for d in fake_dados_lotomania:
        escrever.writerow(d)

    arquivo_csv.flush()

    TEMP_FILE = Path(arquivo_csv.name).resolve()
