from rest_framework import serializers
from aaa.models.user_models import CustomUser


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone']


class CustomUserSerializer(serializers.ModelSerializer):
    creator_user = ShortUserSerializer(read_only=True)
    editor_user = ShortUserSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phone',
            'update_date',
            'is_deleted',
            'delete_date',
            'is_special',
            'creator_user',
            'editor_user'
        ]

        read_only_fields = ['update_date', 'delete_date']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'password', 'creator_user']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserAsAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'full_name',
            'avatar',
        ]

        read_only_fields = ['full_name', 'avatar']


from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "رمز عبور و تکرار آن یکسان نیستند."}
            )

        # اعتبارسنجی قدرت رمز با ولیدیتورهای جنگو
        user = self.context['request'].user
        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs