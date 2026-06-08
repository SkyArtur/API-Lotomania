from rest_framework import serializers

from core.models import Number

__all__ = ['NumberSerializer']


class NumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Number
        fields = ('value',)
