from typing import Optional

from config.settings import BASE_DIR

from core.utils import (
    analisar_sorteio,
    leitor_csv,
    extrair_premios_sorteio_lotomania,
    extrair_referencias_sorteio_lotomania,
    extrair_numeros_sorteio_lotomania
)


__all__ = ['dados_sorteios_lotomania']


ARQUIVO_CSV = BASE_DIR / 'core/data/file/lotomania.csv'

def dados_sorteios_lotomania() -> Optional[list[dict]]:
    """
    Lê e interpreta `core/data/file/lotomania.csv`, devolvendo uma lista com
    um dicionário por sorteio (chaves `sorteio`, `numeros` e `premios`,
    prontos para uso em `create_sorteio`/`bulk_create_sorteio_premio`).

    Retorna `None` se o arquivo CSV não existir, e uma lista vazia se ele
    existir mas não tiver nenhum sorteio.
    """

    if not ARQUIVO_CSV.exists():
        return None

    sorteios = []
    conteudo = leitor_csv(ARQUIVO_CSV)
    analisador = analisar_sorteio(conteudo)

    if analisador:

        for item in analisador:

            sorteios.append(
                {
                    'sorteio': extrair_referencias_sorteio_lotomania(item),
                    'numeros': extrair_numeros_sorteio_lotomania(item, 'bola'),
                    'premios': extrair_premios_sorteio_lotomania(item),
                }
            )

    return sorteios
