"""
Testes das funções de baixo nível de `api.services.creates` (criação única e
em lote), usadas para montar uma aposta ou um sorteio completos: `create_aposta`,
`create_sorteio`, `obter_pares_aposta_sorteio` e os `bulk_create_*`. Os
orquestradores `registrar_aposta`/`registrar_sorteio`, que encadeiam essas
funções, são testados em `test_api_services.py`.
"""

from datetime import date
from types import SimpleNamespace

from django.test import TestCase

from core.models import (
    Numero,
    Sorteio,
    SorteioPremio,
    Aposta,
    Apostador,
    ApostaSorteio,
    ApostaResultado,
    ApostaPremio,
)
from api.services.creates import (
    create_aposta,
    create_sorteio,
    bulk_create_numero_qualquer,
    bulk_create_aposta_sorteio,
    bulk_create_sorteio_premio,
    bulk_create_aposta_resultado,
    bulk_create_aposta_premio,
)
from api.services.creates.bulk.pares_aposta_sorteio import obter_pares_aposta_sorteio


# Referência bem acima da faixa de concursos reais (1-2947), para isolar os
# sorteios fictícios destes testes dos ~2947 sorteios reais semeados pelas
# migrações 0002/0003.
REFERENCIA_FALSA = 999999


class CreateApostaTestCase(TestCase):
    """Testes de `create_aposta`."""

    def setUp(self):
        """Cria um apostador para autenticar as apostas de teste."""
        self.apostador = Apostador.objects.create_user(username='criador1', password='S3nhaForte!23')

    def test_cria_registro_com_os_dados_informados(self):
        """Testar se `create_aposta` cria a Aposta com os dados e o apostador informados, sem números nem sorteios."""

        request = SimpleNamespace(user=self.apostador)
        dados_aposta = {'data': date(2026, 1, 1), 'valor': '5.00', 'inicial': 1, 'final': 10, 'espelho': True}

        aposta = create_aposta(request, dados_aposta)

        self.assertEqual(aposta.apostador, self.apostador)
        self.assertEqual(aposta.inicial, 1)
        self.assertEqual(aposta.final, 10)
        self.assertTrue(aposta.espelho)
        self.assertEqual(aposta.numeros.count(), 0)


class CreateSorteioTestCase(TestCase):
    """Testes de `create_sorteio`."""

    def test_cria_registro_com_os_dados_informados(self):
        """Testar se `create_sorteio` cria o Sorteio com a referência e a data informadas, sem números nem prêmios."""

        sorteio = create_sorteio({'referencia': REFERENCIA_FALSA, 'data': date(2026, 1, 5)})

        self.assertEqual(sorteio.referencia, REFERENCIA_FALSA)
        self.assertEqual(sorteio.data, date(2026, 1, 5))
        self.assertEqual(sorteio.numeros.count(), 0)


class BulkCreateNumeroQualquerTestCase(TestCase):
    """Testes de `bulk_create_numero_qualquer`."""

    def setUp(self):
        """Cria um apostador, uma aposta e um sorteio, ambos ainda sem números associados."""
        self.apostador = Apostador.objects.create_user(username='numeros1', password='S3nhaForte!23')
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=1, final=10,
            espelho=True, apostador=self.apostador,
        )
        self.sorteio = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))

    def test_associa_numeros_a_uma_aposta(self):
        """Testar se uma lista de números é associada à Aposta via ApostaNumero."""

        bulk_create_numero_qualquer(self.aposta, [0, 1, 2])

        valores = set(self.aposta.numeros.values_list('valor', flat=True))
        self.assertEqual(valores, {0, 1, 2})

    def test_associa_numeros_a_um_sorteio(self):
        """Testar se uma lista de números é associada ao Sorteio via SorteioNumero."""

        bulk_create_numero_qualquer(self.sorteio, [10, 20, 30])

        valores = set(self.sorteio.numeros.values_list('valor', flat=True))
        self.assertEqual(valores, {10, 20, 30})

    def test_levanta_type_error_para_objeto_de_tipo_invalido(self):
        """Testar se um objeto que não é Aposta nem Sorteio levanta TypeError."""

        with self.assertRaises(TypeError):
            bulk_create_numero_qualquer(object(), [0])


class BulkCreateApostaSorteioTestCase(TestCase):
    """Testes de `bulk_create_aposta_sorteio`."""

    def setUp(self):
        """Cria um apostador e três sorteios fictícios (REFERENCIA_FALSA, +1 e +2)."""
        self.apostador = Apostador.objects.create_user(username='vincular1', password='S3nhaForte!23')
        self.sorteios = [
            Sorteio.objects.create(referencia=REFERENCIA_FALSA + i, data=date(2026, 1, 1 + i))
            for i in range(3)
        ]

    def _criar_aposta(self, inicial, final):
        return Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=inicial, final=final,
            espelho=True, apostador=self.apostador,
        )

    def test_a_partir_de_um_sorteio_vincula_apenas_as_apostas_cujo_intervalo_o_cobre(self):
        """Testar se, a partir de um Sorteio, apenas as apostas cujo inicial/final cobre a referência dele são vinculadas."""

        aposta_dentro = self._criar_aposta(REFERENCIA_FALSA, REFERENCIA_FALSA + 2)
        aposta_fora = self._criar_aposta(REFERENCIA_FALSA + 1, REFERENCIA_FALSA + 2)

        bulk_create_aposta_sorteio(self.sorteios[0])

        self.assertTrue(ApostaSorteio.objects.filter(aposta=aposta_dentro, sorteio=self.sorteios[0]).exists())
        self.assertFalse(ApostaSorteio.objects.filter(aposta=aposta_fora, sorteio=self.sorteios[0]).exists())

    def test_a_partir_de_uma_aposta_vincula_apenas_os_sorteios_dentro_do_intervalo(self):
        """Testar se, a partir de uma Aposta, apenas os sorteios com referência dentro do seu inicial/final são vinculados."""

        aposta = self._criar_aposta(REFERENCIA_FALSA, REFERENCIA_FALSA + 1)

        bulk_create_aposta_sorteio(aposta)

        vinculados = set(ApostaSorteio.objects.filter(aposta=aposta).values_list('sorteio__referencia', flat=True))
        self.assertEqual(vinculados, {REFERENCIA_FALSA, REFERENCIA_FALSA + 1})

    def test_levanta_type_error_para_objeto_de_tipo_invalido(self):
        """Testar se um objeto que não é Aposta nem Sorteio levanta TypeError."""

        with self.assertRaises(TypeError):
            bulk_create_aposta_sorteio(object())


class BulkCreateSorteioPremioTestCase(TestCase):
    """Testes de `bulk_create_sorteio_premio`."""

    def setUp(self):
        """Cria um sorteio fictício, ainda sem prêmios."""
        self.sorteio = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))

    def test_cria_apenas_as_faixas_de_pontos_com_ganhadores(self):
        """Testar se apenas as faixas de pontos com ganhadores viram registros de SorteioPremio."""

        premios = [
            {'pontos': 0, 'ganhadores': 0, 'valor': 0},
            {'pontos': 15, 'ganhadores': 0, 'valor': 0},
            {'pontos': 20, 'ganhadores': 3, 'valor': '1000.00'},
        ]

        bulk_create_sorteio_premio(self.sorteio, premios)

        self.assertEqual(self.sorteio.premios.count(), 1)
        self.assertTrue(self.sorteio.premios.filter(pontos=20, ganhadores=3).exists())


class ObterParesApostaSorteioTestCase(TestCase):
    """Testes de `obter_pares_aposta_sorteio`."""

    def setUp(self):
        """Cria uma aposta vinculada a dois sorteios fictícios já cadastrados."""
        self.apostador = Apostador.objects.create_user(username='pares1', password='S3nhaForte!23')
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=REFERENCIA_FALSA, final=REFERENCIA_FALSA + 1,
            espelho=True, apostador=self.apostador,
        )
        self.sorteios = [
            Sorteio.objects.create(referencia=REFERENCIA_FALSA + i, data=date(2026, 1, 1 + i))
            for i in range(2)
        ]
        for sorteio in self.sorteios:
            ApostaSorteio.objects.create(aposta=self.aposta, sorteio=sorteio)

    def test_a_partir_de_uma_aposta_retorna_um_par_por_sorteio_vinculado(self):
        """Testar se, a partir de uma Aposta, é devolvido um par (aposta, sorteio) para cada sorteio vinculado a ela."""

        pares = obter_pares_aposta_sorteio(self.aposta)

        self.assertEqual({sorteio.referencia for _, sorteio in pares}, {s.referencia for s in self.sorteios})

    def test_a_partir_de_um_sorteio_retorna_um_par_por_aposta_vinculada(self):
        """Testar se, a partir de um Sorteio, é devolvido um par (aposta, sorteio) para cada aposta vinculada a ele."""

        pares = obter_pares_aposta_sorteio(self.sorteios[0])

        self.assertEqual(pares, [(self.aposta, self.sorteios[0])])

    def test_levanta_type_error_para_objeto_de_tipo_invalido(self):
        """Testar se um objeto que não é Aposta nem Sorteio levanta TypeError."""

        with self.assertRaises(TypeError):
            obter_pares_aposta_sorteio(object())


class BulkCreateApostaResultadoTestCase(TestCase):
    """Testes de `bulk_create_aposta_resultado`."""

    def setUp(self):
        """Cria uma aposta com 20 números vinculada a um sorteio com 15 números em comum com ela."""
        self.apostador = Apostador.objects.create_user(username='resultado1', password='S3nhaForte!23')
        numeros = list(Numero.objects.order_by('valor')[:25])
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=REFERENCIA_FALSA, final=REFERENCIA_FALSA,
            espelho=True, apostador=self.apostador,
        )
        self.aposta.numeros.add(*numeros[:20])
        self.sorteio = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))
        self.sorteio.numeros.add(*numeros[5:20])  # 15 números em comum com a aposta
        ApostaSorteio.objects.create(aposta=self.aposta, sorteio=self.sorteio)

    def test_calcula_os_acertos_e_o_espelho_complementar_quando_a_aposta_e_espelhada(self):
        """Testar se os acertos e os acertos espelhados (20 - acertos) são calculados corretamente para uma aposta espelhada."""

        bulk_create_aposta_resultado(self.aposta)

        resultado = ApostaResultado.objects.get(aposta=self.aposta, sorteio=self.sorteio)
        self.assertEqual(resultado.acertos, 15)
        self.assertEqual(resultado.acertos_espelhados, 5)

    def test_zera_os_acertos_espelhados_quando_a_aposta_nao_e_espelhada(self):
        """Testar se `acertos_espelhados` é gravado como 0 quando a aposta não é espelhada."""

        self.aposta.espelho = False
        self.aposta.save()

        bulk_create_aposta_resultado(self.aposta)

        resultado = ApostaResultado.objects.get(aposta=self.aposta, sorteio=self.sorteio)
        self.assertEqual(resultado.acertos_espelhados, 0)


class BulkCreateApostaPremioTestCase(TestCase):
    """Testes de `bulk_create_aposta_premio`."""

    def setUp(self):
        """Cria uma aposta e um sorteio já com resultado (17 acertos) e a faixa de prêmio correspondente."""
        self.apostador = Apostador.objects.create_user(username='premio1', password='S3nhaForte!23')
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=REFERENCIA_FALSA, final=REFERENCIA_FALSA,
            espelho=False, apostador=self.apostador,
        )
        self.sorteio = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))
        SorteioPremio.objects.create(sorteio=self.sorteio, pontos=17, ganhadores=100, valor='250.00')
        ApostaSorteio.objects.create(aposta=self.aposta, sorteio=self.sorteio)
        ApostaResultado.objects.create(aposta=self.aposta, sorteio=self.sorteio, acertos=17, acertos_espelhados=0)

    def test_cria_o_premio_correspondente_a_pontuacao_do_resultado(self):
        """Testar se um ApostaPremio é criado quando os acertos do resultado batem com uma faixa premiada do sorteio."""

        bulk_create_aposta_premio(self.aposta)

        self.assertTrue(ApostaPremio.objects.filter(aposta=self.aposta, sorteio=self.sorteio, pontos=17).exists())

    def test_nao_duplica_um_premio_ja_registrado(self):
        """Testar se rodar `bulk_create_aposta_premio` duas vezes não duplica o prêmio já registrado."""

        bulk_create_aposta_premio(self.aposta)
        bulk_create_aposta_premio(self.aposta)

        self.assertEqual(
            ApostaPremio.objects.filter(aposta=self.aposta, sorteio=self.sorteio, pontos=17).count(), 1
        )
