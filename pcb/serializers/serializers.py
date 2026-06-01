import json

from django.utils import safestring
from rest_framework import serializers

from blog.serializers import GuidPostContentSerializer
from ..models.models import (AttributeGroup, Attribute, AttributeOption,
                     ConditionalRule, Order, OrderSelection)


class AttributeOptionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    """
    سریالایزر برای مدل گزینه‌ها
    """
    class Meta:
        model = AttributeOption
        # تمام فیلدهای مدل را شامل می‌شود
        fields = ['id', 'attribute', 'value', 'display_name', 'is_default', 'display_order', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class AttributeSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل ویژگی‌ها به همراه گزینه‌های زیرمجموعه‌اش
    """
    # نمایش گزینه‌های مربوط به هر ویژگی به صورت تودرتو (Nested)
    options = AttributeOptionSerializer(many=True, read_only=True)
    # guid = serializers.SerializerMethodField('get_guid_str')
    guid = GuidPostContentSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['id', 'group', 'name', 'display_name', 'control_type', 'display_order', 'options', 'file_url',
                  'guid']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    # def get_guid_str(self, obj):
    #     content = obj.guid.content if obj.guid else ''
    #     return safestring.mark_safe(content)
        # return content


class AttributeGroupSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل گروه‌ها به همراه ویژگی‌های زیرمجموعه‌اش
    """
    # نمایش ویژگی‌های مربوط به هر گروه به صورت تودرتو
    attributes = AttributeSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = AttributeGroup
        fields = ['id', 'name', 'display_name', 'display_order', 'attributes', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ConditionalRuleSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل قوانین شرطی، با فرمتی ساده برای فرانت‌اند.
    """
    # نام مدل هدف را به صورت یک رشته ساده برمی‌گردانیم (مثال: 'attribute' یا 'option')
    target_type = serializers.CharField(source='target_content_type.model', read_only=True)

    class Meta:
        model = ConditionalRule
        fields = [
            'id',
            'trigger_option',  # شناسه گزینه‌ای که شرط را فعال می‌کند
            'action_type',     # نوع عمل: 'disable', 'hide', 'enable', 'show'
            'target_type',     # نوع هدف: 'attributegroup', 'attribute', 'attributeoption'
            'target_object_id' # شناسه هدف
        ]


class OrderSelectionSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.display_name', read_only=True)
    selected_option_name = serializers.CharField(source='selected_option.display_name', read_only=True)

    class Meta:
        model = OrderSelection
        fields = [
            'id',
            'attribute',
            'attribute_name',
            'selected_option',
            'selected_option_name',
            'value',
        ]


# OrderSerializer (نسخه نهایی و امن)
class OrderSerializer(serializers.ModelSerializer):
    selections = OrderSelectionSerializer(many=True, required=False, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    quotation_url = serializers.SerializerMethodField(allow_null=True)
    payments_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_name',
            # 'quantity',
            'status',
            'created_at',
            'updated_at',
            'selections',
            'file',
            'file_url',
            'quotation',
            'quotation_url',
            'payments_urls',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_payments_urls(self, obj):
        return [p.file.url for p in obj.payments.all() if p.file]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url) if obj.file else None
        return None

    def get_quotation_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.quotation.url) if obj.quotation else None
        return None

    def _validate_and_process_selections(self, order_instance, selections_str):
        """یک متد کمکی برای اعتبارسنجی و ایجاد/آپدیت selections"""
        if selections_str is None:
            return

        try:
            selections_data = json.loads(selections_str)
            if not isinstance(selections_data, list):
                raise serializers.ValidationError({'selections': 'Expected a list of items.'})
        except json.JSONDecodeError:
            raise serializers.ValidationError({'selections': 'Invalid JSON format.'})

        # ✅ مرحله اعتبارسنجی دستی
        selection_serializer = OrderSelectionSerializer(data=selections_data, many=True)
        selection_serializer.is_valid(raise_exception=True)  # اگر نامعتبر باشد، خطا برمی‌گرداند

        # اگر متد برای آپدیت استفاده می‌شود، موارد قبلی را حذف کن
        if self.instance:
            order_instance.selections.all().delete()

        # ذخیره داده‌های اعتبارسنجی شده
        # for selection_validated_data in selection_serializer.validated_data:
        #     OrderSelection.objects.create(order=order_instance, **selection_validated_data)

        # 1. یک لیست خالی برای نگهداری آبجکت‌های جدید بسازید
        selections_to_create = []

        # 2. در حلقه، فقط آبجکت‌ها را بسازید (بدون ذخیره در دیتابیس) و به لیست اضافه کنید
        for selection_validated_data in selection_serializer.validated_data:
            selections_to_create.append(
                OrderSelection(order=order_instance, **selection_validated_data)
            )

        # 3. پس از پایان حلقه، همه آبجکت‌ها را با یک کوئری در دیتابیس ایجاد کنید
        if selections_to_create:
            OrderSelection.objects.bulk_create(selections_to_create)

    def create(self, validated_data):
        uploaded_file = self.context['request'].FILES.get('file')

        # اگر فایلی وجود داشت، نام اصلی را در validated_data قرار بده
        if uploaded_file:
            validated_data['original_filename'] = uploaded_file.name  # 👈 این خط مهم است

        selections_str = self.initial_data.get('selections')

        # ابتدا آبجکت اصلی Order را ایجاد می‌کنیم
        order = Order.objects.create(**validated_data)

        # سپس selections را با استفاده از متد کمکی پردازش می‌کنیم
        self._validate_and_process_selections(order, selections_str)

        return order

    def update(self, instance, validated_data):
        selections_str = self.initial_data.get('selections')

        # آپدیت فیلدهای ساده سفارش
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # پردازش و اعتبارسنجی selections
        self._validate_and_process_selections(instance, selections_str)

        return instance