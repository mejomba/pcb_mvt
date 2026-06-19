from rest_framework import serializers
from aaa.models.user_models import CustomUser
from aaa.models.profile_models import Address, LegalProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'phone',
                  'full_name',
                  'first_name',
                  'email',
                  'gender',
                  'birth_date',
                  'avatar',
                  ]
        read_only_fields = ['id', 'phone', 'full_name']


# فیلدهایی که کاربر نباید مستقیم تنظیم کند
AUDIT_READ_ONLY = (
    'create_date', 'update_date', 'is_deleted', 'delete_date',
    'creator_user', 'editor_user', 'user',
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = AUDIT_READ_ONLY


class LegalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalProfile
        fields = '__all__'
        read_only_fields = AUDIT_READ_ONLY
