from decimal import Decimal

from rest_framework import serializers

from core.models import Contest, Number

__all__ = [
    'ContestModelSerializer',
    'ContestSerializer',
    'ContestPrizeSerializer',
    'ContestListSerializer',
    'ContestDetailModelSerializer',
    'ContestCreateSerializer',
    'ContestNumbersListSerializer',
]


class ContestPrizeSerializer(serializers.Serializer):

    points = serializers.IntegerField()
    winners = serializers.IntegerField(min_value=0)
    value = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.00'))


class ContestModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contest
        fields = '__all__'


class ContestSerializer(serializers.Serializer):

    reference = serializers.IntegerField(min_value=1)
    date = serializers.DateField(format="%Y-%m-%d")
    numbers = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=99))
    prizes = ContestPrizeSerializer(many=True)


class ContestNumbersListSerializer(serializers.ModelSerializer):

    numbers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='value')

    class Meta:
        model = Contest
        fields = ['reference', 'numbers']


class ContestListSerializer(ContestModelSerializer):

    class Meta:
        model = Contest
        fields = ['reference', 'date']


class ContestDetailModelSerializer(ContestModelSerializer):

    numbers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='value')
    prizes = ContestPrizeSerializer(many=True, read_only=True)

    class Meta:
        model = Contest
        fields = ['reference', 'date', 'numbers', 'prizes']


class ContestCreateSerializer(ContestSerializer):

    def validate_reference(self, reference):
        if Contest.objects.filter(reference=reference).exists():
            raise serializers.ValidationError('Contest already exists.')
        return reference

    def validate_numbers(self, numbers):
        map_numbers = {num.value: num for num in Number.objects.all()}
        if len(numbers) != 20:
            raise serializers.ValidationError('Invalid number of numbers.')
        if len(set(numbers)) != len(numbers):
            raise serializers.ValidationError('Numbers must be unique.')
        if any(num not in map_numbers for num in numbers):
            raise serializers.ValidationError('Number not found.')
        return numbers

    def validate_prizes(self, prizes):
        valid_points = {0, 15, 16, 17, 18, 19, 20}
        if any(prize['points'] not in valid_points for prize in prizes):
            raise serializers.ValidationError('Invalid value for points of prize.')
        points = [prize['points'] for prize in prizes]
        if len(set(points)) != len(points):
            raise serializers.ValidationError('Prize points must be unique.')
        return prizes
