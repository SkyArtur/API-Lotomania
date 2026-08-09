from datetime import date
from unittest.mock import patch

from django.test import TestCase

from core.models import Aposta, ApostaSorteio, ApostaPremio, ApostaResultado, Apostador, Sorteio, Numero
from core.services import atualizar_sorteios

REFERENCIA_FALSA = 999999


def _dados_sorteio_falso(lista_numeros: list[int]) -> list[dict]:
    return [
        {
            'sorteio': {'referencia': REFERENCIA_FALSA, 'data': date(2026, 1, 5)},
            'numeros': lista_numeros,
            'premios': [
                {'pontos': 0, 'ganhadores': 0, 'valor': 0},
                {'pontos': 15, 'ganhadores': 0, 'valor': 0},
                {'pontos': 16, 'ganhadores': 0, 'valor': 0},
                {'pontos': 17, 'ganhadores': 0, 'valor': 0},
                {'pontos': 18, 'ganhadores': 0, 'valor': 0},
                {'pontos': 19, 'ganhadores': 0, 'valor': 0},
                {'pontos': 20, 'ganhadores': 5, 'valor': '1000.00'},
            ],
        }
    ]


class AtualizarSorteiosTests(TestCase):
    def setUp(self):
        self.apostador = Apostador.objects.create_user(username='tester1', password='S3nhaForte!23')
        self.aposta_numeros = list(Numero.objects.order_by('valor')[:50])
        self.aposta = Aposta.objects.create(
            data=date(2026, 1, 1),
            valor='5.00',
            inicial=1,
            final=REFERENCIA_FALSA,
            espelho=True,
            apostador=self.apostador,
        )
        self.aposta.numeros.add(*self.aposta_numeros)

    def test_retorna_resultado_vazio_quando_o_csv_nao_contem_dados(self):
        with patch('core.services.atualizar_sorteios.dados_sorteios_lotomania', return_value=None):
            resultados = atualizar_sorteios()

        self.assertEqual(resultados.criado, [])
        self.assertEqual(resultados.falhou, [])

    def test_cria_novo_concurso_e_atualiza_aposta_correspondente(self):
        numeros_apostados = [numero.valor for numero in self.aposta_numeros[:20]]
        with patch('core.services.atualizar_sorteios.dados_sorteios_lotomania', return_value=_dados_sorteio_falso(numeros_apostados)):
            resultado = atualizar_sorteios()

        self.assertEqual([sorteio.referencia for sorteio in resultado.criado], [REFERENCIA_FALSA])
        self.assertEqual(resultado.falhou, [])

        sorteio = Sorteio.objects.get(referencia=REFERENCIA_FALSA)
        self.assertTrue(ApostaSorteio.objects.filter(aposta=self.aposta, sorteio=sorteio).exists())

        aposta_resultado = ApostaResultado.objects.get(aposta=self.aposta, sorteio=sorteio)
        self.assertEqual(aposta_resultado.acertos, 20)
        self.assertEqual(aposta_resultado.acertos_espelhados, 0)

        aposta_premio = ApostaPremio.objects.get(aposta=self.aposta, sorteio=sorteio, pontos=20)
        self.assertEqual(str(aposta_premio.valor), '1000.00')

    def test_nao_vincula_apostas_fora_da_faixa_do_concurso(self):
        self.aposta.final = REFERENCIA_FALSA - 1
        self.aposta.save()

        numeros_apostados = [numero.valor for numero in self.aposta_numeros[:20]]
        with patch('core.services.atualizar_sorteios.dados_sorteios_lotomania', return_value=_dados_sorteio_falso(numeros_apostados)):
            atualizar_sorteios()

        sorteio = Sorteio.objects.get(referencia=REFERENCIA_FALSA)
        self.assertFalse(ApostaSorteio.objects.filter(aposta=self.aposta, sorteio=sorteio).exists())

    def test_eh_idempotente_para_concursos_ja_registrados(self):
        numeros_apostados = [numero.valor for numero in self.aposta_numeros[:20]]
        data_falsa = _dados_sorteio_falso(numeros_apostados)
        with patch('core.services.atualizar_sorteios.dados_sorteios_lotomania', return_value=data_falsa):
            atualizar_sorteios()
            resultado_secundario = atualizar_sorteios()

        self.assertEqual(resultado_secundario.criado, [])
        self.assertEqual(Sorteio.objects.filter(referencia=REFERENCIA_FALSA).count(), 1)
