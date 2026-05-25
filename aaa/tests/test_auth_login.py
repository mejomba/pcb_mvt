import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from aaa.models.user_models import CustomUser


@pytest.mark.django_db
def test_login_success():
    CustomUser.objects.create_user(phone="09120001111", password="secure123")

    client = APIClient()
    url = reverse('auth:auth_login')
    response = client.post(url, {'phone': '09120001111', 'password': 'secure123'}, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key
    assert response.data['user']['phone'] == '09120001111'


@pytest.mark.django_db
def test_login_wrong_password():
    CustomUser.objects.create_user(phone="09120001111", password="secure123")

    client = APIClient()
    url = reverse('auth:auth_login')
    response = client.post(url, {'phone': '09120001111', 'password': 'wrongpass'}, format='json')

    assert response.status_code == 400
    assert 'non_field_errors' in response.data or 'detail' in response.data
