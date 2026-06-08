from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

__all__ = ['Number']


class Number(models.Model):
    value = models.SmallIntegerField(primary_key=True,validators=[MinValueValidator(0), MaxValueValidator(99)])

    def __str__(self):
        return f'{self.value:02d}'

    def __repr__(self):
        return f'<Number {self.value:02d}>'

    class Meta:
        db_table = 'number'
        verbose_name = 'Number'
        verbose_name_plural = 'Numbers'
        ordering = ['value']
