import warnings

from core.models import Bet, BetPrize
from api.functions import calculate_results

__all__ = ['create_bet_prize']


def create_bet_prize(bet: Bet) -> None:
    """DEPRECATED - This function is deprecated. Use the `bulk_create_bet_prize` function instead.

    Calculates bet results and records the corresponding prize entries.

    This function processes the hits of a given bet (including standard hits
    and mirror hits, if applicable) by matching them against the prizes available
    for the specific contest. If the bet qualifies for a prize in either category,
    a new `BetPrize` record is persisted in the database.

    Args:
        bet (Bet): The bet instance to be evaluated for prize creation.

    Returns:
        None
    """

    warnings.warn(
        'This function is deprecated. Use the `bulk_create_bet_prize` function instead.',
        DeprecationWarning
    )

    results = calculate_results(bet)

    for result in results:
        contest = result['contest']

        prize_hits = contest.prizes.filter(points=result['hits']).first()
        prize_mirror = contest.prizes.filter(points=result['mirror_hits']).first()

        if prize_hits is not None:
            BetPrize.objects.create(bet=bet, contest=contest, points=prize_hits.points, value=prize_hits.value)
        if prize_mirror is not None:
            BetPrize.objects.create(bet=bet, contest=contest, points=prize_mirror.points, value=prize_mirror.value)

    return None
