import csv
from pathlib import Path


__all__ = ['csv_reader']

def csv_reader(file_path: Path) -> list[dict]:
    """Lê um arquivo CSV e retorna seus registros como dicionários.

    Args:
        file_path: Caminho do arquivo CSV que será lido.

    Returns:
        Lista de dicionários em que cada item representa uma linha do arquivo
        CSV, usando os cabeçalhos como chaves.
    """
    with file_path.open('r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)
