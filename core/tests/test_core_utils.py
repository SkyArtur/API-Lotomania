from django.test import TestCase

from .temp_file import TEMP_FILE

from core.utils import (
    leitor_csv,
    analisar_datas,
    analisar_numeros,
    analisar_pontos,
    analisar_sorteio,
    extrair_referencias_sorteio_lotomania,
    extrair_numeros_sorteio_lotomania,
    extrair_premios_sorteio_lotomania
)


class LeitorCSVTestCase(TestCase):

    def test_leitor_csv(self):
        """Testar se a função `leitor_csv` retorna uma lista e se o conteúdo continua íntegro."""

        conteudo = leitor_csv(TEMP_FILE)

        self.assertEqual(len(conteudo), 2)
        self.assertEqual(isinstance(conteudo, list), True)
        self.assertEqual(conteudo[1]["Ganhadores 20 acertos"], "1")


class ParsersTestCase(TestCase):

    def setUp(self):
        self.conteudo = leitor_csv(TEMP_FILE)

    def test_analisar_datas(self):
        """Testar se a função `analisar_datas` atua sobre diferentes formatos de data."""

        from datetime import date

        for data in ['01/02/2022', '01022022', '01-02-2022']:
            analise = analisar_datas(data)
            self.assertEqual(analise.strftime('%d/%m/%Y'), '01/02/2022')

        formato_iso = analisar_datas('2022-02-01')
        self.assertEqual(isinstance(formato_iso, date), False)

        formato_iso = analisar_datas('2022-02-01', formato_iso=True)
        self.assertEqual(isinstance(formato_iso, date), True)


    def test_analisar_numeros(self):
        """Testar se a função `analisar_numeros` atua sobre diferentes tipos numéricos."""

        sorteio = self.conteudo[0]
        referencia = analisar_numeros(sorteio['Concurso'])
        ganhadores = analisar_numeros(sorteio["Ganhadores 20 acertos"], inteiro=True)
        premio = analisar_numeros(sorteio["Rateio 20 acertos"], brl=True)

        self.assertEqual(isinstance(referencia, float), True)
        self.assertEqual(isinstance(ganhadores, int), True)
        self.assertEqual(premio, 0.0)
        self.assertEqual(analisar_numeros([]), None)

    def test_analisar_pontos(self):
        """Testar se a função `analisar_pontos` é capaz de validar pontos dentro e fora da pontuação válida para a Lotomania"""

        self.assertEqual(analisar_pontos('0'), 0)
        self.assertEqual(analisar_pontos(17), 17)
        self.assertEqual(analisar_pontos(15.5), None)

    def test_analisar_sorteio(self):
        """Testar se a função `analisar_concurso` normaliza as chaves e retorna uma lista de dicionários."""

        analises = analisar_sorteio(self.conteudo)

        self.assertEqual(isinstance(analises, list), True)
        self.assertEqual(isinstance(analises[0], dict), True)
        self.assertEqual('concurso' in analises[0].keys(), True)
        self.assertEqual('data sorteio' in analises[0].keys(), True )
        self.assertEqual('rateio_20' in analises[0].keys(), True)



class ExtractorsTestCase(TestCase):
    def setUp(self):
        self.conteudo = leitor_csv(TEMP_FILE)
        self.analisador = analisar_sorteio(self.conteudo)

    def test_extrair_referencias_sorteio_lotomania(self):
        """Testar se o extrator retorna um dicionário com as chaves que serão usadas como campos para as models."""

        from datetime import date

        item = self.analisador[0]
        sorteio = extrair_referencias_sorteio_lotomania(item)

        self.assertEqual(isinstance(sorteio, dict), True)
        self.assertEqual('referencia' in sorteio.keys(), True)
        self.assertEqual(isinstance(sorteio['data'], date), True)


    def test_extrair_numeros_sorteio_lotomania(self):
        """Testar se o extrator retorna uma lista de inteiros."""

        item = self.analisador[1]
        numeros = extrair_numeros_sorteio_lotomania(item, 'bola')

        self.assertEqual(isinstance(numeros, list), True)
        self.assertEqual(isinstance(numeros[0], int), True)

    def test_extrair_premios_sorteio_lotomania(self):
        """Testar se o extrator retorna um dicionário com prêmios e as chaves apropriadas para as models futuras."""

        item = self.analisador[1]
        premios = extrair_premios_sorteio_lotomania(item)

        self.assertEqual(isinstance(premios, list), True)
