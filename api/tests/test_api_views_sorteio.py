"""
Testes HTTP de `SorteioViewSet`: leitura pública (`list`, `retrieve`,
`ultimo-sorteio`, `detalhados`) e cadastro restrito a apostadores
autenticados (`create`). Usa `APITestCase`/`APIClient`. O banco de testes já
vem populado pelas migrações de seed (0002/0003) com os ~2947 sorteios
históricos reais, por isso os testes de leitura não partem de uma tabela
vazia.
"""

from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Apostador, Sorteio

REFERENCIA_FALSA = 999999


class SorteioLeituraTestCase(APITestCase):
    """Testes de `list`/`retrieve`/`ultimo-sorteio`/`detalhados`, todos públicos."""

    def test_list_e_publico(self):
        """Testar se a listagem de sorteios não exige autenticação."""

        response = self.client.get(reverse('api:sorteios-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_e_publico(self):
        """Testar se o detalhe de um sorteio existente (referência 1, do seed) é acessível sem autenticação."""

        url = reverse('api:sorteios-detail', kwargs={'referencia': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['numeros']), 20)

    def test_ultimo_sorteio_retorna_o_de_maior_referencia(self):
        """Testar se `ultimo-sorteio` retorna o sorteio de maior referência, mesmo entre os dados de seed."""

        sorteio_novo = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))
        sorteio_novo.numeros.set(Sorteio.objects.first().numeros.model.objects.filter(valor__lt=20))

        response = self.client.get(reverse('api:sorteios-ultimo-sorteio'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['referencia'], REFERENCIA_FALSA)

    def test_detalhados_inclui_sorteios_recem_criados(self):
        """Testar se `detalhados` retorna a lista completa (com números e prêmios), incluindo um sorteio novo."""

        sorteio_novo = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))
        sorteio_novo.numeros.set(Sorteio.objects.first().numeros.model.objects.filter(valor__lt=20))

        response = self.client.get(reverse('api:sorteios-detalhados'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        referencias_retornadas = [item['referencia'] for item in response.data]
        self.assertIn(REFERENCIA_FALSA, referencias_retornadas)


class SorteioCreateTestCase(APITestCase):
    """Testes do cadastro manual de sorteios (`POST /sorteios/`)."""

    def setUp(self):
        self.apostador = Apostador.objects.create_user(username='criadorteste', password='S3nhaForte!23')
        self.numeros_validos = list(range(20))

    def payload_valido(self, referencia=REFERENCIA_FALSA):
        return {
            'referencia': referencia,
            'data': '2026-01-01',
            'numeros': self.numeros_validos,
            'premios': [
                {'pontos': 20, 'ganhadores': 1, 'valor': '1000000.00'},
                {'pontos': 0, 'ganhadores': 50, 'valor': '500.00'},
            ],
        }

    def test_create_exige_autenticacao(self):
        """Testar se um cliente não autenticado não consegue cadastrar sorteios (leitura pública, escrita não)."""

        response = self.client.post(reverse('api:sorteios-list'), self.payload_valido(), format='json')

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.assertFalse(Sorteio.objects.filter(referencia=REFERENCIA_FALSA).exists())

    def test_create_cadastra_sorteio_com_numeros_e_premios(self):
        """Testar se um apostador autenticado consegue cadastrar um sorteio válido."""

        self.client.force_authenticate(user=self.apostador)

        response = self.client.post(reverse('api:sorteios-list'), self.payload_valido(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        sorteio = Sorteio.objects.get(referencia=REFERENCIA_FALSA)
        self.assertEqual(sorteio.numeros.count(), 20)
        self.assertEqual(sorteio.premios.count(), 2)

    def test_create_com_referencia_ja_cadastrada_retorna_400(self):
        """Testar se cadastrar uma referência já existente (ex.: a do seed) é rejeitado."""

        self.client.force_authenticate(user=self.apostador)

        response = self.client.post(reverse('api:sorteios-list'), self.payload_valido(referencia=1), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_com_quantidade_de_numeros_invalida_retorna_400(self):
        """Testar se um sorteio com menos de 20 números é rejeitado."""

        self.client.force_authenticate(user=self.apostador)

        dados = self.payload_valido()
        dados['numeros'] = self.numeros_validos[:19]

        response = self.client.post(reverse('api:sorteios-list'), dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Sorteio.objects.filter(referencia=REFERENCIA_FALSA).exists())

    def test_create_com_pontuacao_de_premio_invalida_retorna_400(self):
        """Testar se uma faixa de pontos fora de {0, 15-20} é rejeitada."""

        self.client.force_authenticate(user=self.apostador)

        dados = self.payload_valido()
        dados['premios'] = [{'pontos': 10, 'ganhadores': 1, 'valor': '10.00'}]

        response = self.client.post(reverse('api:sorteios-list'), dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
