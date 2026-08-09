"""
Testes de `api.exceptions.custom_exception_handler`: garante que exceções já
tratadas pelo DRF continuam respondendo normalmente e que exceções não
tratadas pelo DRF sempre resultam em JSON (nunca na página de erro em HTML
do Django), exceto em desenvolvimento (`DEBUG=True`), quando a página de
debug do Django é mais útil para investigar o problema.
"""

from django.test import TestCase, override_settings
from rest_framework.exceptions import NotFound

from api.exceptions import custom_exception_handler


class CustomExceptionHandlerTestCase(TestCase):
    """Testes de `custom_exception_handler`."""

    def test_delega_para_o_exception_handler_padrao_quando_o_drf_trata_a_excecao(self):
        """Testar se uma `APIException` (ex.: `NotFound`) continua sendo respondida normalmente pelo exception_handler padrão do DRF."""

        excecao = NotFound()
        response = custom_exception_handler(excecao, {})

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 404)
        # Não comparar com o texto padrão em inglês do DRF: com LANGUAGE_CODE = 'pt-br',
        # `NotFound.default_detail` já vem traduzido ("Não encontrado.").
        self.assertEqual(response.data, {'detail': excecao.detail})

    @override_settings(DEBUG=True)
    def test_retorna_none_em_debug_para_excecao_nao_tratada_pelo_drf(self):
        """Testar se, com DEBUG=True, uma exceção que o DRF não trata devolve None (deixa o Django mostrar a página de debug padrão)."""

        response = custom_exception_handler(ValueError('erro interno'), {})

        self.assertIsNone(response)

    @override_settings(DEBUG=False)
    def test_retorna_json_generico_em_producao_para_excecao_nao_tratada_pelo_drf(self):
        """Testar se, com DEBUG=False, uma exceção que o DRF não trata devolve uma resposta JSON genérica com status 500."""

        response = custom_exception_handler(ValueError('erro interno'), {})

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertIn('detail', response.data)
