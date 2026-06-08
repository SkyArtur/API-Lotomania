from decimal import Decimal, InvalidOperation
from django.utils.formats import number_format


__all__ = ['money_formatter']

def money_formatter(value: Decimal) -> str | None:
    """Formata um valor decimal como moeda brasileira.

    Args:
        value: Valor que será convertido para `Decimal` e formatado.

    Returns:
        Texto formatado em reais. Retorna `None` quando o valor não pode ser
        convertido ou formatado.
    """
    try:
        value = number_format(Decimal(value), decimal_pos=2, use_l10n=True, force_grouping=True)
        return f'R$ {value}'
    except (InvalidOperation, TypeError, ValueError,):
        return None
