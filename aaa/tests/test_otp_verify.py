import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from aaa.models.user_models import CustomUser
from aaa.models.otp import OTP
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_verify_otp_success():
    OTP.objects.create(
        phone='09120005555',
        code='123456',
        expires_at=timezone.now() + timedelta(minutes=1)
    )

    client = APIClient()
    url = reverse('auth:auth_otp_verify')
    response = client.post(url, {'phone': '09120005555', 'code': '123456'}, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key
    assert CustomUser.objects.filter(phone='09120005555').exists()


@pytest.mark.django_db
def test_verify_invalid_code():
    OTP.objects.create(
        phone='09120001111',
        code='654321',
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    client = APIClient()
    url = reverse('auth:auth_otp_verify')
    response = client.post(url, {'phone': '09120001111', 'code': '999999'}, format='json')

    assert response.status_code == 400
    assert 'non_field_errors' in response.data or 'code' in response.data
