import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from aaa.models.user_models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_logout_success():
    user = CustomUser.objects.create_user(phone='09120002222', password='testpass')
    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.force_authenticate(user)

    url = reverse('auth:auth_logout')
    response = client.post(url, {'refresh': str(refresh)})

    assert response.status_code == 205
    # اطمینان از اینکه توکن در لیست بلاک‌شده ثبت شده
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
    assert BlacklistedToken.objects.filter(token__jti=refresh['jti']).exists()


@pytest.mark.django_db
def test_logout_with_invalid_token():
    user = CustomUser.objects.create_user(phone='09129999999', password='testpass')
    client = APIClient()
    client.force_authenticate(user)

    url = reverse('auth:auth_logout')
    response = client.post(url, {'refresh': 'invalidtoken'})
    assert response.status_code == 400
