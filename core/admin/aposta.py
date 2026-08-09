from django.contrib import admin

from core.models import Aposta, ApostaNumero, ApostaPremio, ApostaSorteio, ApostaResultado


__all__ = ['ApostaAdmin']


class ApostaNumeroInline(admin.TabularInline):

    model = ApostaNumero
    extra = 0


class ApostaPremioInline(admin.TabularInline):

    model = ApostaPremio
    extra = 0


class ApostaSorteioInline(admin.TabularInline):

    model = ApostaSorteio
    extra = 0


class ApostaResultadoInline(admin.TabularInline):

    model = ApostaResultado


@admin.register(Aposta)
class ApostaAdmin(admin.ModelAdmin):
    """Administração de apostas: números escolhidos, sorteios cobertos, resultados e prêmios em inlines."""

    list_display = ('id', 'data_aposta', 'valor', 'apostador', 'sorteios_validos', 'numeros_apostados', 'espelho')
    search_fields = ('id', 'data')
    list_display_links = ('id', 'data_aposta')
    list_filter = ('data', 'apostador',)
    list_per_page = 25
    inlines = [ApostaNumeroInline, ApostaSorteioInline, ApostaPremioInline, ApostaResultadoInline]

    @admin.display(description='Data da aposta', ordering='data')
    def data_aposta(self, obj):
        """Data da aposta formatada como `dd/mm/aaaa`."""
        return obj.data.strftime('%d/%m/%Y')

    @admin.display(description='Validade da Aposta')
    def sorteios_validos(self, obj):
        """Intervalo de concursos (`inicial`-`final`) para os quais a aposta vale."""
        return f'{obj.inicial} - {obj.final}'

    @admin.display(description='Números Apostados')
    def numeros_apostados(self, obj):
        """Lista formatada dos 50 números escolhidos na aposta."""
        return ', '.join(
            f'{valor:02d}'
            for valor in obj.numeros.values_list('valor', flat=True)
        )
