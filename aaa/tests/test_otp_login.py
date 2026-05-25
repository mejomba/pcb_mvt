import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from aaa.models import CustomUser, OTP
from datetime import timedelta


@pytest.mark.django_db
class TestOtpLogin:
    endpoint = reverse('auth:otp-login')

    def test_successful_login(self):
        user = CustomUser.objects.create_user(phone='09120000001', password='test1234')
        otp = OTP.objects.create(
            phone=user.phone,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        client = APIClient()
        response = client.post(self.endpoint, data={
            'phone': user.phone,
            'code': otp.code
        })

        assert response.status_code == 200
        data = response.json()
        assert 'access' in data and 'refresh' in response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key
        assert data['user']['phone'] == user.phone
        otp.refresh_from_db()
        assert otp.is_used is True

    def test_invalid_code(self):
        CustomUser.objects.create_user(phone='09120000002', password='test1234')
        OTP.objects.create(
            phone='09120000002',
            code='654321',
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        client = APIClient()
        response = client.post(self.endpoint, data={
            'phone': '09120000002',
            'code': 'wrongcode'
        })

        assert response.status_code == 400
        assert response.data['detail'] == 'کد وارد شده نادرست است.'

    def test_expired_code(self):
        CustomUser.objects.create_user(phone='09120000003', password='test1234')
        OTP.objects.create(
            phone='09120000003',
            code='222222',
            expires_at=timezone.now() - timedelta(minutes=1),
            is_used=False
        )

        client = APIClient()
        response = client.post(self.endpoint, data={
            'phone': '09120000003',
            'code': '222222'
        })

        assert response.status_code == 400
        assert response.data['detail'] == 'کد منقضی شده است.'

    def test_user_not_found(self):
        OTP.objects.create(
            phone='09120009999',
            code='999999',
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        client = APIClient()
        response = client.post(self.endpoint, data={
            'phone': '09120009999',
            'code': '999999'
        })

        assert response.status_code == 404
        assert response.data['detail'] == 'کاربری با این شماره وجود ندارد.'

    def test_missing_fields(self):
        client = APIClient()
        response = client.post(self.endpoint, data={})

        assert response.status_code == 400
        assert 'detail' in response.data
