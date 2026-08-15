from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from core.models import Apostador
from api.serializers import (
    ApostadorSerializer,
    ApostadorRegistroSerializer,
    ApostadorPerfilSerializer,
    ApostadorAlterarSenhaSerializer,
    ApostadorLogoutSerializer
)


__all__ = ['ApostadorViewSet']


@extend_schema_view(
    create=extend_schema(
        description=(
            'Cadastra um novo apostador. Endpoint público (não exige autenticação). '
            'O `username` deve ser alfanumérico, entre 4 e 15 caracteres, e a senha '
            'passa pelas validações padrão do Django (tamanho mínimo, não ser inteiramente '
            'numérica, entre outras).'
        ),
        request=ApostadorRegistroSerializer,
        responses={201: ApostadorSerializer},
    ),
)
class ApostadorViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Cadastro de apostadores (`create`, público) e consulta do próprio perfil
    (`perfil`, autenticado). Não expõe listagem nem detalhe de outros
    apostadores.
    """

    queryset = Apostador.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_serializer_class(self):

        match self.action:
            case 'create':
                return ApostadorRegistroSerializer
            case 'senha':
                return ApostadorAlterarSenhaSerializer
            case 'perfil':
                return ApostadorPerfilSerializer
            case 'logout':
                return ApostadorLogoutSerializer

        return ApostadorSerializer

    def get_permissions(self):

        if self.action == 'create':
            return [AllowAny()]

        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apostador = serializer.save()
        saida_serializer = ApostadorSerializer(apostador)

        return Response(saida_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description=(
                'Permite ao apostador autenticado, atualizar a sua senha. '
                'Este método não visa a atualização em caso de esquecimento.'
        ),
        request=ApostadorAlterarSenhaSerializer,
        responses={204: None}
    )
    @action(detail=False, methods=['patch'], url_path='senha')
    def senha(self, request):

        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description=(
            'Retorna o perfil do apostador autenticado, incluindo o total apostado e o total '
            'já recebido em prêmios.'
        ),
        responses={200: ApostadorPerfilSerializer}
    )
    @action(detail=False, methods=['get'], url_path='perfil')
    def perfil(self, request):

        serializer = self.get_serializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description=(
            'Invalida (blacklist) o refresh token informado, encerrando a sessão do apostador '
            'autenticado. O access token em uso continua válido até expirar por conta própria '
            '(ver `ACCESS_TOKEN_LIFETIME`); esta ação apenas impede que esse refresh token gere '
            'novos access/refresh tokens no futuro.'
        ),
        request=ApostadorLogoutSerializer,
        responses={205: OpenApiResponse(description='Logout realizado com sucesso.')}
    )
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_205_RESET_CONTENT)
