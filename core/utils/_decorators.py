from functools import wraps
from typing import Callable

from django.core.exceptions import ValidationError

__all__ = ['validators_decorator']


def validators_decorator(func: Callable) -> Callable:
    """Converte erros comuns de validação em `ValidationError` do Django.

    Args:
        func: Função de validação que será executada pelo decorador.

    Returns:
        Função decorada, preparada para tratar erros comuns como validações do
        Django.

    Raises:
        ValidationError: Quando a função decorada gerar erro de atributo, tipo
        ou valor.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Callable:
        """Executa a função decorada e trata erros de validação.

        Args:
            *args: Argumentos posicionais repassados para a função decorada.
            **kwargs: Argumentos nomeados repassados para a função decorada.

        Returns:
            Resultado retornado pela função decorada.

        Raises:
            ValidationError: Quando a função decorada gerar erro de atributo,
            tipo ou valor.
        """
        try:
            return func(*args, **kwargs)
        except (AttributeError, TypeError, ValueError) as e:
            raise ValidationError(e.message)
    return wrapper
