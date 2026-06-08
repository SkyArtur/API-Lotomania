from django.db import models

__all__ = ['ContestNumber']


class ContestNumber(models.Model):
    number = models.ForeignKey(to='Number', on_delete=models.PROTECT)
    contest = models.ForeignKey(to='Contest', on_delete=models.CASCADE)

    class Meta:
        db_table = 'contest_number'
        verbose_name = 'Número de concurso'
        verbose_name_plural = 'Números de concursos'
        constraints = [
            models.UniqueConstraint(fields=['number', 'contest'], name='unique_number_contest')
        ]
