from core.models import Aposta, Sorteio, ApostaPremio
from .pares_aposta_sorteio import obter_pares_aposta_sorteio


__all__ = ['bulk_create_aposta_premio']


def bulk_create_aposta_premio(obj: Aposta | Sorteio) -> None:
    """
    Cria em lote os prêmios (``ApostaPremio``) de cada par aposta/sorteio.

    Para cada par, usa o ``ApostaResultado`` já calculado (acertos e, se a
    aposta for espelhada, acertos espelhados) e cria um ``ApostaPremio`` para
    cada faixa de pontos premiada no sorteio, evitando duplicar um prêmio já
    registrado para o mesmo par aposta/sorteio/pontos.
    """

    novos_premios = []
    pares_aposta_sorteio = obter_pares_aposta_sorteio(obj)

    for aposta, sorteio in pares_aposta_sorteio:
        resultado = aposta.resultados.filter(sorteio=sorteio).first()

        if resultado is None:
            continue

        pontos = [resultado.acertos]

        if aposta.espelho:
            pontos.append(resultado.acertos_espelhados)

        premios = sorteio.premios.filter(pontos__in=pontos)

        for premio in premios:
            existe = aposta.premios.filter(sorteio=sorteio, pontos=premio.pontos).exists()

            if existe:
                continue

            novos_premios.append(
                ApostaPremio(
                    aposta=aposta,
                    sorteio=sorteio,
                    pontos=premio.pontos,
                    valor=premio.valor
                )
            )

    ApostaPremio.objects.bulk_create(novos_premios)
    return None
