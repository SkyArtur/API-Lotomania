from django.contrib import admin

from core.models import Contest, ContestNumber, ContestPrize

__all__ = ['ContestAdmin']


class ContestNumberInline(admin.TabularInline):
    model = ContestNumber
    extra = 0


class ContestPrizeInline(admin.TabularInline):
    model = ContestPrize
    extra = 0


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('reference', 'contest_date', 'drawn_numbers', 'prizes')
    search_fields = ('reference',)
    list_display_links = ('reference',)
    list_filter = ('date',)
    list_per_page = 25
    inlines = [ContestNumberInline, ContestPrizeInline]

    @admin.display(description='Data do concurso', ordering='date')
    def contest_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')

    @admin.display(description='Números sorteados')
    def drawn_numbers(self, obj):
        return ', '.join(f'{value:02d}' for value in obj.numbers.values_list('value', flat=True))

    @admin.display(description='Prêmios pagos')
    def prizes(self, obj):
        return ' | '.join(
            f'{prize.points} pontos - {prize.winners} ganhadores - R$ {prize.value:.2f}'
            for prize in obj.prizes.all()
        )
