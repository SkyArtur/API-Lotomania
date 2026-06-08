from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Number
from api.serializers import NumberSerializer


class NumberViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Number.objects.all()
    serializer_class = NumberSerializer
    lookup_field = 'value'
    http_method_names = ['get', 'head', 'options']


    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        numbers = self.get_queryset()
        serializer = self.get_serializer(numbers, many=True)
        return Response([i['value'] for i in serializer.data], status=status.HTTP_200_OK)
