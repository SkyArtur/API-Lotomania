from core.models import Bet

__all__ = ['create_bet']


def create_bet(data_bet: dict) -> Bet:
    bet = Bet.objects.create(
        date=data_bet['date'],
        value=data_bet['value'],
        initial=data_bet['initial'],
        final=data_bet['final'],
        mirror=data_bet['mirror']
    )
    return bet
