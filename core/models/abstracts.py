from django.db import models
from core.utils import validate_range_points

__all__ = ['Prize']


class Prize(models.Model):
    points = models.PositiveIntegerField(default=0, validators=[validate_range_points])
    value = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class Result(models.Model):
    hits = models.PositiveSmallIntegerField()
    mirror_hits = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True
