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

from core.models import Apostador, Sorteio, SorteioPremio, Numero

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


class SorteioFiltrosTestCase(APITestCase):
    """
    Testes de `filterset_fields`/`ordering_fields` de `SorteioViewSet` (`GET /sorteios/`), sempre públicos.
    Usa referências e datas bem fora da faixa dos dados de seed (0002/0003), para isolar os sorteios de
    teste dos ~2947 sorteios históricos reais já cadastrados.
    """

    REFERENCIA_1 = 9000001
    REFERENCIA_2 = 9000002

    def setUp(self):
        self.sorteio_antigo = Sorteio.objects.create(referencia=self.REFERENCIA_1, data=date(2030, 1, 1))
        self.sorteio_antigo.numeros.set(Numero.objects.filter(valor__lt=20))

        self.sorteio_novo = Sorteio.objects.create(referencia=self.REFERENCIA_2, data=date(2030, 6, 1))
        self.sorteio_novo.numeros.set(Numero.objects.filter(valor__gte=20, valor__lt=40))

    def referencias_retornadas(self, response):
        """Extrai as `referencia` retornadas na listagem, já considerando a paginação."""

        resultados = response.data['results'] if 'results' in response.data else response.data
        return [item['referencia'] for item in resultados]

    def test_filtrar_por_referencia(self):
        """Testar se `?referencia=` retorna apenas o sorteio daquela referência exata."""

        response = self.client.get(reverse('api:sorteios-list'), {'referencia': self.REFERENCIA_1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        referencias = self.referencias_retornadas(response)
        self.assertIn(self.REFERENCIA_1, referencias)
        self.assertNotIn(self.REFERENCIA_2, referencias)

    def test_filtrar_por_data_gte(self):
        """Testar se `?data__gte=` restringe a listagem a sorteios a partir da data informada."""

        response = self.client.get(reverse('api:sorteios-list'), {'data__gte': '2030-03-01'})

        referencias = self.referencias_retornadas(response)
        self.assertIn(self.REFERENCIA_2, referencias)
        self.assertNotIn(self.REFERENCIA_1, referencias)

    def test_filtrar_por_numeros_valor(self):
        """Testar se `?numeros__valor=` retorna apenas os sorteios em que aquele número saiu."""

        response = self.client.get(reverse('api:sorteios-list'), {'numeros__valor': 5})

        referencias = self.referencias_retornadas(response)
        self.assertIn(self.REFERENCIA_1, referencias)
        self.assertNotIn(self.REFERENCIA_2, referencias)

    def test_filtrar_por_premios_pontos(self):
        """Testar se `?premios__pontos=` retorna apenas os sorteios com uma faixa de prêmio específica."""

        SorteioPremio.objects.create(sorteio=self.sorteio_novo, pontos=20, ganhadores=1, valor='1000000.00')

        response = self.client.get(reverse('api:sorteios-list'), {'premios__pontos': 20})

        referencias = self.referencias_retornadas(response)
        self.assertIn(self.REFERENCIA_2, referencias)
        self.assertNotIn(self.REFERENCIA_1, referencias)

    def test_filtrar_por_premios_valor_gte_nao_duplica_sorteio(self):
        """
        Testar se `?premios__valor__gte=` retorna o sorteio uma única vez mesmo com mais de uma faixa de
        prêmio acima do valor informado — confirma que o `.distinct()` do queryset evita duplicação.
        """

        SorteioPremio.objects.create(sorteio=self.sorteio_novo, pontos=20, ganhadores=1, valor='1000000.00')
        SorteioPremio.objects.create(sorteio=self.sorteio_novo, pontos=19, ganhadores=5, valor='25000.00')

        response = self.client.get(reverse('api:sorteios-list'), {'premios__valor__gte': '10000.00'})

        referencias = self.referencias_retornadas(response)
        self.assertEqual(referencias.count(self.REFERENCIA_2), 1)

    def test_ordenar_por_referencia_crescente(self):
        """
        Testar se `?ordering=referencia` ordena da referência menor para a maior, combinando com o filtro
        de data para isolar apenas os sorteios de teste em meio aos dados de seed.
        """

        response = self.client.get(
            reverse('api:sorteios-list'), {'ordering': 'referencia', 'data__gte': '2029-01-01'}
        )

        referencias = self.referencias_retornadas(response)
        self.assertEqual(referencias, [self.REFERENCIA_1, self.REFERENCIA_2])

    def test_ordenar_por_data_decrescente(self):
        """Testar se `?ordering=-data` ordena da data mais recente para a mais antiga (mesmo isolamento)."""

        response = self.client.get(
            reverse('api:sorteios-list'), {'ordering': '-data', 'data__gte': '2029-01-01'}
        )

        referencias = self.referencias_retornadas(response)
        self.assertEqual(referencias, [self.REFERENCIA_2, self.REFERENCIA_1])
