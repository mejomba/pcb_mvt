import json

from django.utils import safestring, timezone
from rest_framework import serializers

from blog.serializers import GuidPostContentSerializer
from ..models.models import (AttributeGroup, Attribute, AttributeOption,
                             ConditionalRule, Order, OrderSelection, Wrapper, FAQ, Unit, Product)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'title']


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
    unit = UnitSerializer(many=True)
    guid = GuidPostContentSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['id', 'group', 'name', 'display_name', 'unit', 'control_type', 'description',
                  'display_order', 'options', 'file_url', 'guid']

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


class WrapperSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل گروه‌ها به همراه ویژگی‌های زیرمجموعه‌اش
    """
    # نمایش گروه های مربوط به هر رپر به صورت تودرتو
    attribute_groups = AttributeGroupSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Wrapper
        fields = ['id', 'name', 'display_name', 'display_order', 'attribute_groups', 'file_url']

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
    # item_name = serializers.SerializerMethodField(read_only=True)

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

    def _get_order_part_number(self, selections_str, file_name):
        try:
            selections_data = json.loads(selections_str)
            if not isinstance(selections_data, list):
                raise serializers.ValidationError({'selections': 'Expected a list of items.'})
        except json.JSONDecodeError:
            raise serializers.ValidationError({'selections': 'Invalid JSON format.'})

        try:
            current_date_time = timezone.now()
            y = current_date_time.year
            m = current_date_time.month
            d = current_date_time.day
            h = current_date_time.hour
            mm = current_date_time.minute
            s = current_date_time.second

            prefix = Attribute.objects.get(pk=selections_data[0]['attribute']).group.name
            attribute_pk_in_part_number = [y.pk for y in Attribute.objects.filter(pk__in=[x['attribute'] for x in selections_data], in_part_number=True)]
            attribute_names = '--'.join([x['value'] or 'empty' for x in selections_data if x['attribute'] in attribute_pk_in_part_number])
            return f'{prefix}--{file_name}--{y}/{m}/{d}-{h}:{mm}:{s}--{attribute_names}'
        except Exception as e:
            return 'can_not_create_part_number'

    def create(self, validated_data):
        uploaded_file = self.context['request'].FILES.get('file')
        file_name = 'no_file'

        # اگر فایلی وجود داشت، نام اصلی را در validated_data قرار بده
        if uploaded_file:
            validated_data['original_filename'] = uploaded_file.name  # 👈 این خط مهم است
            file_name = uploaded_file.name
            if len(file_name) > 50:
                file_name = file_name[:50] + '...'

        selections_str = self.initial_data.get('selections')

        part_number = self._get_order_part_number(selections_str, file_name)

        # ابتدا آبجکت اصلی Order را ایجاد می‌کنیم
        order = Order.objects.create(**validated_data, part_number=part_number)

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


class FAQSerializer(serializers.ModelSerializer):
    # نمایش لینک کامل فایل
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FAQ
        fields = ['id', 'title', 'text', 'file', 'file_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def validate_file(self, value):
        # اعتبارسنجی حجم فایل (حداکثر 2 مگابایت)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("حجم فایل نباید بیشتر از 2 مگابایت باشد.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    # نمایش لینک کامل فایل
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'text', 'file', 'file_url', 'min_price', 'min_quantity',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def validate_file(self, value):
        # اعتبارسنجی حجم فایل (حداکثر 2 مگابایت)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("حجم فایل نباید بیشتر از 2 مگابایت باشد.")
        return value
