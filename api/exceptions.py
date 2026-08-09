import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


__all__ = ['custom_exception_handler']


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Envolve o exception_handler padrão do DRF para garantir que a API *sempre*
    responda em JSON a um cliente HTTP (app, script, etc.), mesmo diante de um
    erro que o DRF não sabe tratar.

    O exception_handler padrão só converte em Response as exceções que herdam
    de rest_framework.exceptions.APIException (e Http404/PermissionDenied).
    Qualquer outra exceção (erro de banco não previsto, bug de programação,
    etc.) faz `drf_exception_handler` devolver None, e nesse caso o Django
    assume o tratamento do erro sozinho: em produção (DEBUG=False), ele
    responde com uma página de erro em HTML — o que quebra qualquer cliente
    que espere JSON, pois `response.json()` estoura uma exceção de parsing.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        return response

    logger.exception('Erro não tratado na API: %s', exc)

    if settings.DEBUG:
        # Em desenvolvimento, deixa o Django mostrar a página de debug padrão
        # com o traceback completo - é mais útil para investigar o problema.
        return None

    return Response(
        {'detail': 'Erro interno no servidor. Tente novamente mais tarde.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
