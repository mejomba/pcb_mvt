# === aaa/forms.py ===
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from aaa.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """فرم افزودن کاربر — با password1 / password2"""
    class Meta:
        model = CustomUser
        fields = ('phone',)   # به‌جای username


class CustomUserChangeForm(UserChangeForm):
    """
    فرم ویرایش کاربر — فیلد password از نوع ReadOnlyPasswordHashField
    همون رفتار قبلی (نمایش هش + لینک تغییر رمز) رو می‌ده
    """
    class Meta:
        model = CustomUser
        fields = '__all__'