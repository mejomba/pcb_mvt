# === aaa/admin.py ===
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from aaa.models import CustomUser
from aaa.forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # فرم‌های سفارشی
    form     = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # لیست
    list_display = ("id", "phone", "email", "full_name", "is_staff", "date_joined")
    list_filter  = ("is_staff", "is_superuser", "is_active", "is_special", "is_deleted")
    search_fields = ("id", "phone", "full_name", "email")
    ordering = ("id",)          # ⚠️ مهم: نباید username باشه (وجود نداره)

    # full_name و فیلدهای auto فقط خواندنی
    readonly_fields = ("full_name", "last_login", "date_joined", "update_date")

    # فرم ویرایش — جایگزین username با phone
    fieldsets = (
        (None,                {"fields": ("phone", "password")}),
        ("اطلاعات شخصی",      {"fields": ("first_name", "last_name", "full_name",
                                          "email", "gender", "birth_date", "avatar")}),
        ("دسترسی‌ها",         {"fields": ("is_active", "is_staff", "is_superuser",
                                          "is_special", "groups", "user_permissions")}),
        ("تاریخ‌های مهم",     {"fields": ("last_login", "date_joined", "update_date")}),
        ("حذف",               {"fields": ("is_deleted", "delete_date")}),
    )

    # فرم افزودن کاربر جدید
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "password2"),
        }),
    )