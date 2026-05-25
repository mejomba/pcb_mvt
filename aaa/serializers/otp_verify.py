from rest_framework import serializers
from aaa.models.otp import OTP
from aaa.models.user_models import CustomUser
from aaa.utils.auth_throttle import is_blocked, register_failed_attempt, reset_attempts


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs['phone']
        code = attrs['code']

        if is_blocked(phone):
            raise serializers.ValidationError("Too many failed attempts. Try again later.")

        try:
            otp = OTP.objects.filter(phone=phone, code=code, is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            register_failed_attempt(phone)
            raise serializers.ValidationError("Invalid or expired OTP.")

        if otp.is_expired():
            register_failed_attempt(phone)
            raise serializers.ValidationError("OTP has expired.")

        attrs['otp'] = otp
        return attrs

    def create(self, validated_data):
        otp = validated_data['otp']
        otp.is_used = True
        otp.save()

        reset_attempts(otp.phone)
        user, created = CustomUser.objects.get_or_create(phone=otp.phone)
        return user
