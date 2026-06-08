from core.models import Number, Bet, BetNumber, Contest, ContestNumber

__all__ = ['bulk_create_any_number']


def bulk_create_any_number(obj: Bet | Contest, list_numbers: list[int]) -> None:
    numbers = []
    map_numbers = {n.value: n for n in Number.objects.all()}

    if isinstance(obj, Bet):

        for num in list_numbers:
            numbers.append(BetNumber(bet=obj, number=map_numbers[num]))
        BetNumber.objects.bulk_create(numbers)

    elif isinstance(obj, Contest):

        for num in list_numbers:
            numbers.append(ContestNumber(contest=obj, number=map_numbers[num]))
        ContestNumber.objects.bulk_create(numbers)

    else:
        raise TypeError('Invalid object type.')

    return None