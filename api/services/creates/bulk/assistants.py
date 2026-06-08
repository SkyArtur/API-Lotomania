from core.models import Bet, Contest

__all__ = ['get_bet_contest_pairs']


def get_bet_contest_pairs(obj: Bet | Contest) -> list[tuple]:
    if isinstance(obj, Bet):
        return [(obj, contest) for contest in obj.contests.prefetch_related('numbers', 'prizes')]
    elif isinstance(obj, Contest):
        return [(bet, obj) for bet in obj.bets.prefetch_related('numbers')]
    else:
        raise TypeError('Invalid object type.')
