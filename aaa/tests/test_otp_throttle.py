import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from aaa.models.otp import OTP
from aaa.utils.auth_throttle import _cache_key
from django.core.cache import cache
import random


def unique_phone():
    return '0912' + str(random.randint(1000000, 9999999))


def create_otp_for_testing(phone=None, code='123456'):
    if not phone:
        phone = unique_phone()
    otp = OTP.objects.create(
        phone=phone,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=5)
    )
    return otp


@pytest.mark.django_db
def test_otp_verify_throttle_blocks_after_5_failures():
    otp = create_otp_for_testing()
    phone = otp.phone

    client = APIClient()
    url = reverse('auth:auth_otp_verify')

    for _ in range(5):
        response = client.post(url, {'phone': phone, 'code': '000000'})
        assert response.status_code == 400

    response = client.post(url, {'phone': phone, 'code': '000000'})
    assert response.status_code == 400
    assert 'Too many failed attempts' in str(response.data)


@pytest.mark.django_db
def test_otp_verify_throttle_resets_on_success():
    otp = create_otp_for_testing()
    phone = otp.phone
    code = otp.code

    client = APIClient()
    url = reverse('auth:auth_otp_verify')

    for _ in range(2):
        client.post(url, {'phone': phone, 'code': 'wrongcode'})

    response = client.post(url, {'phone': phone, 'code': code})
    assert response.status_code == 200
    assert cache.get(_cache_key(phone)) is None
