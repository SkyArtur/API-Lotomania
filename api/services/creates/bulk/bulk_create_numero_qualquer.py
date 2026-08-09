from core.models import Numero, Aposta, ApostaNumero, Sorteio, SorteioNumero


__all__ = ['bulk_create_numero_qualquer']


def bulk_create_numero_qualquer(obj: Aposta | Sorteio, lista_numeros: list[int]) -> None:
    """
    Associa em lote uma lista de números a uma `Aposta` (via `ApostaNumero`)
    ou a um `Sorteio` (via `SorteioNumero`), dependendo do tipo de `obj`.
    """

    numeros = []
    map_numeros = {
        numero.valor: numero
        for numero in Numero.objects.all()
    }

    if isinstance(obj, Aposta):

        for num in lista_numeros:
            numeros.append(ApostaNumero(aposta=obj, numero=map_numeros[num]))
        ApostaNumero.objects.bulk_create(numeros)

    elif isinstance(obj, Sorteio):

        for num in lista_numeros:
            numeros.append(SorteioNumero(sorteio=obj, numero=map_numeros[num]))
        SorteioNumero.objects.bulk_create(numeros)

    else:
        raise TypeError('Tipo inválido de objeto.')

    return None