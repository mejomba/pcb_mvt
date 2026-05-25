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