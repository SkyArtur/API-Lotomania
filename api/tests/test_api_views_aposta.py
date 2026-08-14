"""
Testes HTTP de `ApostaViewSet`: todas as ações exigem um apostador autenticado
e ficam restritas às apostas de quem fez a requisição (`get_queryset` filtra
por `apostador=request.user`). Usa `APITestCase`/`APIClient`, exercitando o
ciclo completo de URL → permissão → serializer → view → `api.services`.
"""

from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Apostador, Aposta, Numero, Sorteio, ApostaPremio, ApostaResultado


class ApostaViewSetTestCaseBase(APITestCase):
    """Base comum: dois apostadores autenticáveis e uma lista de números válidos."""

    def setUp(self):
        """Cria dois apostadores e deixa `self.numeros_validos` pronto para montar apostas."""

        self.apostador = Apostador.objects.create_user(username='apostador1', password='S3nhaForte!23')
        self.outro_apostador = Apostador.objects.create_user(username='apostador2', password='S3nhaForte!23')
        self.numeros_validos = list(range(50))

    def criar_aposta(self, apostador, data=date(2024, 1, 10), inicial=2700, final=2710, valor='5.00', espelho=True):
        """Cria uma `Aposta` diretamente no banco, sem passar pelo endpoint, para os testes de leitura/remoção."""

        aposta = Aposta.objects.create(
            apostador=apostador, data=data, valor=valor, inicial=inicial, final=final, espelho=espelho
        )
        aposta.numeros.set(Numero.objects.filter(valor__in=self.numeros_validos))

        return aposta


class ApostaPermissaoTestCase(ApostaViewSetTestCaseBase):
    """Testes de que nenhuma ação de `ApostaViewSet` está disponível sem autenticação."""

    def test_list_exige_autenticacao(self):
        """Testar se listar apostas sem autenticação é negado."""

        response = self.client.get(reverse('api:apostas-list'))

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_exige_autenticacao(self):
        """Testar se criar uma aposta sem autenticação é negado."""

        response = self.client.post(reverse('api:apostas-list'), {}, format='json')

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class ApostaListRetrieveTestCase(ApostaViewSetTestCaseBase):
    """Testes de `list`/`retrieve`, garantindo que cada apostador só enxerga as próprias apostas."""

    def setUp(self):
        super().setUp()
        self.minha_aposta = self.criar_aposta(self.apostador)
        self.aposta_de_outro = self.criar_aposta(self.outro_apostador)
        self.client.force_authenticate(user=self.apostador)

    def test_list_retorna_apenas_as_apostas_do_apostador_autenticado(self):
        """Testar se a listagem não vaza apostas de outros apostadores."""

        response = self.client.get(reverse('api:apostas-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resultados = response.data['results'] if 'results' in response.data else response.data
        ids_retornados = [item['id'] for item in resultados]

        self.assertIn(self.minha_aposta.id, ids_retornados)
        self.assertNotIn(self.aposta_de_outro.id, ids_retornados)

    def test_retrieve_da_propria_aposta(self):
        """Testar se o detalhe da própria aposta retorna números, sorteios e prêmios."""

        url = reverse('api:apostas-detail', kwargs={'id': self.minha_aposta.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['numeros']), 50)

    def test_retrieve_de_aposta_de_outro_apostador_retorna_404(self):
        """Testar se tentar acessar a aposta de outra pessoa retorna 404, não 403 (não revela nem a existência)."""

        url = reverse('api:apostas-detail', kwargs={'id': self.aposta_de_outro.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApostaCreateTestCase(ApostaViewSetTestCaseBase):
    """Testes da criação de apostas (`POST /apostas/`)."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.apostador)

    def test_create_registra_aposta_do_apostador_autenticado(self):
        """Testar se uma aposta válida é criada e vinculada ao apostador autenticado."""

        dados = {
            'data': '2024-05-20',
            'valor': '5.00',
            'inicial': 2700,
            'final': 2710,
            'espelho': True,
            'numeros': self.numeros_validos,
        }

        response = self.client.post(reverse('api:apostas-list'), dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        aposta = Aposta.objects.get(apostador=self.apostador)
        self.assertEqual(aposta.numeros.count(), 50)

    def test_create_com_quantidade_de_numeros_invalida_retorna_400(self):
        """Testar se uma aposta com menos de 50 números é rejeitada e nada é criado."""

        dados = {
            'data': '2024-05-20',
            'valor': '5.00',
            'inicial': 2700,
            'final': 2710,
            'espelho': True,
            'numeros': self.numeros_validos[:49],
        }

        response = self.client.post(reverse('api:apostas-list'), dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Aposta.objects.filter(apostador=self.apostador).exists())

    def test_create_com_intervalo_invertido_retorna_400(self):
        """Testar se `inicial` maior que `final` é rejeitado pela validação do serializer."""

        dados = {
            'data': '2024-05-20',
            'valor': '5.00',
            'inicial': 2710,
            'final': 2700,
            'espelho': True,
            'numeros': self.numeros_validos,
        }

        response = self.client.post(reverse('api:apostas-list'), dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ApostaActionsTestCase(ApostaViewSetTestCaseBase):
    """Testes das actions `ultima-aposta` e `detalhadas`."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.apostador)

    def test_ultima_aposta_sem_apostas_retorna_404(self):
        """Testar se, sem nenhuma aposta registrada, a action retorna 404 em vez de uma lista vazia."""

        response = self.client.get(reverse('api:apostas-ultima-aposta'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ultima_aposta_retorna_a_mais_recente_por_data(self):
        """Testar se, com mais de uma aposta, a action retorna a de data mais recente."""

        aposta_antiga = self.criar_aposta(self.apostador, data=date(2023, 1, 1))
        aposta_recente = self.criar_aposta(self.apostador, data=date(2024, 6, 1))

        response = self.client.get(reverse('api:apostas-ultima-aposta'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], aposta_recente.id)
        self.assertNotEqual(response.data['id'], aposta_antiga.id)

    def test_detalhadas_retorna_todas_as_apostas_do_apostador(self):
        """Testar se a action `detalhadas` retorna todas as apostas do apostador, já com números e prêmios."""

        self.criar_aposta(self.apostador, data=date(2023, 1, 1))
        self.criar_aposta(self.apostador, data=date(2024, 6, 1))
        self.criar_aposta(self.outro_apostador)

        response = self.client.get(reverse('api:apostas-detalhadas'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class ApostaDestroyTestCase(ApostaViewSetTestCaseBase):
    """Testes da remoção de apostas (`DELETE /apostas/<id>/`)."""

    def setUp(self):
        super().setUp()
        self.minha_aposta = self.criar_aposta(self.apostador)
        self.aposta_de_outro = self.criar_aposta(self.outro_apostador)
        self.client.force_authenticate(user=self.apostador)

    def test_destroy_remove_a_propria_aposta(self):
        """Testar se o apostador consegue remover a própria aposta."""

        url = reverse('api:apostas-detail', kwargs={'id': self.minha_aposta.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Aposta.objects.filter(id=self.minha_aposta.id).exists())

    def test_destroy_de_aposta_de_outro_apostador_retorna_404_e_nao_remove(self):
        """Testar se não é possível remover a aposta de outra pessoa."""

        url = reverse('api:apostas-detail', kwargs={'id': self.aposta_de_outro.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Aposta.objects.filter(id=self.aposta_de_outro.id).exists())


class ApostaFiltrosTestCase(ApostaViewSetTestCaseBase):
    """
    Testes de `filterset_fields`/`ordering_fields` de `ApostaViewSet` (`GET /apostas/`), sempre restritos às
    apostas do apostador autenticado (mesma regra de `get_queryset`).
    """

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.apostador)

        self.aposta_barata = self.criar_aposta(
            self.apostador, data=date(2024, 1, 10), inicial=2700, final=2705, valor='5.00', espelho=False
        )
        self.aposta_cara = self.criar_aposta(
            self.apostador, data=date(2024, 6, 20), inicial=2720, final=2730, valor='50.00', espelho=True
        )

    def ids_retornados(self, response):
        """Extrai os `id` retornados na listagem, já considerando a paginação."""

        resultados = response.data['results'] if 'results' in response.data else response.data
        return [item['id'] for item in resultados]

    def test_filtrar_por_data_exact(self):
        """Testar se `?data=` retorna apenas a aposta com aquela data exata."""

        response = self.client.get(reverse('api:apostas-list'), {'data': '2024-01-10'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_barata.id, ids)
        self.assertNotIn(self.aposta_cara.id, ids)

    def test_filtrar_por_data_gte(self):
        """Testar se `?data__gte=` restringe a listagem a apostas a partir da data informada."""

        response = self.client.get(reverse('api:apostas-list'), {'data__gte': '2024-05-01'})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_cara.id, ids)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_filtrar_por_valor_gte(self):
        """Testar se `?valor__gte=` retorna apenas as apostas de valor igual ou maior ao informado."""

        response = self.client.get(reverse('api:apostas-list'), {'valor__gte': '10.00'})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_cara.id, ids)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_filtrar_por_inicial_gte(self):
        """Testar se `?inicial__gte=` exclui apostas cujo concurso inicial é anterior ao informado."""

        response = self.client.get(reverse('api:apostas-list'), {'inicial__gte': '2710'})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_cara.id, ids)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_filtrar_por_final_lte(self):
        """Testar se `?final__lte=` exclui apostas cujo concurso final é posterior ao informado."""

        response = self.client.get(reverse('api:apostas-list'), {'final__lte': '2710'})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_barata.id, ids)
        self.assertNotIn(self.aposta_cara.id, ids)

    def test_filtrar_por_espelho(self):
        """Testar se `?espelho=` filtra apostas pelo campo booleano `espelho`."""

        response = self.client.get(reverse('api:apostas-list'), {'espelho': 'false'})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_barata.id, ids)
        self.assertNotIn(self.aposta_cara.id, ids)

    def test_filtrar_por_sorteios_referencia(self):
        """Testar se `?sorteios__referencia=` retorna apenas a aposta que já conferiu aquele sorteio."""

        sorteio = Sorteio.objects.first()
        self.aposta_cara.sorteios.add(sorteio)

        response = self.client.get(reverse('api:apostas-list'), {'sorteios__referencia': sorteio.referencia})

        ids = self.ids_retornados(response)
        self.assertIn(self.aposta_cara.id, ids)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_filtrar_por_resultados_acertos_gte_nao_duplica_aposta(self):
        """
        Testar se `?resultados__acertos__gte=` retorna a aposta uma única vez mesmo quando ela tem mais de
        um resultado (contra sorteios diferentes) acima do valor informado — confirma que o `.distinct()`
        do queryset evita duplicação por causa do JOIN na relação reversa `resultados`.
        """

        sorteio_1, sorteio_2 = Sorteio.objects.all()[:2]
        ApostaResultado.objects.create(aposta=self.aposta_cara, sorteio=sorteio_1, acertos=20, acertos_espelhados=20)
        ApostaResultado.objects.create(aposta=self.aposta_cara, sorteio=sorteio_2, acertos=18, acertos_espelhados=18)

        response = self.client.get(reverse('api:apostas-list'), {'resultados__acertos__gte': '15'})

        ids = self.ids_retornados(response)
        self.assertEqual(ids.count(self.aposta_cara.id), 1)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_filtrar_por_premios_valor_gte_nao_duplica_aposta(self):
        """
        Testar se `?premios__valor__gte=` retorna a aposta uma única vez mesmo com mais de um prêmio acima
        do valor informado — confirma o `.distinct()` do queryset.
        """

        sorteio_1, sorteio_2 = Sorteio.objects.all()[:2]
        ApostaPremio.objects.create(aposta=self.aposta_cara, sorteio=sorteio_1, pontos=20, valor='1000.00')
        ApostaPremio.objects.create(aposta=self.aposta_cara, sorteio=sorteio_2, pontos=19, valor='500.00')

        response = self.client.get(reverse('api:apostas-list'), {'premios__valor__gte': '100.00'})

        ids = self.ids_retornados(response)
        self.assertEqual(ids.count(self.aposta_cara.id), 1)
        self.assertNotIn(self.aposta_barata.id, ids)

    def test_ordenar_por_valor_decrescente(self):
        """Testar se `?ordering=-valor` ordena a listagem da aposta de maior para a de menor valor."""

        response = self.client.get(reverse('api:apostas-list'), {'ordering': '-valor'})

        ids = self.ids_retornados(response)
        self.assertEqual(ids[:2], [self.aposta_cara.id, self.aposta_barata.id])

    def test_ordenar_por_data_crescente(self):
        """Testar se `?ordering=data` ordena a listagem da aposta mais antiga para a mais recente."""

        response = self.client.get(reverse('api:apostas-list'), {'ordering': 'data'})

        ids = self.ids_retornados(response)
        self.assertEqual(ids[:2], [self.aposta_barata.id, self.aposta_cara.id])
