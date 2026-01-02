# devblogg_auth/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from devblogg_common.models import BaseModel

class UserRole(models.TextChoices):
    USER = 'USER', _('User')
    MODERATOR = 'MODERATOR', _('Moderator')
    ADMIN = 'ADMIN', _('Admin')

class User(AbstractUser, BaseModel):
    """
    Custom User Model.
    Mapping Rule 1.A:
    - Email & Username unique.
    - Default Role = USER.
    """
    email = models.EmailField(_('email address'), unique=True)
    
    bio = models.TextField(max_length=500, blank=True, default='')
    
    # Avatar logic sinh tự động sẽ nằm ở Service, trường này chỉ lưu URL
    avatar_url = models.URLField(max_length=1024, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True
    )

    is_banned = models.BooleanField(default=False, db_index=True)
    banned_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email', 'username']),
        ]

    def __str__(self):
        return self.email