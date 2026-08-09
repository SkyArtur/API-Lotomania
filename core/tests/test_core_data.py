"""
Testes de `core.data.dados_sorteios_lotomania`, que lê e interpreta o
`lotomania.csv` oficial (não um arquivo fictício) e devolve um dicionário por
sorteio com as chaves `sorteio`, `numeros` e `premios`.
"""

from django.test import TestCase

from core.data import dados_sorteios_lotomania


class DadosSorteiosLotomaniaTestCase(TestCase):
    """Testar se a função de recuperação de dados do arquivo oficial da Lotomania está processando os dados do arquivo lotomania.csv."""

    def setUp(self):
        """Recupera os dados do `lotomania.csv` e isola o último sorteio, usado como amostra nos testes."""
        self.dados = dados_sorteios_lotomania()
        self.ultimo_sorteio = self.dados[-1]

    def test_tamanho_da_lista(self):
        """Testar se a quantidade de sorteios lidos bate com a referência do último concurso (concursos são sequenciais a partir de 1)."""

        self.assertEqual(len(self.dados or []) , self.ultimo_sorteio['sorteio']['referencia'])

    def test_tamanho_da_lista_numeros(self):
        """Testar se cada sorteio tem os 20 números sorteados da Lotomania."""

        self.assertEqual(len(self.ultimo_sorteio['numeros']), 20)

    def test_chaves_dos_premios(self):
        """Testar se cada faixa de prêmio do sorteio tem as chaves `pontos`, `ganhadores` e `valor`."""

        self.assertEqual('pontos' in self.ultimo_sorteio['premios'][0].keys(), True)
        self.assertEqual('ganhadores' in self.ultimo_sorteio['premios'][0].keys(), True)
        self.assertEqual('valor' in self.ultimo_sorteio['premios'][0].keys(), True)