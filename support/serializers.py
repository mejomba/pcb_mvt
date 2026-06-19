from django.urls import reverse
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Ticket, TicketMessage, TicketAttachment
from .models import Notification  # به importها اضافه کن


ALLOWED_TICKET_TARGETS = {
    'pcb.order': 'user',  # ⚠️ نام فیلد مالک را مطابق مدل Order خودت تنظیم کن
}

# محدودیت‌های پیوست
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # ۱۰ مگابایت
ALLOWED_ATTACHMENT_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf',
    'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip', 'rar',
]


def validate_attachment(f):
    if f.size > MAX_ATTACHMENT_SIZE:
        raise serializers.ValidationError(
            f"حجم فایل «{f.name}» بیش از حد مجاز ({MAX_ATTACHMENT_SIZE // (1024*1024)}MB) است."
        )
    ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise serializers.ValidationError(f"پسوند «{ext}» مجاز نیست.")
    return f


def create_attachments(message, files, user):
    """ساخت رکورد پیوست برای هر فایل (به‌صورت create تا فایل واقعاً ذخیره شود)."""
    for f in files:
        TicketAttachment.objects.create(
            message=message,
            file=f,
            original_name=(f.name or '')[:255],
            size=getattr(f, 'size', 0) or 0,
            mime_type=(getattr(f, 'content_type', '') or '')[:100],
            creator_user=user,
        )


def resolve_related(related_type, related_id, user):
    if related_type is None and related_id is None:
        return None, None
    if (related_type is None) != (related_id is None):
        raise serializers.ValidationError(
            {"related": "برای اتصال، هم نوع و هم شناسه‌ی موجودیت لازم است."}
        )

    key = related_type.lower()
    if key not in ALLOWED_TICKET_TARGETS:
        raise serializers.ValidationError(
            {"related_type": f"اتصال به «{related_type}» مجاز نیست."}
        )

    app_label, model = key.split('.')
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        raise serializers.ValidationError({"related_type": "نوع موجودیت نامعتبر است."})

    obj = ct.model_class().objects.filter(pk=related_id).first()
    if obj is None:
        raise serializers.ValidationError({"related_id": "موجودیت مورد نظر یافت نشد."})

    if not user.is_staff:
        owner_field = ALLOWED_TICKET_TARGETS[key]
        if getattr(obj, owner_field, None) != user:
            raise serializers.ValidationError({"related_id": "این مورد به شما تعلق ندارد."})

    return ct, related_id


class TicketAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = ['id', 'url', 'original_name', 'size', 'mime_type', 'create_date']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        url = reverse('support:attachment-download', kwargs={'pk': obj.id})
        return request.build_absolute_uri(url) if request else url


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = ['id', 'sender', 'sender_name', 'body', 'is_internal',
                  'attachments', 'create_date']
        read_only_fields = fields

    @extend_schema_field(TicketAttachmentSerializer(many=True))
    def get_attachments(self, obj):
        qs = obj.attachments.filter(is_deleted=False)
        return TicketAttachmentSerializer(qs, many=True, context=self.context).data


class TicketMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    is_internal = serializers.BooleanField(required=False, default=False)
    files = serializers.ListField(
        child=serializers.FileField(validators=[validate_attachment]),
        required=False, write_only=True,
    )


class TicketListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    is_sla_breached = serializers.BooleanField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'priority', 'category',
                  'assignee', 'message_count', 'create_date', 'update_date',
                  'number', 'first_response_due', 'first_response_at', 'is_sla_breached']

    @extend_schema_field(serializers.IntegerField)
    def get_message_count(self, obj):
        return obj.messages.filter(is_deleted=False).count()


class TicketDetailSerializer(serializers.ModelSerializer):
    related = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    is_sla_breached = serializers.BooleanField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'status', 'priority', 'category',
                  'assignee', 'related', 'messages', 'create_date', 'update_date',
                  'number', 'first_response_due', 'first_response_at', 'is_sla_breached']

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_related(self, obj):
        if not obj.content_type_id or obj.related_object is None:
            return None
        return {
            'type': f'{obj.content_type.app_label}.{obj.content_type.model}',
            'id': obj.object_id,
            'display': str(obj.related_object),
        }

    @extend_schema_field(TicketMessageSerializer(many=True))
    def get_messages(self, obj):
        request = self.context.get('request')
        qs = obj.messages.filter(is_deleted=False)
        if not (request and request.user.is_staff):
            qs = qs.filter(is_internal=False)
        return TicketMessageSerializer(qs, many=True, context=self.context).data


class TicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200)
    priority = serializers.ChoiceField(
        choices=Ticket.Priority.choices, default=Ticket.Priority.NORMAL
    )
    category = serializers.ChoiceField(
        choices=Ticket.Category.choices, default=Ticket.Category.OTHER
    )
    message = serializers.CharField()
    related_type = serializers.CharField(required=False, allow_null=True)
    related_id = serializers.IntegerField(required=False, allow_null=True)
    files = serializers.ListField(
        child=serializers.FileField(validators=[validate_attachment]),
        required=False, write_only=True,
    )

    def validate(self, attrs):
        user = self.context['request'].user
        ct, obj_id = resolve_related(
            attrs.get('related_type'), attrs.get('related_id'), user
        )
        attrs['_content_type'] = ct
        attrs['_object_id'] = obj_id
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        files = validated_data.get('files', [])
        ticket = Ticket.objects.create(
            subject=validated_data['subject'],
            priority=validated_data['priority'],
            category=validated_data['category'],
            content_type=validated_data['_content_type'],
            object_id=validated_data['_object_id'],
            status=Ticket.Status.AWAITING_SUPPORT,
            creator_user=user,
        )
        message = TicketMessage.objects.create(
            ticket=ticket, sender=user, body=validated_data['message'],
            is_internal=False, creator_user=user,
        )
        create_attachments(message, files, user)
        return ticket


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'category', 'assignee']

    def validate_assignee(self, value):
        if value is not None and not value.is_staff:
            raise serializers.ValidationError("مسئول باید کارشناس پشتیبانی باشد.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    ticket_number = serializers.CharField(source='ticket.number', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'text', 'ticket', 'ticket_number', 'message',
                  'is_read', 'read_date', 'create_date']
        read_only_fields = fields