from django.test import TestCase

from core.data import dados_sorteios_lotomania


class DadosSorteiosLotomaniaTestCase(TestCase):
    """Testar se a função de recuperação de dados do arquivo oficial da Lotomania, esta processando os dados do arquivo lotomania.csv."""

    def setUp(self):
        self.dados = dados_sorteios_lotomania()
        self.ultimo_sorteio = self.dados[-1]

    def test_tamanho_da_lista(self):

        self.assertEqual(len(self.dados or []) , self.ultimo_sorteio['sorteio']['referencia'])

    def test_tamanho_da_lista_numeros(self):

        self.assertEqual(len(self.ultimo_sorteio['numeros']), 20)

    def test_chaves_dos_premios(self):

        self.assertEqual('pontos' in self.ultimo_sorteio['premios'][0].keys(), True)
        self.assertEqual('ganhadores' in self.ultimo_sorteio['premios'][0].keys(), True)
        self.assertEqual('valor' in self.ultimo_sorteio['premios'][0].keys(), True)