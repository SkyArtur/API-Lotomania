from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from core.models import Bet
from api.serializers import BetDetailSerializer, BetListSerializer, BetCreateSerializer, BetNumbersListSerializer
from api.services import post_bet


__all__ = ['BetViewSet']


@extend_schema_view(
    list=extend_schema(
        description='Retorna uma lista resumida das apostas cadastradas.',
        responses={200: BetListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        description='Retorna os detalhes de uma aposta específica.',
        responses={200: BetDetailSerializer}
    ),
    create=extend_schema(
        description='Cria uma nova aposta da Lotomania.',
        request=BetCreateSerializer,
        responses={201: BetCreateSerializer},
        examples=[
            OpenApiExample(
                'Criação de aposta',
                value={
                    'date': '2026-06-09',
                    'value': '5.00',
                    'initial': 2700,
                    'final': 2710,
                    'mirror': True,
                    'numbers': [
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
        description='Remove uma aposta cadastrada.'
    )
)
class BetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Bet.objects.prefetch_related('numbers', 'contests', 'prizes', 'results')
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return BetListSerializer
            case 'create':
                return BetCreateSerializer
            case 'numbers':
                return BetNumbersListSerializer
            case _:
                return BetDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_bet(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Retorna a última aposta registrada.',
        responses={200: BetDetailSerializer}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='latest'
    )
    def latest(self, request):
        bet = self.get_queryset().order_by('-date').first()

        if bet is None:
            raise NotFound('Nenhuma aposta foi encontrada.')

        serializer = self.get_serializer(bet)
        return Response(serializer.data)

    @extend_schema(
        description='Retorna uma lista de apostas detalhadas.',
        responses={200: BetDetailSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='all'
    )
    def all(self, request):
        contests = self.get_queryset()

        if contests is None:
            raise NotFound('Nenhum concurso foi encontrado.')

        serializer = self.get_serializer(contests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Retorna uma lista com os números apostados.',
        responses={200: BetNumbersListSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='numbers'
    )
    def numbers(self, request):
        bets = self.get_queryset().order_by('-date')
        serializer = self.get_serializer(bets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
