from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from aaa.models import CustomUser


class PasswordLoginOrSignupTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth:password-login-or-signup')
        self.phone = "+989123456789"
        self.password = "secret123"

    def test_signup_new_user_with_password(self):
        response = self.client.post(self.url, {"phone": self.phone, "password": self.password})
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].key)
        self.assertTrue(CustomUser.objects.filter(phone=self.phone).exists())

    def test_login_existing_user_with_password(self):
        user = CustomUser.objects.create_user(phone=self.phone, password=self.password)
        response = self.client.post(self.url, {"phone": self.phone, "password": self.password})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_error_for_wrong_password(self):
        user = CustomUser.objects.create_user(phone=self.phone, password="correctpass")
        response = self.client.post(self.url, {"phone": self.phone, "password": "wrongpass"})
        self.assertEqual(response.status_code, 401)

    def test_error_for_otp_only_account(self):
        user = CustomUser.objects.create(phone=self.phone)
        user.set_unusable_password()
        user.save()
        response = self.client.post(self.url, {"phone": self.phone, "password": "somepass"})
        self.assertEqual(response.status_code, 400)
