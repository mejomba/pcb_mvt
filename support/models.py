from .storages import protected_media_storage
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import F

# هدف SLA برای اولین پاسخ، بر حسب ساعت و بر اساس اولویت
SLA_FIRST_RESPONSE_HOURS = {
    'urgent': 2,
    'high': 8,
    'normal': 24,
    'low': 72,
}


class TicketSequence(models.Model):
    """شمارنده‌ی سالانه برای تولید شماره‌ی یکتای تیکت."""
    year = models.PositiveIntegerField(unique=True)
    last_number = models.PositiveIntegerField(default=0)


def next_ticket_number():
    year = timezone.now().year
    with transaction.atomic():
        seq, _ = TicketSequence.objects.get_or_create(year=year)
        seq = TicketSequence.objects.select_for_update().get(pk=seq.pk)
        seq.last_number = F('last_number') + 1
        seq.save(update_fields=['last_number'])
        seq.refresh_from_db(fields=['last_number'])
    return f"TK-{year}-{seq.last_number:05d}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        IN_PROGRESS = 'in_progress', 'در حال بررسی'
        AWAITING_CUSTOMER = 'awaiting_customer', 'در انتظار پاسخ مشتری'
        AWAITING_SUPPORT = 'awaiting_support', 'در انتظار پاسخ پشتیبانی'
        RESOLVED = 'resolved', 'حل شده'
        CLOSED = 'closed', 'بسته شده'

    class Priority(models.TextChoices):
        LOW = 'low', 'کم'
        NORMAL = 'normal', 'عادی'
        HIGH = 'high', 'زیاد'
        URGENT = 'urgent', 'فوری'

    class Category(models.TextChoices):
        TECHNICAL = 'technical', 'فنی'
        BILLING = 'billing', 'مالی'
        SALES = 'sales', 'فروش'
        OTHER = 'other', 'سایر'

    subject = models.CharField('موضوع', max_length=200)
    status = models.CharField('وضعیت', max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField('اولویت', max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    category = models.CharField('دسته', max_length=20, choices=Category.choices, default=Category.OTHER)

    # اتصال جنریک به موجودیت مرتبط (سفارش و غیره)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets'
    )

    # فیلدهای ممیزی
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    creator_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticket_created'
    )
    editor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticket_edited'
    )
    number = models.CharField('شماره تیکت', max_length=20, unique=True,
                              null=True, blank=True, db_index=True)
    first_response_due = models.DateTimeField('مهلت اولین پاسخ', null=True, blank=True)
    first_response_at = models.DateTimeField('زمان اولین پاسخ', null=True, blank=True)

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-create_date']
        indexes = [models.Index(fields=['content_type', 'object_id'])]

    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.number:
                self.number = next_ticket_number()
            if self.first_response_due is None:
                hours = SLA_FIRST_RESPONSE_HOURS.get(self.priority, 24)
                self.first_response_due = timezone.now() + timedelta(hours=hours)
        super().save(*args, **kwargs)

    @property
    def is_sla_breached(self):
        if self.first_response_due is None:
            return False
        if self.first_response_at is not None:
            return self.first_response_at > self.first_response_due
        return timezone.now() > self.first_response_due


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='sent_ticket_messages'
    )
    body = models.TextField('متن پیام')
    is_internal = models.BooleanField('یادداشت داخلی', default=False)

    # فیلدهای ممیزی
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    creator_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticketmessage_created'
    )
    editor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticketmessage_edited'
    )

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام‌های تیکت'
        ordering = ['create_date']


class TicketAttachment(models.Model):
    message = models.ForeignKey(
        TicketMessage, on_delete=models.CASCADE, related_name='attachments'
    )
    file = models.FileField(
        'فایل', upload_to='ticket_attachments/%Y/%m/',
        storage=protected_media_storage,
    )
    original_name = models.CharField('نام فایل', max_length=255, blank=True)
    size = models.PositiveIntegerField('حجم (بایت)', default=0)
    mime_type = models.CharField('نوع فایل', max_length=100, blank=True)

    # فیلدهای ممیزی
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    creator_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticketattachment_created'
    )
    editor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
        related_name='ticketattachment_edited'
    )

    class Meta:
        verbose_name = 'پیوست تیکت'
        verbose_name_plural = 'پیوست‌های تیکت'
        ordering = ['create_date']


class Notification(models.Model):
    class Type(models.TextChoices):
        NEW_MESSAGE = 'new_message', 'پیام جدید'
        STATUS_CHANGED = 'status_changed', 'تغییر وضعیت'
        ASSIGNED = 'assigned', 'تخصیص تیکت'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(
        TicketMessage, on_delete=models.CASCADE, null=True, blank=True
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.NEW_MESSAGE)
    text = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-create_date']