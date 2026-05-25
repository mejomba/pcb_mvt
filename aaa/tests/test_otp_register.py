import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from aaa.models import CustomUser
from aaa.models.otp import OTP


@pytest.mark.django_db
def test_otp_register_success():
    client = APIClient()
    phone = '09121234567'
    code = '654321'

    # ساخت OTP معتبر
    otp = OTP.objects.create(
        phone=phone,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    response = client.post(reverse('auth:otp-register'), {
        'phone': phone,
        'code': code
    })

    assert response.status_code == 201
    data = response.json()
    assert 'access' in data
    assert 'refresh' in response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key
    assert data['user']['phone'] == phone

    user = CustomUser.objects.get(phone=phone)
    assert user is not None

    otp.refresh_from_db()
    assert otp.is_used is True


@pytest.mark.django_db
def test_otp_register_invalid_code():
    client = APIClient()
    phone = '09121234567'
    OTP.objects.create(
        phone=phone,
        code='111111',
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    response = client.post('/api/v1/auth/otp/register/', {
        'phone': phone,
        'code': '000000'  # کد اشتباه
    })

    assert response.status_code == 400
    assert 'detail' in response.json()


@pytest.mark.django_db
def test_otp_register_expired_code():
    client = APIClient()
    phone = '09121234567'
    code = '123456'

    OTP.objects.create(
        phone=phone,
        code=code,
        expires_at=timezone.now() - timedelta(minutes=1),
    )

    response = client.post('/api/v1/auth/otp/register/', {
        'phone': phone,
        'code': code
    })

    assert response.status_code == 400
    assert 'کد منقضی' in response.json()['detail']

