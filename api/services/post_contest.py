from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from .creates import (
    create_contest,
    create_bet_prize,
    bulk_create_any_number,
    bulk_create_contest_prize,
    bulk_create_bet_contest,
    bulk_create_bet_result,
    bulk_create_bet_prize
)

__all__ = ['post_contest']


def post_contest(contest: dict) -> bool:
    try:
        with transaction.atomic():
            new_contest = create_contest(contest)
            bulk_create_any_number(new_contest, contest['numbers'])
            bulk_create_contest_prize(new_contest, contest['prizes'])
            bulk_create_bet_contest(new_contest)
            bulk_create_bet_result(new_contest)
            bulk_create_bet_prize(new_contest)
            return True
    except (IntegrityError, KeyError, TypeError) as error:
        raise ValidationError('Error creating a new contest.') from error
