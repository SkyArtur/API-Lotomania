from .parsers import parse_points
from ._decorators import validators_decorator as validation

__all__ = ['validate_range_points']


@validation
def validate_range_points(value: str | int) -> bool:
    """Valida se uma pontuação pertence às faixas aceitas da Lotomania.

    Args:
        value: Pontuação que será validada.

    Returns:
        `True` quando a pontuação pertence às faixas aceitas.

    Raises:
        ValueError: Quando a pontuação não pertence às faixas aceitas.
    """
    references = {0, 15, 16, 17, 18, 19, 20}
    point = parse_points(value, references)
    if point is None:
        raise ValueError(f'Invalid value: {value}. Must be a number between 0 and 20.')
    return True
