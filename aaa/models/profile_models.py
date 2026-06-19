import datetime
from django.db import models
from django.core.validators import RegexValidator

# ولیدیتورهای مشترک
phone_validator = RegexValidator(
    r'^09\d{9}$', message='تلفن نا معتبر', code='invalid_phone'
)
postal_code_validator = RegexValidator(
    r'^\d{10}$', message='کد پستی باید ۱۰ رقم باشد', code='invalid_postal_code'
)
national_id_validator = RegexValidator(
    r'^\d{11}$', message='شناسه ملی باید ۱۱ رقم باشد', code='invalid_national_id'
)
national_code_validator = RegexValidator(
    r'^\d{10}$', message='کد ملی باید ۱۰ رقم باشد', code='invalid_national_code'
)


class Address(models.Model):
    user = models.ForeignKey(
        'CustomUser', on_delete=models.CASCADE, related_name='addresses'
    )
    title = models.CharField('عنوان', max_length=50, blank=True, null=True)
    province = models.CharField('استان', max_length=50)
    city = models.CharField('شهر', max_length=50)
    postal_code = models.CharField(
        'کد پستی', max_length=10, blank=True, null=True,
        validators=[postal_code_validator]
    )
    address = models.TextField('نشانی کامل')
    receiver_name = models.CharField('نام گیرنده', max_length=100, blank=True, null=True)
    receiver_phone = models.CharField(
        'تلفن گیرنده', max_length=11, blank=True, null=True,
        validators=[phone_validator]
    )
    is_default = models.BooleanField('پیش‌فرض', default=False)

    # فیلدهای ممیزی
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    creator_user = models.ForeignKey(
        'CustomUser', on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='address_created'
    )
    editor_user = models.ForeignKey(
        'CustomUser', on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='address_edited'
    )

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # تضمین یکتایی آدرس پیش‌فرض برای هر کاربر
        if self.is_default and not self.is_deleted:
            Address.objects.filter(
                user=self.user, is_default=True, is_deleted=False
            ).exclude(pk=self.pk).update(is_default=False)


class LegalProfile(models.Model):
    user = models.ForeignKey(
        'CustomUser', on_delete=models.CASCADE, related_name='legal_profiles'
    )

    # اطلاعات شخص حقوقی (شرکت)
    company_name = models.CharField('نام شرکت', max_length=150)
    national_id = models.CharField(
        'شناسه ملی', max_length=11, validators=[national_id_validator]
    )
    economic_code = models.CharField('کد اقتصادی', max_length=20, blank=True, null=True)
    registration_number = models.CharField('شماره ثبت', max_length=20, blank=True, null=True)
    legal_phone = models.CharField(
        'تلفن ثابت', max_length=11, blank=True, null=True
    )
    legal_address = models.TextField('نشانی قانونی', blank=True, null=True)

    # اطلاعات نماینده‌ی حقیقی
    rep_full_name = models.CharField('نام و نام خانوادگی نماینده', max_length=100)
    rep_national_code = models.CharField(
        'کد ملی نماینده', max_length=10, validators=[national_code_validator]
    )
    rep_phone = models.CharField(
        'تلفن نماینده', max_length=11, blank=True, null=True,
        validators=[phone_validator]
    )
    rep_position = models.CharField('سمت نماینده', max_length=50, blank=True, null=True)

    # فیلدهای ممیزی
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    creator_user = models.ForeignKey(
        'CustomUser', on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='legalprofile_created'
    )
    editor_user = models.ForeignKey(
        'CustomUser', on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='legalprofile_edited'
    )

    class Meta:
        verbose_name = 'پروفایل حقوقی'
        verbose_name_plural = 'پروفایل‌های حقوقی'