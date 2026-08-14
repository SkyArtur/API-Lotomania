from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_view,
    OpenApiResponse
)

from core.models import Aposta
from api.services import registrar_aposta
from api.serializers import (
    ApostaDetalheSerializer,
    ApostaListSerializer,
    ApostaCreateSerializer
)


__all__ = ['ApostaViewSet']


@extend_schema_view(
    list=extend_schema(
        description=(
            'Retorna uma lista resumida das apostas do apostador autenticado, sem os números, '
            'resultados ou prêmios de cada uma.'
        ),
        responses={200: ApostaListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        description=(
            'Retorna os detalhes completos de uma aposta específica do apostador autenticado, '
            'incluindo números escolhidos, sorteios já conferidos, acertos e prêmios.'
        ),
        responses={200: ApostaDetalheSerializer}
    ),
    create=extend_schema(
        description=(
            'Cria uma nova aposta da Lotomania para o apostador autenticado. A aposta exige '
            'exatamente 50 números distintos entre 0 e 99 e um intervalo de concursos válidos '
            '(`inicial`/`final`, com `inicial` menor ou igual a `final`). Quando `espelho` é '
            'verdadeiro, os acertos também são conferidos considerando o espelho dos números sorteados.'
        ),
        request=ApostaCreateSerializer,
        responses={201: OpenApiResponse(description='Aposta criada com sucesso.')},
        examples=[
            OpenApiExample(
                'Criação de aposta',
                value={
                    'data': '2026-06-09',
                    'valor': '5.00',
                    'inicial': 2700,
                    'final': 2710,
                    'espelho': True,
                    'numeros': [
                        0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                        10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                        20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                        30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
                        40, 41, 42, 43, 44, 45, 46, 47, 48, 49
                    ]
                },
                request_only=True
            )
        ]
    ),
    destroy=extend_schema(
        description='Remove uma aposta do apostador autenticado. A exclusão é definitiva.'
    )
)
class ApostaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    """
    CRUD (sem edição) das apostas do apostador autenticado. Todas as ações
    são restritas às apostas de quem fez a requisição — `get_queryset` já
    filtra pelo usuário autenticado, então nunca é possível ver ou remover a
    aposta de outra pessoa.
    """

    queryset = Aposta.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated,]
    filterset_fields = {
        'data': ['exact', 'lte', 'gte'],
        'valor': ['exact', 'lte', 'gte'],
        'inicial': ['gte'],
        'final': ['lte'],
        'espelho': ['exact'],
        'sorteios__referencia': ['exact'],
        'resultados__acertos': ['gte'],
        'premios__valor': ['exact', 'gte'],
    }
    ordering_fields = ['data', 'valor', 'inicial', 'final']

    def get_queryset(self):

        return (
            Aposta.objects.filter(apostador=self.request.user)
            .prefetch_related('sorteios', 'numeros', 'premios')
            .distinct()
        )

    def get_serializer_class(self):

        match self.action:
            case 'list':
                return ApostaListSerializer
            case 'create':
                return ApostaCreateSerializer
            case _:
                return ApostaDetalheSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registrar_aposta(request, serializer.validated_data)

        return Response({'detail': 'Aposta registrada com sucesso.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Retorna a aposta mais recente (por data) do apostador autenticado.',
        responses={200: ApostaDetalheSerializer}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='ultima-aposta'
    )
    def ultima_aposta(self, request):

        aposta = self.get_queryset().order_by('-data').first()

        if aposta is None:
            raise NotFound('Nenhuma aposta foi encontrada.')

        serializer = self.get_serializer(aposta)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description=(
            'Retorna todas as apostas do apostador autenticado já com os detalhes completos '
            '(números, sorteios conferidos, acertos e prêmios), evitando uma chamada por aposta.'
        ),
        responses={200: ApostaDetalheSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='detalhadas'
    )
    def detalhadas(self, request):

        apostas = self.get_queryset()

        serializer = self.get_serializer(apostas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
