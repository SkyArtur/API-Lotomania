from rest_framework import status
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import Number
from api.serializers import NumberSerializer


@extend_schema_view(
    list=extend_schema(
        description='Retorna os números disponíveis para apostas e concursos.',
        responses={200: NumberSerializer(many=True)}
    )
)
class NumberViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Number.objects.all()
    serializer_class = NumberSerializer
    lookup_field = 'value'
    http_method_names = ['get', 'head', 'options']

    @extend_schema(
        description='Retorna uma lista simples de números de 0 a 99.',
        responses={200: list[int]}
    )
    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        numbers = self.get_queryset()
        serializer = self.get_serializer(numbers, many=True)
        return Response([i['value'] for i in serializer.data], status=status.HTTP_200_OK)
