import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from aaa.models.otp import OTP


@pytest.mark.django_db
def test_send_otp_creates_entry():
    client = APIClient()
    url = reverse('auth:auth_otp_send')
    data = {'phone': '09123456789'}

    response = client.post(url, data, format='json')

    assert response.status_code == 201
    assert OTP.objects.filter(phone='09123456789').count() == 1
