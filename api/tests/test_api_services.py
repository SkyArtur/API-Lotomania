"""
Testes dos serviços orquestradores `registrar_aposta` e `registrar_sorteio`,
que encadeiam as funções de `api.services.creates` (criação, associação de
números, vínculo aposta/sorteio, resultados e prêmios) em uma única
transação. As funções encadeadas em si são testadas isoladamente em
`test_api_creates.py`.
"""

from datetime import date
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models import (
    Numero,
    Sorteio,
    Aposta,
    Apostador,
    ApostaSorteio,
    ApostaResultado,
    ApostaPremio,
)
from api.services import registrar_aposta, registrar_sorteio


# Referência bem acima da faixa de concursos reais (1-2947), para isolar os
# sorteios fictícios destes testes dos ~2947 sorteios reais semeados pelas
# migrações 0002/0003.
REFERENCIA_FALSA = 999999


class RegistrarApostaTestCase(TestCase):
    """Testes de `registrar_aposta`."""

    def setUp(self):
        """Cria um apostador e um sorteio fictício já cadastrado, com 20 números e um prêmio de 20 pontos."""
        self.apostador = Apostador.objects.create_user(username='registrar1', password='S3nhaForte!23')
        self.numeros = list(Numero.objects.order_by('valor')[:20])
        self.sorteio = Sorteio.objects.create(referencia=REFERENCIA_FALSA, data=date(2026, 1, 1))
        self.sorteio.numeros.add(*self.numeros)
        self.sorteio.premios.create(pontos=20, ganhadores=1, valor='1000.00')

    def _request(self):
        return SimpleNamespace(user=self.apostador)

    def test_registra_a_aposta_e_confere_o_sorteio_ja_cadastrado(self):
        """Testar se `registrar_aposta` cria a aposta, associa os números, vincula o sorteio existente na faixa e grava resultado e prêmio."""

        dados = {
            'data': date(2026, 1, 1),
            'valor': '5.00',
            'inicial': REFERENCIA_FALSA,
            'final': REFERENCIA_FALSA,
            'espelho': True,
            'numeros': [numero.valor for numero in self.numeros],
        }

        resultado = registrar_aposta(self._request(), dados)

        self.assertTrue(resultado)

        aposta = Aposta.objects.get(apostador=self.apostador)
        self.assertEqual(aposta.numeros.count(), 20)
        self.assertTrue(ApostaSorteio.objects.filter(aposta=aposta, sorteio=self.sorteio).exists())

        aposta_resultado = ApostaResultado.objects.get(aposta=aposta, sorteio=self.sorteio)
        self.assertEqual(aposta_resultado.acertos, 20)

        self.assertTrue(ApostaPremio.objects.filter(aposta=aposta, sorteio=self.sorteio, pontos=20).exists())

    def test_reverte_tudo_quando_os_dados_estao_incompletos(self):
        """Testar se dados incompletos (chave `numeros` ausente) levantam ValidationError e não deixam nenhuma aposta registrada."""

        dados_incompletos = {
            'data': date(2026, 1, 1),
            'valor': '5.00',
            'inicial': REFERENCIA_FALSA,
            'final': REFERENCIA_FALSA,
            'espelho': True,
            # 'numeros' ausente de propósito
        }

        with self.assertRaises(ValidationError):
            registrar_aposta(self._request(), dados_incompletos)

        self.assertEqual(Aposta.objects.filter(apostador=self.apostador).count(), 0)


class RegistrarSorteioTestCase(TestCase):
    """Testes de `registrar_sorteio`."""

    def setUp(self):
        """Cria um apostador com uma aposta já cadastrada cujo intervalo cobre o novo sorteio a ser registrado."""
        self.apostador = Apostador.objects.create_user(username='registrar2', password='S3nhaForte!23')
        self.numeros = list(Numero.objects.order_by('valor')[:20])
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1), valor='5.00', inicial=REFERENCIA_FALSA, final=REFERENCIA_FALSA,
            espelho=True, apostador=self.apostador,
        )
        self.aposta.numeros.add(*self.numeros)

    def test_registra_o_sorteio_e_confere_as_apostas_ja_cadastradas(self):
        """Testar se `registrar_sorteio` cria o sorteio, associa números e prêmios, e confere automaticamente as apostas na faixa."""

        dados = {
            'referencia': REFERENCIA_FALSA,
            'data': date(2026, 1, 5),
            'numeros': [numero.valor for numero in self.numeros],
            'premios': [{'pontos': 20, 'ganhadores': 1, 'valor': '1000.00'}],
        }

        resultado = registrar_sorteio(dados)

        self.assertTrue(resultado)

        sorteio = Sorteio.objects.get(referencia=REFERENCIA_FALSA)
        self.assertEqual(sorteio.numeros.count(), 20)
        self.assertTrue(ApostaSorteio.objects.filter(aposta=self.aposta, sorteio=sorteio).exists())

        aposta_resultado = ApostaResultado.objects.get(aposta=self.aposta, sorteio=sorteio)
        self.assertEqual(aposta_resultado.acertos, 20)

        self.assertTrue(ApostaPremio.objects.filter(aposta=self.aposta, sorteio=sorteio, pontos=20).exists())

    def test_reverte_tudo_quando_os_dados_estao_incompletos(self):
        """Testar se dados incompletos (chave `premios` ausente) levantam ValidationError e não deixam nenhum sorteio registrado."""

        dados_incompletos = {
            'referencia': REFERENCIA_FALSA,
            'data': date(2026, 1, 5),
            'numeros': [numero.valor for numero in self.numeros],
            # 'premios' ausente de propósito
        }

        with self.assertRaises(ValidationError):
            registrar_sorteio(dados_incompletos)

        self.assertFalse(Sorteio.objects.filter(referencia=REFERENCIA_FALSA).exists())
