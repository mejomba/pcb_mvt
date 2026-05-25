# aaa/views/otp_login.py
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from aaa.models import CustomUser
from aaa.models.otp import OTP
from rest_framework_simplejwt.tokens import RefreshToken

from aaa.serializers.auth_signup import SignupSerializer
from aaa.utils.jwt_tokens import generate_jwt_response


class OtpLoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # غیرفعال کردن JWT برای این endpoint

    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')

        if not phone or not code:
            return Response({'detail': 'phone and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp = OTP.objects.get(phone=phone, code=code, is_used=False)
        except OTP.DoesNotExist:
            return Response({'detail': 'کد وارد شده نادرست است.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp.expires_at < timezone.now():
            return Response({'detail': 'کد منقضی شده است.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'کاربری با این شماره وجود ندارد.'}, status=status.HTTP_404_NOT_FOUND)

        otp.is_used = True
        otp.save()

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_200_OK)

        xponse.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],  # usually 'refresh_token'
            value=str(refresh),
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['AUTH_COOKIE_MAX_AGE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
            domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
        )
        xponse.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_ACCESS'],  # usually 'access_token'
            value=str(access),
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['AUTH_COOKIE_MAX_AGE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
            domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
        )
        return xponse