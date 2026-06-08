from core.models import Bet, Contest, BetContest

__all__ = ['bulk_create_bet_contest']


def bulk_create_bet_contest(obj: Contest | Bet) -> None:
    bet_contests = []

    if isinstance(obj, Contest):
        bets = Bet.objects.filter(initial__lte=obj.reference, final__gte=obj.reference)

        for bet in bets:
            bet_contests.append(BetContest(bet=bet, contest=obj))

    elif isinstance(obj, Bet):
        contests = Contest.objects.filter(reference__gte=obj.initial, reference__lte=obj.final)

        for contest in contests:
            bet_contests.append(BetContest(bet=obj, contest=contest))

    else:
        raise TypeError('Invalid object type.')

    BetContest.objects.bulk_create(bet_contests)
    return None
