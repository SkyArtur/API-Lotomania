"""
Testes HTTP de `ApostadorViewSet`: cadastro público (`create`), consulta do
próprio perfil (`perfil`), troca de senha (`senha`) e logout (`logout`),
sempre restritas ao apostador autenticado. Usa `APITestCase`/`APIClient`
(ciclo completo de URL → permissão → serializer → view), diferente de
`test_api_creates.py` e `test_api_services.py`, que chamam as funções de
`api.services` diretamente.
"""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Apostador


class ApostadorCreateTestCase(APITestCase):
    """Testes do cadastro público de apostadores (`POST /apostador/`)."""

    def test_create_publico_cadastra_apostador(self):
        """Testar se um cliente não autenticado consegue se cadastrar, e se a senha não vaza na resposta."""

        url = reverse('api:apostador-list')
        dados = {'username': 'novoapostador', 'password': 'S3nhaForte!23'}

        response = self.client.post(url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'novoapostador')
        self.assertNotIn('password', response.data)

        apostador = Apostador.objects.get(username='novoapostador')
        self.assertTrue(apostador.check_password('S3nhaForte!23'))

    def test_create_com_senha_fraca_retorna_400(self):
        """Testar se uma senha que não passa em `validate_password` (ex.: inteiramente numérica) é rejeitada."""

        url = reverse('api:apostador-list')
        dados = {'username': 'outroapostador', 'password': '12345678'}

        response = self.client.post(url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Apostador.objects.filter(username='outroapostador').exists())

    def test_create_com_username_invalido_retorna_400(self):
        """Testar se um username fora do padrão (`validar_username`: alfanumérico, 4-15 caracteres) é rejeitado."""

        url = reverse('api:apostador-list')
        dados = {'username': 'ab', 'password': 'S3nhaForte!23'}

        response = self.client.post(url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_nao_esta_disponivel(self):
        """
        Testar se não existe listagem de apostadores: GET na mesma rota do create retorna 405.

        Autentica antes de checar, pois `get_permissions` exige `IsAuthenticated` para qualquer
        ação diferente de `create` (inclusive um método sem handler, como este GET) — sem isso,
        a requisição seria barrada por 401 antes de chegar ao método não permitido.
        """

        self.client.force_authenticate(user=Apostador.objects.create_user(username='qualquerum', password='S3nhaForte!23'))
        url = reverse('api:apostador-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ApostadorPerfilTestCase(APITestCase):
    """Testes da action `perfil` (`GET /apostador/perfil/`)."""

    def setUp(self):
        """Cria um apostador autenticado, sem apostas nem prêmios."""
        self.apostador = Apostador.objects.create_user(username='perfilteste', password='S3nhaForte!23')

    def test_perfil_exige_autenticacao(self):
        """Testar se um cliente não autenticado não consegue acessar o próprio perfil."""

        url = reverse('api:apostador-perfil')

        response = self.client.get(url)

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_perfil_retorna_totais_zerados_para_apostador_sem_apostas(self):
        """Testar se o perfil do apostador autenticado retorna `total_apostado`/`total_premios` zerados."""

        self.client.force_authenticate(user=self.apostador)
        url = reverse('api:apostador-perfil')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'perfilteste')
        self.assertEqual(response.data['total_apostado'], Decimal('0.00'))
        self.assertEqual(response.data['total_premios'], Decimal('0.00'))


class ApostadorSenhaTestCase(APITestCase):
    """Testes da action `senha` (`PATCH /apostador/senha/`)."""

    def setUp(self):
        """Cria um apostador autenticado com senha conhecida."""
        self.apostador = Apostador.objects.create_user(username='senhateste', password='SenhaAntiga!12')
        self.client.force_authenticate(user=self.apostador)

    def test_senha_exige_autenticacao(self):
        """Testar se um cliente não autenticado não consegue trocar a senha de ninguém."""

        self.client.force_authenticate(user=None)
        url = reverse('api:apostador-senha')

        response = self.client.patch(
            url, {'senha_atual': 'SenhaAntiga!12', 'nova_senha': 'SenhaNova!34'}, format='json'
        )

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_senha_troca_com_sucesso(self):
        """Testar se, com a senha atual correta, a senha é trocada e devolve 204 sem corpo."""

        url = reverse('api:apostador-senha')

        response = self.client.patch(
            url, {'senha_atual': 'SenhaAntiga!12', 'nova_senha': 'SenhaNova!34'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        self.apostador.refresh_from_db()
        self.assertTrue(self.apostador.check_password('SenhaNova!34'))

    def test_senha_atual_incorreta_retorna_400_e_nao_altera_a_senha(self):
        """Testar se informar a senha atual errada rejeita a troca e mantém a senha original."""

        url = reverse('api:apostador-senha')

        response = self.client.patch(
            url, {'senha_atual': 'SenhaErrada!00', 'nova_senha': 'SenhaNova!34'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.apostador.refresh_from_db()
        self.assertTrue(self.apostador.check_password('SenhaAntiga!12'))

    def test_senha_igual_a_atual_retorna_400(self):
        """Testar se a validação de 'nova senha diferente da atual' também é aplicada via HTTP."""

        url = reverse('api:apostador-senha')

        response = self.client.patch(
            url, {'senha_atual': 'SenhaAntiga!12', 'nova_senha': 'SenhaAntiga!12'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ApostadorLogoutTestCase(APITestCase):
    """Testes da action `logout` (`POST /apostador/logout/`)."""

    def setUp(self):
        """Cria um apostador autenticado e um refresh token válido para ele."""
        self.apostador = Apostador.objects.create_user(username='logoutteste', password='S3nhaForte!23')
        self.refresh = RefreshToken.for_user(self.apostador)
        self.client.force_authenticate(user=self.apostador)

    def test_logout_exige_autenticacao(self):
        """Testar se um cliente não autenticado não consegue fazer logout de ninguém."""

        self.client.force_authenticate(user=None)
        url = reverse('api:apostador-logout')

        response = self.client.post(url, {'refresh': str(self.refresh)}, format='json')

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_logout_sem_refresh_retorna_400(self):
        """Testar se a ausência do campo `refresh` no corpo é rejeitada pelo serializer."""

        url = reverse('api:apostador-logout')

        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_com_refresh_invalido_retorna_400(self):
        """Testar se um refresh token malformado é rejeitado com 400, sem estourar erro 500."""

        url = reverse('api:apostador-logout')

        response = self.client.post(url, {'refresh': 'token-invalido'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_com_sucesso_invalida_o_refresh_token(self):
        """Testar se o logout retorna 205 sem corpo e o refresh token deixa de servir para renovar o access token."""

        url = reverse('api:apostador-logout')

        response = self.client.post(url, {'refresh': str(self.refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertFalse(response.data)

        response_refresh = self.client.post(reverse('token_refresh'), {'refresh': str(self.refresh)}, format='json')

        self.assertEqual(response_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_repetido_com_o_mesmo_token_retorna_400(self):
        """Testar se um segundo logout com um refresh token já na blacklist é rejeitado com 400, não 500."""

        url = reverse('api:apostador-logout')
        self.client.post(url, {'refresh': str(self.refresh)}, format='json')

        response = self.client.post(url, {'refresh': str(self.refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
