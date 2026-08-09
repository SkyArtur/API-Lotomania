from django.contrib import admin

from core.models import Apostador, Aposta


__all__ = ['ApostadorAdmin']


class ApostasInline(admin.TabularInline):

    model = Aposta
    extra = 0


@admin.register(Apostador)
class ApostadorAdmin(admin.ModelAdmin):
    """Administração de apostadores, com as apostas de cada um listadas em inline."""

    list_display = ('admin_username', 'admin_is_staff')
    search_fields = ('username',)
    list_per_page = 25
    ordering = ('username',)
    inlines = [ApostasInline]

    @admin.display(description='Usuário', ordering='username')
    def admin_username(self, obj):
        return obj.username

    @admin.display(description='Administrador')
    def admin_is_staff(self, obj):
        return obj.is_staff