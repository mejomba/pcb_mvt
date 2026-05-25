from django.conf import settings
from rest_framework import serializers, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from aaa.models.user_models import CustomUser
from aaa.serializers.auth_signup import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from aaa.utils.jwt_tokens import generate_jwt_response
import re


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), phone=phone, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        data = super().validate(attrs)
        data['user'] = {
            'id': user.id,
            'phone': user.phone
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone'] = user.phone
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class PhoneCheckAPIView(APIView):
    phone_pattern = r'^09\d{9}$'

    def post(self, request):
        phone = request.data.get('phone')
        method = request.data.get('method')  # values: "password" or "otp"

        if not phone or not method:
            return Response({'detail': 'phone and method are required.'}, status=400)

        if not re.match(self.phone_pattern, phone):
            raise ValueError("phone number is not valid format")

        try:
            user = CustomUser.objects.get(phone=phone)
            exists = True
        except CustomUser.DoesNotExist:
            user = None
            exists = False

        return Response({
            'exists': exists,
            'method': method,
            'next_step': self.get_next_step(exists, method)
        })

    def get_next_step(self, exists, method):
        if method == 'password':
            return 'login' if exists else 'register'
        elif method == 'otp':
            return 'login' if exists else 'register'
        return 'unknown'


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_201_CREATED)
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
