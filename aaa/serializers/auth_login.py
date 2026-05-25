from rest_framework import serializers
from django.contrib.auth import authenticate

from aaa.utils.auth_throttle import is_blocked, reset_attempts, register_failed_attempt


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not phone or not password:
            raise serializers.ValidationError("Phone and password are required.")

        print('before block...')
        if is_blocked(phone):
            print('block...')
            raise serializers.ValidationError("Too many failed attempts. Try again later.")
        print('after block...')

        user = authenticate(phone=phone, password=password)

        if not user:
            register_failed_attempt(phone)
            raise serializers.ValidationError("Invalid phone or password.")

        reset_attempts(phone)
        attrs['user'] = user
        return attrs
