from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from aaa.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

from aaa.serializers.auth_signup import SignupSerializer
from aaa.utils.jwt_tokens import generate_jwt_response


class PasswordLoginOrSignupView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        created = None

        if not phone or not password:
            return Response({"error": "Phone and password are required."}, status=400)

        try:
            user = CustomUser.objects.get(phone=phone)
            if not user.has_usable_password():
                return Response({"error": "This account uses OTP login. Cannot use password."}, status=400)

            user = authenticate(request, phone=phone, password=password)
            if not user:
                return Response({"error": "Invalid password."}, status=401)

        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.create_user(phone=phone, password=password)
                created = True
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        refresh = RefreshToken.for_user(user)

        if created:
            xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_201_CREATED)
        else:
            xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_200_OK)

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
