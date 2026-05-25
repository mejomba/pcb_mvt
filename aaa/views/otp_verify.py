from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from aaa.serializers.otp_verify import OTPVerifySerializer
from aaa.serializers.auth_signup import SignupSerializer
from aaa.utils.jwt_tokens import generate_jwt_response


@method_decorator(csrf_exempt, name="dispatch")
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # غیرفعال کردن JWT برای این endpoint

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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
                key=settings.SIMPLE_JWT['AUTH_ACCESS'],  # usually 'refresh_token'
                value=str(access),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['AUTH_COOKIE_MAX_AGE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
                domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
            )
            return xponse
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
