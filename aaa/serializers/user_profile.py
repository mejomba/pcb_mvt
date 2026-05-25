from rest_framework import serializers
from aaa.models.user_models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'phone',
                  'full_name',
                  'email',
                  'gender',
                  'birth_date',
                  'avatar',
                  ]
        read_only_fields = ['id', 'phone', 'full_name']
