from datetime import timedelta

from django.urls import reverse
from rest_framework.test import APITestCase
from django.utils import timezone
from aaa.models.otp import OTP


class ResendOTPTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth:resend-otp')
        self.phone = "+989123456789"

    def test_resend_otp_success(self):
        response = self.client.post(self.url, {"phone": self.phone})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "OTP sent successfully.")
        self.assertTrue(OTP.objects.filter(phone=self.phone).exists())

    def test_resend_otp_without_phone(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    def test_resend_otp_too_soon(self):
        OTP.objects.create(phone=self.phone, code="123456", expires_at=timezone.now() + timedelta(minutes=2), created_at=timezone.now())
        response = self.client.post(self.url, {"phone": self.phone})
        self.assertEqual(response.status_code, 429)
