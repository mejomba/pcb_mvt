# users/tests/test_managers.py

import pytest
from aaa.models.user_models import CustomUser


@pytest.mark.django_db
def test_create_user_with_phone():
    user = CustomUser.objects.create_user(phone="09121234567", password="securepass")

    assert user.phone == "09121234567"
    assert user.check_password("securepass")
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser():
    admin = CustomUser.objects.create_superuser(phone="09121111111", password="adminpass")

    assert admin.phone == "09121111111"
    assert admin.is_superuser is True
    assert admin.is_staff is True


@pytest.mark.django_db
def test_create_user_without_phone_raises_error():
    with pytest.raises(ValueError) as exc:
        CustomUser.objects.create_user(phone=None, password="test")

    assert "Phone number is required" in str(exc.value)


@pytest.mark.django_db
def test_create_superuser_without_flags_raises_error():
    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(phone="09123334455", password="admin", is_staff=False)

    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(phone="09123334455", password="admin", is_superuser=False)
