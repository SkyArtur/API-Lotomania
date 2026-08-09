from core.models import Aposta, ApostaResultado, Sorteio
from .pares_aposta_sorteio import obter_pares_aposta_sorteio


__all__ = ['bulk_create_aposta_resultado']


def bulk_create_aposta_resultado(obj: Aposta | Sorteio) -> None:
    """
    Calcula e cria em lote os acertos (``ApostaResultado``) de cada par aposta/sorteio.

    Compara os números da aposta com os números sorteados e grava a
    quantidade de acertos "normais" e, quando a aposta é espelhada, a
    quantidade de acertos considerando o espelho (complementar a 20 pontos).
    """

    resultados = []
    pares = obter_pares_aposta_sorteio(obj)

    for aposta, sorteio in pares:
        aposta_numeros = {
            numero.valor
            for numero in aposta.numeros.all()
        }
        sorteio_numeros = {
            numero.valor
            for numero in sorteio.numeros.all()
        }
        acertos = len(aposta_numeros.intersection(sorteio_numeros))
        acertos_espelhados = 20 - acertos
        resultados.append(
            ApostaResultado(
                aposta=aposta,
                sorteio=sorteio,
                acertos=acertos,
                acertos_espelhados=acertos_espelhados if aposta.espelho else 0
            )
        )

    ApostaResultado.objects.bulk_create(resultados)
    return None
