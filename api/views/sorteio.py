from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_view,
    OpenApiResponse
)

from core.models import Sorteio
from api.services import registrar_sorteio
from api.serializers import (
    SorteioDetalheModelSerializer,
    SorteioListSerializer,
    SorteioCreateSerializer,
)


__all__ = ['SorteioViewSet']


@extend_schema_view(
    list=extend_schema(
        description=(
            'Retorna a lista de sorteios cadastrados. Sem filtros, a listagem é resumida '
            '(referência e data). Se algum filtro for aplicado (`referencia`, `data`, '
            '`numeros__valor`, `premios__pontos` ou `premios__valor`), a resposta traz os '
            'detalhes completos (números sorteados e tabela de prêmios) dos sorteios '
            'encontrados. Endpoint de leitura pública, não exige autenticação.'
        ),
        responses={200: SorteioListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        description=(
            'Retorna os detalhes de um sorteio específico, identificado pela sua referência: '
            'os 20 números sorteados e a tabela de prêmios por faixa de pontos.'
        ),
        responses={200: SorteioDetalheModelSerializer}
    ),
    create=extend_schema(
        description=(
            'Cadastra manualmente um novo sorteio da Lotomania, exigindo autenticação. Requer '
            'referência única, data, exatamente 20 números distintos entre 0 e 99 e a tabela de '
            'prêmios (pontuações válidas: 0 ou de 15 a 20, cada uma informada uma única vez). Ao '
            'ser criado, o sorteio é conferido automaticamente contra todas as apostas cujo '
            'intervalo (`inicial`/`final`) cobre a sua referência.'
        ),
        request=SorteioCreateSerializer,
        responses={201: OpenApiResponse(description='Sorteio criado com sucesso.')},
        examples=[
            OpenApiExample(
                'Criação de sorteio',
                value={
                    'referencia': 2700,
                    'data': '2026-06-09',
                    'numeros': [
                        0, 4, 7, 9, 13, 18, 21, 25, 30, 34,
                        39, 42, 47, 53, 61, 68, 72, 80, 91, 99
                    ],
                    'premios': [
                        {'pontos': 20, 'ganhadores': 1, 'valor': '1000000.00'},
                        {'pontos': 19, 'ganhadores': 5, 'valor': '25000.00'},
                        {'pontos': 18, 'ganhadores': 100, 'valor': '1500.00'}
                    ]
                },
                request_only=True
            )
        ]
    )
)
class SorteioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    """
    Consulta pública dos sorteios cadastrados (leitura, sem autenticação) e
    cadastro manual de um novo sorteio (autenticado). Não há edição nem
    remoção: um sorteio, uma vez registrado, é definitivo.
    """

    queryset = Sorteio.objects.prefetch_related('numeros', 'premios',).distinct()
    lookup_field = 'referencia'
    http_method_names = ['get', 'post', 'head', 'options']
    filterset_fields = {
        'referencia': ['exact'],
        'data': ['exact', 'lte', 'gte'],
        'numeros__valor': ['exact'],
        'premios__pontos': ['exact'],
        'premios__valor': ['gte']
    }
    ordering_fields = ['referencia', 'data']

    def get_serializer_class(self):

        match self.action:
            case 'create':
                return SorteioCreateSerializer
            case 'list':
                return SorteioDetalheModelSerializer if self._algum_filtro_aplicado() else SorteioListSerializer
            case _:
                return SorteioDetalheModelSerializer

    def _algum_filtro_aplicado(self):
        """Verifica se algum parâmetro de `filterset_fields` foi informado na query string da listagem."""

        campos_filtraveis = {
            campo if lookup == 'exact' else f'{campo}__{lookup}'
            for campo, lookups in self.filterset_fields.items()
            for lookup in lookups
        }

        return bool(set(self.request.query_params) & campos_filtraveis)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registrar_sorteio(serializer.validated_data)

        return Response({'detail': 'Sorteio criado com sucesso.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Retorna o sorteio de referência mais recente já cadastrado.',
        responses={200: SorteioDetalheModelSerializer}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='ultimo-sorteio'
    )
    def ultimo_sorteio(self, request):

        sorteio = self.get_queryset().order_by('-referencia').first()

        if sorteio is None:
            raise NotFound('Nenhum sorteio foi encontrado.')

        serializer = self.get_serializer(sorteio)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description=(
            'Retorna todos os sorteios já cadastrados com os detalhes completos (números '
            'sorteados e tabela de prêmios), ordenados da referência mais recente para a mais antiga.'
        ),
        responses={200: SorteioDetalheModelSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='detalhados'
    )
    def detalhados(self, request):

        sorteios = self.get_queryset().order_by('-referencia')

        serializer = self.get_serializer(sorteios, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
