from django.contrib import admin

from core.models import Sorteio, SorteioNumero, SorteioPremio


__all__ = ['SorteioAdmin']


class SorteioNumeroInline(admin.TabularInline):

    model = SorteioNumero
    extra = 0


class SorteioPremioInline(admin.TabularInline):

    model = SorteioPremio
    extra = 0


@admin.register(Sorteio)
class SorteioAdmin(admin.ModelAdmin):
    """Administração de sorteios: números sorteados e tabela de prêmios em inlines."""

    list_display = ('referencia', 'data_sorteio', 'numeros_sorteados', 'premios')
    search_fields = ('referencia',)
    list_display_links = ('referencia',)
    list_filter = ('data',)
    list_per_page = 25
    inlines = [SorteioNumeroInline, SorteioPremioInline]

    @admin.display(description='Data do concurso', ordering='data')
    def data_sorteio(self, obj):
        """Data do concurso formatada como `dd/mm/aaaa`."""
        return obj.data.strftime('%d/%m/%Y')

    @admin.display(description='Números sorteados')
    def numeros_sorteados(self, obj):
        """Lista formatada dos 20 números sorteados no concurso."""
        return ', '.join(f'{valor:02d}' for valor in obj.numeros.values_list('valor', flat=True))

    @admin.display(description='Prêmios pagos')
    def premios(self, obj):
        """Resumo dos prêmios pagos em cada faixa de pontos do concurso."""
        return ' | '.join(
            f'{premio.pontos} pontos - {premio.ganhadores} ganhadores - R$ {premio.valor:.2f}'
            for premio in obj.premios.all()
        )
