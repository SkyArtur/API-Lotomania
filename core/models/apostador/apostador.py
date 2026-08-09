from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.utils import validar_username
from core.models.apostador.managers import ApostadorUserManager


__all__ = ['Apostador']


class Apostador(AbstractBaseUser, PermissionsMixin):
    """Usuário da API: o apostador dono de suas apostas, autenticado via JWT."""

    username = models.CharField(max_length=15, unique=True, validators=[validar_username])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = ApostadorUserManager()

    USERNAME_FIELD = 'username'

    class Meta:

        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'

    def __str__(self):
        return self.username
