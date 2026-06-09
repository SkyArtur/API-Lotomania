from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view, inline_serializer

from core.models import Contest
from api.services import post_contest
from api.serializers import (
    ContestDetailModelSerializer,
    ContestListSerializer,
    ContestCreateSerializer,
    ContestNumbersListSerializer
)


__all__ = ['ContestViewSet']


@extend_schema_view(
    list=extend_schema(
        description='Retorna uma lista resumida dos concursos cadastrados.',
        responses={200: ContestListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        description='Retorna os detalhes de um concurso específico.',
        responses={200: ContestDetailModelSerializer}
    ),
    create=extend_schema(
        description='Cria um novo concurso da Lotomania.',
        request=ContestCreateSerializer,
        responses={
            201: inline_serializer(
                name='ContestCreateResponseSerializer',
                fields={
                    'detail': serializers.CharField()
                }
            )
        },
        examples=[
            OpenApiExample(
                'Criação de concurso',
                value={
                    'reference': 2700,
                    'date': '2026-06-09',
                    'numbers': [
                        0, 4, 7, 9, 13, 18, 21, 25, 30, 34,
                        39, 42, 47, 53, 61, 68, 72, 80, 91, 99
                    ],
                    'prizes': [
                        {'points': 20, 'winners': 1, 'value': '1000000.00'},
                        {'points': 19, 'winners': 5, 'value': '25000.00'},
                        {'points': 18, 'winners': 100, 'value': '1500.00'}
                    ]
                },
                request_only=True
            )
        ]
    )
)
class ContestViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):

    queryset = Contest.objects.prefetch_related('numbers', 'prizes',)
    lookup_field = 'reference'
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return ContestCreateSerializer
            case 'list':
                return ContestListSerializer
            case 'numbers':
                return ContestNumbersListSerializer
            case _:
                return ContestDetailModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_contest(serializer.validated_data)

        return Response({'detail': 'Contest created successfully.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Retorna o último concurso registrado.',
        responses={200: ContestDetailModelSerializer}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='latest'
    )
    def latest(self, request):
        contest = self.get_queryset().order_by('-reference').first()

        if contest is None:
            raise NotFound('Nenhum concurso foi encontrado.')

        serializer = self.get_serializer(contest)
        return Response(serializer.data)

    @extend_schema(
        description='Retorna uma lista de concursos detalhados.',
        responses={200: ContestDetailModelSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='all'
    )
    def all(self, request):
        contests = self.get_queryset().order_by('-reference')

        if contests is None:
            raise NotFound('Nenhum concurso foi encontrado.')

        serializer = self.get_serializer(contests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Retorna uma lista com os números dos concursos.',
        responses={200: ContestNumbersListSerializer(many=True)}
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='numbers'
    )
    def numbers(self, request):
        contests = self.get_queryset().order_by('-reference')
        serializer = self.get_serializer(contests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
