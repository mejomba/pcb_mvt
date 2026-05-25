# aaa/views/auth/otp_register.py
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from aaa.models import CustomUser
from aaa.models.otp import OTP
from aaa.serializers.auth_signup import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from aaa.utils.jwt_tokens import generate_jwt_response


class OtpRegisterAPIView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')

        if not phone or not code:
            return Response({'detail': 'phone and code are required.'}, status=400)

        try:
            otp = OTP.objects.get(phone=phone, code=code, is_used=False)
        except OTP.DoesNotExist:
            return Response({'detail': 'کد وارد شده معتبر نیست.'}, status=400)

        if otp.expires_at < timezone.now():
            return Response({'detail': 'کد منقضی شده است.'}, status=400)

        if CustomUser.objects.filter(phone=phone).exists():
            return Response({'detail': 'کاربر از قبل وجود دارد.'}, status=400)

        # ایجاد کاربر
        user = CustomUser.objects.create_user(phone=phone)
        otp.is_used = True
        otp.save()

        refresh = RefreshToken.for_user(user)

        xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_201_CREATED)

        xponse.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],  # usually 'refresh_token'
            value=str(refresh),
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['AUTH_COOKIE_MAX_AGE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
        )
        return xponse
