import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from aaa.models.user_models import CustomUser
from aaa.utils.auth_throttle import _cache_key
from django.core.cache import cache


@pytest.mark.django_db
def test_login_throttle_blocks_after_5_failures():
    CustomUser.objects.create_user(phone='09120001111', password='correctpass')

    client = APIClient()
    url = reverse('auth:auth_login')

    for _ in range(5):
        response = client.post(url, {'phone': '09120001111', 'password': 'wrongpass'})
        assert response.status_code == 400

    # تلاش ششم باید بلاک بشه
    response = client.post(url, {'phone': '09120001111', 'password': 'wrongpass'})
    assert response.status_code == 400
    assert 'Too many failed attempts' in str(response.data)


@pytest.mark.django_db
def test_login_throttle_resets_on_success():
    user = CustomUser.objects.create_user(phone='09120002222', password='correctpass')

    client = APIClient()
    url = reverse('auth:auth_login')

    for _ in range(3):
        client.post(url, {'phone': '09120002222', 'password': 'wrongpass'})

    # حالا ورود موفق
    response = client.post(url, {'phone': '09120002222', 'password': 'correctpass'})
    assert response.status_code == 200

    # داده‌های cache باید پاک شده باشه
    assert cache.get(_cache_key('09120002222')) is None
