from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from .creates import (
    create_bet,
    bulk_create_any_number,
    bulk_create_bet_contest,
    bulk_create_bet_result,
    bulk_create_bet_prize
)

__all__ = ['post_bet']


def post_bet(bet: dict) -> bool:
    try:
        with transaction.atomic():
            new_bet = create_bet(bet)
            bulk_create_any_number(new_bet, bet['numbers'])
            bulk_create_bet_contest(new_bet)
            bulk_create_bet_result(new_bet)
            bulk_create_bet_prize(new_bet)
            return True
    except (IntegrityError, KeyError) as error:
        raise ValidationError('Error creating a new bet.') from error
