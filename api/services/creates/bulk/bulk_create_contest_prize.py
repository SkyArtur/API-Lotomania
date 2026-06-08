from core.models import Contest, ContestPrize

__all__ = ['bulk_create_contest_prize']


def bulk_create_contest_prize(contest: Contest, list_prizes: list[dict]) -> None:
    prizes = []

    for prize in list_prizes:

        if prize['winners'] > 0:
            prizes.append(ContestPrize(contest=contest, **prize))

    ContestPrize.objects.bulk_create(prizes)
    return None
