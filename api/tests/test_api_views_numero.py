"""
Testes HTTP de `NumeroViewSet`: consulta pública, somente leitura, dos 100
números válidos (0-99) e suas estatísticas. Usa `APITestCase`/`APIClient`.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Apostador


class NumeroListTestCase(APITestCase):
    """Testes da listagem de números (`GET /numeros/`)."""

    def test_list_e_publico_e_retorna_os_100_numeros(self):
        """Testar se a listagem não exige autenticação e traz os 100 números válidos (seed da migração 0002)."""

        response = self.client.get(reverse('api:numeros-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        total = response.data['count'] if 'count' in response.data else len(response.data)
        self.assertEqual(total, 100)

    def test_list_traz_as_estatisticas_de_cada_numero(self):
        """Testar se cada número vem com `valor`, `vezes_sorteado` e `vezes_apostado`."""

        response = self.client.get(reverse('api:numeros-list'))

        resultados = response.data['results'] if 'results' in response.data else response.data
        numero = resultados[0]

        self.assertIn('valor', numero)
        self.assertIsInstance(numero['vezes_sorteado'], int)
        self.assertIsInstance(numero['vezes_apostado'], int)

    def test_create_nao_e_permitido(self):
        """
        Testar se não existe cadastro de números: POST na listagem retorna 405, mesmo autenticado.

        Autentica antes de checar: sem isso, a escrita já seria barrada por `IsAuthenticatedOrReadOnly`
        (401), antes de chegar à ausência de handler para POST (405).
        """

        self.client.force_authenticate(user=Apostador.objects.create_user(username='qualquerum', password='S3nhaForte!23'))

        response = self.client.post(reverse('api:numeros-list'), {'valor': 5}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detalhe_de_numero_nao_existe(self):
        """Testar se não há rota de detalhe (`retrieve`) para números: a URL nem chega a resolver."""

        url = reverse('api:numeros-list') + '5/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
