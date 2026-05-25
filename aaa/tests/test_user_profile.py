import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from aaa.models.user_models import CustomUser


@pytest.mark.django_db
def test_get_user_profile():
    user = CustomUser.objects.create_user(phone='0912XXXXXXX', password='pass123')
    client = APIClient()
    client.force_authenticate(user)
    url = reverse('auth:auth_profile')

    response = client.get(url)
    assert response.status_code == 200
    assert response.data['phone'] == user.phone


@pytest.mark.django_db
def test_update_user_profile():
    user = CustomUser.objects.create_user(phone='0912XXXXXXX', password='pass123')
    client = APIClient()
    client.force_authenticate(user)
    url = reverse('auth:auth_profile')

    data = {
        'first_name': 'Ali',
        'last_name': 'Testi',
        'email': 'ali@example.com',
        'gender': 'male'
    }
    response = client.patch(url, data, format='json')
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.full_name == 'Ali Testi'


@pytest.mark.django_db
def test_full_name_auto_updates():
    user = CustomUser.objects.create_user(
        phone='0912XXXXXXX', password='pass123',
        first_name='Ali', last_name='Test'
    )
    assert user.full_name == 'Ali Test'

    user.first_name = 'Reza'
    user.last_name = 'Taj'
    user.save()

    assert user.full_name == 'Reza Taj'
