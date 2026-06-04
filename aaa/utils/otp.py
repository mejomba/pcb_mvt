import random
from typing import List

import requests
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from aaa.models.otp import OTP


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class OTPAction:
    email_backend = None
    phone_backend = None

    @staticmethod
    def _send_email(message: str, emails: List):
        print(emails, message)

    @staticmethod
    def _send_sms(message: str, phones: List):
        for phone in phones:
            import json
            json_data = json.dumps({
                                    "mobile": phone,
                                    "templateId": 485441,
                                    "parameters": [
                                      {
                                        "name": "Code",
                                        "value": message
                                      }
                                    ]
                                })
            # headers = {"X-API-KEY": "YfBVq1GRodeKKzWnMH7S7odrZ8ENxSjsop7dgfxgJXa7G9ay"}
            headers = {"X-API-KEY": "8hNXrAanJnZ9ZBF48EQwuUCmaR1C4GVhjU58b4Oq5eTfvfRc"}
            res = requests.post('https://api.sms.ir/v1/send/verify', json=json_data, headers=headers)
            print(phones, message)

    @staticmethod
    def cache_in_redis(otp_code, user):
        pass
        # cache.set(otp_code, user.id, CACHE_TTL)

    @staticmethod
    def _generate_otp(destination):
        code = str(random.randint(10000, 99999))
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_LIFE_TIME)

        otp = OTP.objects.create(
            phone=destination,
            code=code,
            expires_at=expires_at
        )
        # در عمل باید پیامک یا ایمیل ارسال بشه؛ فعلاً فقط چاپش می‌کنیم:
        print(f"[OTP] Code for {otp.phone}: {otp.code}")
        # utils.send_otp()
        return otp

    @classmethod
    def _get_backend(cls, backend):
        backend = backend.lower()
        if backend == "email":
            return cls._send_email
        elif backend == "sms":
            return cls._send_sms

        return print

    @classmethod
    def perform_otp(cls, destination, backend: str):
        otp = cls._generate_otp(destination)
        sender = cls._get_backend(backend)  # email or sms
        sender(otp.code, [destination])
        return otp
