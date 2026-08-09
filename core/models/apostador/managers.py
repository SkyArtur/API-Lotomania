from django.contrib.auth.models import BaseUserManager

__all__ = ['ApostadorUserManager']


class ApostadorUserManager(BaseUserManager):
    """
    Gerenciador customizado do `Apostador`, exigido pelo Django sempre que o
    model de usuário não usa `email` como identificador padrão. Os nomes dos
    métodos (`normalize_username`, `create_user`, `create_superuser`) seguem
    a convenção do `django.contrib.auth`, chamada internamente pelo framework
    e pelo comando `createsuperuser`.
    """

    @staticmethod
    def normalize_username(username):
        """Normaliza o username para minúsculo, evitando duplicidade por diferença de caixa."""
        return str(username).lower()

    def create_user(self, username, password=None, **extra_fields):
        """Cria e salva um apostador comum, com a senha já hasheada."""

        if not username:
            raise ValueError('Os usuários devem ter um username.')

        _username = self.normalize_username(username)
        user = self.model(username=_username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Cria um apostador com acesso ao Django admin (`is_staff`/`is_superuser`)."""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)