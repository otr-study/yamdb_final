from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.constraints import UniqueConstraint


class UserRole:

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


USER_ROLE = (
    (UserRole.USER, UserRole.USER),
    (UserRole.MODERATOR, UserRole.MODERATOR),
    (UserRole.ADMIN, UserRole.ADMIN),
)


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=150,
    )
    email = models.EmailField(
        'Электронный адрес',
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Пользовательская роль',
        max_length=max(len(role) for role, _ in USER_ROLE),
        choices=USER_ROLE,
        default=USER_ROLE[0][0],
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=24,
        blank=True
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('email', 'username'),
                name='unique_user'
            ),
        )
        ordering = ('id',)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR
