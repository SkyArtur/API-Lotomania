from core.models import Bet, BetPrize, BetResult, Contest
from .assistants import get_bet_contest_pairs

__all__ = ['bulk_create_bet_result']


def bulk_create_bet_result(obj: Contest | Bet) -> None:
    results = []
    pairs = get_bet_contest_pairs(obj)

    for bet, contest in pairs:
        bet_numbers = {n.value for n in bet.numbers.all()}
        contests_numbers = {n.value for n in contest.numbers.all()}
        hits = len(bet_numbers.intersection(contests_numbers))
        mirror_hits = 20 - hits
        results.append(
            BetResult(
                bet=bet,
                contest=contest,
                hits=hits,
                mirror_hits=mirror_hits if bet.mirror else 0
            )
        )

    BetResult.objects.bulk_create(results)
    return None
