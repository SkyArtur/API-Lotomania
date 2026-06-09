from decimal import Decimal

from rest_framework import serializers

from core.models import Number, Bet

__all__ = [
    'BetResultSerializer',
    'BetPrizeSerializer',
    'BetModelSerializer',
    'BetSerializer',
    'BetNumbersListSerializer',
    'BetListSerializer',
    'BetDetailSerializer',
    'BetCreateSerializer',
]

class BetResultSerializer(serializers.Serializer):

    contest = serializers.IntegerField(source='contest.reference', read_only=True)
    hits = serializers.IntegerField()
    mirror_hits = serializers.IntegerField()


class BetPrizeSerializer(serializers.Serializer):

    contest = serializers.IntegerField(source='contest.reference', read_only=True)
    points = serializers.IntegerField()
    value = serializers.DecimalField(max_digits=12, decimal_places=2)


class BetModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = '__all__'


class BetSerializer(serializers.Serializer):

    date = serializers.DateField(format="%Y-%m-%d")
    value = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.00'))
    initial = serializers.IntegerField(min_value=1)
    final = serializers.IntegerField(min_value=1)
    mirror = serializers.BooleanField(default=True)
    numbers = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=99))


class BetNumbersListSerializer(serializers.ModelSerializer):
    numbers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='value')

    class Meta:
        model = Bet
        fields = ['id', 'numbers']


class BetListSerializer(BetModelSerializer):

    class Meta:
        model = Bet
        fields = ['id', 'date', 'value', 'initial', 'final', 'mirror']


class BetDetailSerializer(serializers.ModelSerializer):
    contests = serializers.SlugRelatedField(many=True, read_only=True, slug_field='reference')
    numbers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='value')
    results = BetResultSerializer(many=True, read_only=True)
    prizes = BetPrizeSerializer(many=True, read_only=True)

    class Meta:
        model = Bet
        fields = ['id', 'date', 'value', 'initial', 'final', 'mirror', 'contests', 'numbers', 'results', 'prizes']


class BetCreateSerializer(BetSerializer):

    def validate(self, attrs):
        if attrs['initial'] > attrs['final']:
            raise serializers.ValidationError({
                'final': 'Final contest must be greater than or equal to initial contest.'
            })
        return attrs

    def validate_numbers(self, numbers):
        map_numbers = {num.value: num for num in Number.objects.all()}
        if len(numbers) != 50:
            raise serializers.ValidationError('Invalid number of numbers.')
        if len(set(numbers)) != len(numbers):
            raise serializers.ValidationError('Numbers must be unique.')
        if any(num not in map_numbers for num in numbers):
            raise serializers.ValidationError('Number not found.')
        return numbers
