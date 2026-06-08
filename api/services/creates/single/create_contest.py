from core.models import Contest

__all__ = ['create_contest']


def create_contest(data_contest: dict) -> Contest:
    contest = Contest.objects.create(
        reference=data_contest['reference'],
        date=data_contest['date']
    )
    return contest
