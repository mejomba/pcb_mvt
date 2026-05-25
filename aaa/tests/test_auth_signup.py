import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.urls import reverse
from aaa.models.user_models import CustomUser


@pytest.mark.django_db
def test_signup_success():
    client = APIClient()
    url = reverse('auth:auth_signup')
    data = {
        'phone': '09123456789',
        'password': 'securepass123'
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key
    assert response.data['user']['phone'] == '09123456789'
    assert CustomUser.objects.filter(phone='09123456789').exists()


@pytest.mark.django_db
def test_signup_with_existing_phone_should_fail():
    CustomUser.objects.create_user(phone='09123456789', password='existingpass')
    client = APIClient()
    url = reverse('auth:auth_signup')
    data = {
        'phone': '09123456789',
        'password': 'anotherpass'
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 400
    assert 'phone' in response.data
