import csv
from pathlib import Path


__all__ = ['leitor_csv']


def leitor_csv(arquivo: Path) -> list[dict]:
    """Lê um arquivo CSV com cabeçalho e retorna cada linha como um dicionário."""

    with arquivo.open('r', newline='', encoding='utf-8') as arquivo_csv:

        conteudo = csv.DictReader(arquivo_csv)

        return list(conteudo)
