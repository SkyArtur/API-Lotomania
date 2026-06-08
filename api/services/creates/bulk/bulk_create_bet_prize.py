from core.models import Bet, Contest, BetPrize
from .assistants import get_bet_contest_pairs

__all__ = ['bulk_create_bet_prize']


def bulk_create_bet_prize(obj: Bet | Contest) -> None:
    prizes_to_create = []
    pairs = get_bet_contest_pairs(obj)

    for bet, contest in pairs:
        result = bet.results.filter(contest=contest).first()

        if result is None:
            continue

        points = [result.hits]

        if bet.mirror:
            points.append(result.mirror_hits)

        prizes = contest.prizes.filter(points__in=points)

        for prize in prizes:
            already_exists = bet.prizes.filter(contest=contest, points=prize.points).exists()

            if already_exists:
                continue

            prizes_to_create.append(
                BetPrize(
                    bet=bet,
                    contest=contest,
                    points=prize.points,
                    value=prize.value
                )
            )

    BetPrize.objects.bulk_create(prizes_to_create)
    return None
