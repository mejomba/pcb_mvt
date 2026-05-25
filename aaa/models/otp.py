from django.db import models
from django.utils import timezone


class OTPManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_used=False)


class OTP(models.Model):
    phone = models.CharField(max_length=15, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    objects = OTPManager()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone} - {self.code}"
