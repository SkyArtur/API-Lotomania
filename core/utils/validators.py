from functools import wraps
from typing import Callable
from django.core.exceptions import ValidationError

from .parsers import analisar_pontos


__all__ = ['decorador_validadores', 'validar_pontos', 'validar_username']


def decorador_validadores(func: Callable) -> Callable:
    """
    Adapta uma função validadora (que levanta `ValueError`/`TypeError`/`AttributeError`
    em caso de valor inválido) para o formato esperado pelos `validators` de
    campo do Django, que exige uma `django.core.exceptions.ValidationError`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Callable:

        try:

            return func(*args, **kwargs)

        except (AttributeError, TypeError, ValueError) as e:
            raise ValidationError(str(e))

    return wrapper


@decorador_validadores
def validar_pontos(valor: str | int) -> bool:
    """Valida que `valor` é uma pontuação de prêmio válida (0 ou de 15 a 20)."""

    ponto = analisar_pontos(valor)

    if ponto is None:
        raise ValueError(f'Valor inválido: {valor}. Deve ser um número entre 0 e 20.')

    return True


@decorador_validadores
def validar_username(valor: str) -> bool:
    """Valida que `valor` é um username aceitável: alfanumérico, entre 4 e 15 caracteres."""

    if not valor.isalnum():
        raise ValueError(f'Valor inválido: {valor}. O username deve conter apenas letras e números.')

    if len(valor) < 4 or len(valor) > 15:
        raise ValueError(f'Valor inválido: {valor}. O username deve ter entre 4 e 15 caracteres.')

    return True

