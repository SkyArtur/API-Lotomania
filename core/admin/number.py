from django.contrib import admin

from core.models import Number

__all__ = ['NumberAdmin']


@admin.register(Number)
class NumberAdmin(admin.ModelAdmin):
    list_display = ('value',)
    search_fields = ('value',)
    list_per_page = 25
