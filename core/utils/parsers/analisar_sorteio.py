from typing import Optional


__all__ = ['analisar_sorteio']


def analisar_sorteio(concursos: list[dict]) -> Optional[list[dict]]:
    """
    Normaliza as chaves de cada linha lida do `lotomania.csv`.

    O cabeçalho original da planilha da Caixa vem com nomes de coluna como
    `'Ganhadores 15 pontos'` ou `'Rateio Nenhum'`; essa função converte esse
    formato para chaves previsíveis (`'ganhadores_15'`, `'rateio_0'`, etc.) e
    deixa as demais colunas em minúsculo, para uso pelos extractors.
    """
    try:

        dados_concurso = []

        for concurso in concursos:

            analise = {}

            for chave, valor in concurso.items():

                if 'Ganhadores' in chave or 'Rateio' in chave:

                    _key = chave.split(' ')
                    analise[f'{_key[0].lower()}_{_key[1] if _key[1] != "Nenhum" else "0"}'] = valor

                else:

                    analise[chave.lower()] = valor

            dados_concurso.append(analise)

        return dados_concurso

    except (TypeError, AttributeError, ValueError):
        return None
