from django.contrib import admin

from core.models import Numero


__all__ = ['NumeroAdmin']


@admin.register(Numero)
class NumeroAdmin(admin.ModelAdmin):
    """Exibe, para cada número (0-99), quantas vezes foi sorteado e quantas vezes foi apostado."""

    list_display = ('numero', 'vezes_sorteado', 'vezes_apostado')
    search_fields = ('valor',)
    list_per_page = 25

    @admin.display(description='Número', ordering='valor')
    def numero(self, obj):
        return f'{obj.valor:02d}'
