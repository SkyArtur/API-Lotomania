from core.models import Aposta, Sorteio, ApostaSorteio


__all__ = ['bulk_create_aposta_sorteio']


def bulk_create_aposta_sorteio(obj: Aposta | Sorteio) -> None:
    """
    Vincula em lote (`ApostaSorteio`) uma aposta a todos os sorteios que ela
    cobre, ou um sorteio a todas as apostas que o cobrem — dependendo do tipo
    de `obj` —, usando o intervalo `inicial`/`final` de cada aposta.
    """
    aposta_sorteio = []

    if isinstance(obj, Sorteio):
        apostas = Aposta.objects.filter(inicial__lte=obj.referencia, final__gte=obj.referencia)

        for aposta in apostas:
            aposta_sorteio.append(ApostaSorteio(aposta=aposta, sorteio=obj))

    elif isinstance(obj, Aposta):
        sorteios = Sorteio.objects.filter(referencia__gte=obj.inicial, referencia__lte=obj.final)

        for sorteio in sorteios:
            aposta_sorteio.append(ApostaSorteio(aposta=obj, sorteio=sorteio))

    else:
        raise TypeError('Tipo inválido de objeto.')

    ApostaSorteio.objects.bulk_create(aposta_sorteio)
    return None
