from django.db import models

__all__ = ['Contest']


class Contest(models.Model):
    reference = models.PositiveIntegerField(primary_key=True)
    date = models.DateField()
    numbers = models.ManyToManyField('Number', related_name='contests', through='ContestNumber')

    class Meta:
        db_table = 'contest'
        verbose_name = 'Concurso'
        verbose_name_plural = 'Concursos'
        ordering = ['-reference', '-date']

    def __str__(self):
        return f'{self.reference:04d}'

    def __repr__(self):
        return f'<Contest {self.__str__()}>'
