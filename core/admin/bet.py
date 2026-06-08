from django.contrib import admin

from core.models import Bet, BetNumber, BetPrize, BetContest, BetResult

__all__ = ['BetAdmin']


class BetNumberInline(admin.TabularInline):
    model = BetNumber
    extra = 0


class BetPrizeInline(admin.TabularInline):
    model = BetPrize
    extra = 0


class BetContestInline(admin.TabularInline):
    model = BetContest
    extra = 0


class BetResultInline(admin.TabularInline):
    model = BetResult


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('id', 'bet_date', 'value', 'valid_contests', 'contests_held', 'numbers_bet', 'mirror')
    search_fields = ('id', 'date')
    list_display_links = ('id', 'bet_date')
    list_filter = ('date',)
    list_per_page = 25
    inlines = [BetNumberInline, BetContestInline, BetPrizeInline, BetPrizeInline]

    @admin.display(description='Data da aposta', ordering='date')
    def bet_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')

    @admin.display(description='Validade da Aposta')
    def valid_contests(self, obj):
        return f'{obj.initial} - {obj.final}'

    @admin.display(description='Concursos realizados')
    def contests_held(self, obj):
        return ', '.join(
            f'{contest.reference:04d}'
            for contest in obj.contests.all()
        )

    @admin.display(description='Premiações Recebidas')
    def prizes_received(self, obj):
        return ' | '.join(
            f'{prize.points} pontos - R$ {prize.value:.2f}'
            for prize in obj.prizes.all()
        )

    @admin.display(description='Números Apostados')
    def numbers_bet(self, obj):
        return ', '.join(
            f'{value:02d}'
            for value in obj.numbers.values_list('value', flat=True)
        )
