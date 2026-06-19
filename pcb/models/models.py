from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from blog.models import Post
from core.models import AbstractCommWithUserModel


class AttributeGroup(models.Model):
    """
    گروهی برای دسته‌بندی ویژگی‌ها، مانند 'مشخصات PCB'.
    """
    file = models.FileField(upload_to='uploads/attribute_group/image/', blank=True, null=True)
    name = models.CharField(max_length=100, unique=True, help_text="نام سیستمی و انگلیسی (مثال: pcb_specifications)")
    display_name = models.CharField(max_length=255, help_text="نام نمایشی برای کاربر (مثال: مشخصات PCB)")
    display_order = models.PositiveIntegerField(default=0, help_text="ترتیب نمایش گروه")

    class Meta:
        verbose_name = "گروه ویژگی"
        verbose_name_plural = "گروه‌های ویژگی"
        ordering = ['display_order']

    def __str__(self):
        return self.display_name


class Attribute(models.Model):
    """
    یک ویژگی خاص از محصول که قابل تنظیم است، مانند 'رنگ برد' یا 'ضخامت'.
    """
    class ControlType(models.TextChoices):
        TEXT_INPUT = 'text_input', 'ورودی متنی/عددی'
        RADIO_BUTTON = 'radio_button', 'دکمه رادیویی'
        SELECT_BOX = 'select_box', 'لیست کشویی'
        COLOR_PICKER = 'color_picker', 'انتخابگر رنگ'

    file = models.FileField(upload_to='uploads/attribute/image/', blank=True, null=True)
    guid = models.ForeignKey(Post, on_delete=models.DO_NOTHING, related_name='guids', null=True, blank=True)
    group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attributes',
        verbose_name="گروه ویژگی"
    )
    name = models.CharField(max_length=100, unique=True, help_text="نام سیستمی (مثال: pcb_color)")
    display_name = models.CharField(max_length=255, help_text="نام نمایشی (مثال: رنگ برد)")
    control_type = models.CharField(
        max_length=20,
        choices=ControlType.choices,
        default=ControlType.RADIO_BUTTON,
        verbose_name="نوع کنترل در فرم"
    )
    display_order = models.PositiveIntegerField(default=0, help_text="ترتیب نمایش ویژگی در گروه")

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ['group__display_order', 'display_order']

    def __str__(self):
        return f"{self.display_name} ({self.group.display_name if self.group else 'بدون گروه'})"


class AttributeOption(models.Model):
    """
    یک گزینه یا مقدار ممکن برای یک ویژگی، مانند 'سبز' برای 'رنگ برد'.
    """
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="ویژگی مربوطه"
    )
    value = models.CharField(max_length=100, help_text="مقدار واقعی (مثال: #008000 یا 1.6mm)")
    display_name = models.CharField(max_length=255, help_text="نام نمایشی (مثال: سبز)")
    is_default = models.BooleanField(default=False, verbose_name="گزینه پیش‌فرض؟")
    display_order = models.PositiveIntegerField(default=0, help_text="ترتیب نمایش گزینه")
    file = models.FileField(upload_to='uploads/attribute/image/', blank=True, null=True)

    class Meta:
        verbose_name = "گزینه ویژگی"
        verbose_name_plural = "گزینه‌های ویژگی"
        ordering = ['display_order']
        unique_together = ('attribute', 'value') # هر گزینه برای یک ویژگی باید یکتا باشد

    def __str__(self):
        return f"{self.attribute.group.display_name} - {self.attribute.display_name} - {self.display_name}"


class Order(models.Model):
    """
    اطلاعات کلی یک سفارش ثبت‌شده توسط کاربر را نگهداری می‌کند.
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'در انتظار بررسی'
        QUOTATION = 'quotation', 'پیش فاکتور شده (در انتظار پرداخت)'
        PROCESS = 'process', 'در حال ساخت'
        PENDING_DELIVERY = 'pending_delivery', 'در انتظار تحویل'
        DELIVER = 'deliver', 'تحویل شده'
        CANCELED = 'canceled', 'لغو شده'

    file = models.FileField(upload_to='uploads/orders/files/', blank=True, null=True)
    quotation = models.FileField(upload_to='uploads/orders/quotation/files/', blank=True, null=True)
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    download_count = models.PositiveSmallIntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # اگر کاربر حذف شد، سفارش باقی بماند
        null=True,
        blank=True,
        verbose_name="کاربر"
    )
    # quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="وضعیت سفارش"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    part_number = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش شماره {self.id} توسط {self.user}"


class OrderSelection(models.Model):
    """
    هر ردیف در این جدول، یک انتخاب کاربر برای یک ویژگی خاص در یک سفارش مشخص است.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE, # اگر سفارش حذف شد، انتخاب‌ها هم حذف شوند
        related_name='selections',
        verbose_name="سفارش"
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT, # از حذف ویژگی‌ای که در سفارش‌ها استفاده شده جلوگیری می‌کند
        verbose_name="ویژگی"
    )
    # اگر کاربر یک گزینه از پیش تعریف‌شده را انتخاب کند، اینجا ذخیره می‌شود
    selected_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="گزینه انتخابی"
    )
    # اگر کاربر مقداری را دستی وارد کند (مثل ابعاد)، اینجا ذخیره می‌شود
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="مقدار وارد شده"
    )

    class Meta:
        verbose_name = "گزینه انتخابی سفارش"
        verbose_name_plural = "گزینه‌های انتخابی سفارش"
        # هر ویژگی فقط یک بار می‌تواند برای هر سفارش انتخاب شود
        unique_together = ('order', 'attribute')

    def __str__(self):
        display_value = self.selected_option.display_name if self.selected_option else self.value
        return f"{self.attribute.display_name}: {display_value}"


class OrderPayment(AbstractCommWithUserModel):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='payments')
    file = models.FileField(upload_to='uploads/orders/payment/files/', blank=True, null=True)


class OrderReadOnly(Order):
    class Meta:
        proxy = True
        verbose_name = "Order (View Only)"
        verbose_name_plural = "Orders (View Only)"


class ConditionalRule(models.Model):
    """
    این مدل یک قانون شرطی را تعریف می‌کند.
    IF trigger_option is selected, THEN perform action_type ON target_object.
    """

    class ActionType(models.TextChoices):
        DISABLE = 'disable', 'غیرفعال کردن (Disable)'
        HIDE = 'hide', 'مخفی کردن (Hide)'
        ENABLE = 'enable', 'فعال کردن (Enable)'
        SHOW = 'show', 'نمایش دادن (Show)'

    name = models.CharField(max_length=255, help_text="یک نام توصیفی برای این قانون")

    # بخش IF: شرطی که قانون را فعال می‌کند
    trigger_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        related_name='triggered_rules',
        verbose_name="گزینه فعال‌کننده"
    )

    # بخش THEN: عملی که باید انجام شود
    action_type = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        verbose_name="نوع عمل"
    )

    # بخش ON: هدفی که عمل روی آن انجام می‌شود (با استفاده از Generic Foreign Key)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="نوع مدل هدف"
    )
    target_object_id = models.PositiveIntegerField(verbose_name="شناسه آبجکت هدف")
    target_object = GenericForeignKey('target_content_type', 'target_object_id')

    class Meta:
        verbose_name = "قانون شرطی"
        verbose_name_plural = "قوانین شرطی"

    def __str__(self):
        return f"اگر '{self.trigger_option}' انتخاب شد، آنگاه هدف را '{self.get_action_type_display()}' کن"