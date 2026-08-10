from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import Numero
from api.serializers import NumeroSerializer


@extend_schema_view(
    list=extend_schema(
        description=(
            'Retorna os 100 números válidos (0 a 99) para apostas e sorteios, cada um já com '
            'a contagem de quantas vezes foi sorteado (`vezes_sorteado`) e de quantas vezes foi '
            'apostado (`vezes_apostado`). Endpoint de leitura pública, não exige autenticação.'
        ),
        responses={200: NumeroSerializer(many=True)}
    )
)
class NumeroViewSet(mixins.ListModelMixin, GenericViewSet):
    """Consulta pública, somente leitura, dos 100 números válidos (0-99) e suas estatísticas."""

    serializer_class = NumeroSerializer
    queryset = Numero.objects.prefetch_related('apostas', 'sorteios')
    lookup_field = 'valor'
    http_method_names = ['get', 'head', 'options']
