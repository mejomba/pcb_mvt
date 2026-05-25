from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from aaa.models.managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    password = models.CharField("password", max_length=128, null=True)
    phone = models.CharField(verbose_name='تلفن همراه', max_length=11, unique=True, null=True, blank=True,
                             validators=[RegexValidator(r'^09\d{9}',
                                                        message='تلفن نا معتبر',
                                                        code='invalid_phone')])
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    is_special = models.BooleanField(default=False)
    creator_user = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='user_created')
    editor_user = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='user_edited')

    full_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'phone'

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name.strip()} {self.last_name.strip()}".strip()
        super().save(*args, **kwargs)
