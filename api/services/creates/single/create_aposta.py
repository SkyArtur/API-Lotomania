from core.models import Aposta


__all__ = ['create_aposta']


def create_aposta(request, dados_aposta: dict) -> Aposta:
    """Cria o registro base de uma `Aposta` (sem números, sorteios, resultados ou prêmios) para o usuário autenticado."""

    aposta = Aposta.objects.create(
        data=dados_aposta['data'],
        valor=dados_aposta['valor'],
        inicial=dados_aposta['inicial'],
        final=dados_aposta['final'],
        espelho=dados_aposta['espelho'],
        apostador=request.user
    )

    return aposta
