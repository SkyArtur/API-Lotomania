from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Bet
from api.serializers import BetDetailSerializer, BetListSerializer, BetCreateSerializer, BetNumbersListSerializer
from api.services import post_bet


__all__ = ['BetViewSet']


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

    @action(detail=False, methods=['get'], url_path='latest')
    def latest(self, request):
        bet = self.get_queryset().order_by('-date').first()

        if bet is None:
            raise NotFound('Nenhuma aposta foi encontrada.')

        serializer = self.get_serializer(bet)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request):
        contests = self.get_queryset()

        if contests is None:
            raise NotFound('Nenhum concurso foi encontrado.')

        serializer = self.get_serializer(contests, many=True)
        return Response(serializer, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='numbers')
    def numbers(self, request):
        bets = self.get_queryset().order_by('-date')
        serializer = self.get_serializer(bets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)