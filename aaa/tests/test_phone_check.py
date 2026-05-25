import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from aaa.models.user_models import CustomUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_phone_check_existing_user_password_method(api_client):
    # Arrange
    user = CustomUser.objects.create_user(phone="09123456789", password="testpass")
    url = reverse('auth:phone_check')
    data = {
        "phone": "09123456789",
        "method": "password"
    }

    # Act
    response = api_client.post(url, data, format='json')

    # Assert
    assert response.status_code == 200
    assert response.data == {
        "exists": True,
        "method": "password",
        "next_step": "login"
    }


@pytest.mark.django_db
def test_phone_check_new_user_password_method(api_client):
    url = reverse('auth:phone_check')
    data = {
        "phone": "09987654321",
        "method": "password"
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == 200
    assert response.data == {
        "exists": False,
        "method": "password",
        "next_step": "register"
    }


@pytest.mark.django_db
def test_phone_check_otp_method_existing_user(api_client):
    CustomUser.objects.create_user(phone="09111111111", password="otp-pass")
    url = reverse('auth:phone_check')
    data = {
        "phone": "09111111111",
        "method": "otp"
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == 200
    assert response.data == {
        "exists": True,
        "method": "otp",
        "next_step": "login"
    }


@pytest.mark.django_db
def test_phone_check_missing_fields(api_client):
    url = reverse('auth:phone_check')
    response = api_client.post(url, {"phone": ""}, format='json')

    assert response.status_code == 400
    assert 'detail' in response.data
