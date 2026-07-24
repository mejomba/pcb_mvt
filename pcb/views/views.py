# products/views.py
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import viewsets, permissions, parsers, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAuthenticatedAndOwner
from ..models.models import (AttributeGroup, Attribute, AttributeOption,
                             ConditionalRule, Order, OrderSelection, OrderPayment, Wrapper)
from ..serializers.serializers import (AttributeGroupSerializer, AttributeSerializer, AttributeOptionSerializer,
                                       ConditionalRuleSerializer, OrderSerializer, OrderSelectionSerializer,
                                       WrapperSerializer)


class WrapperViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مشاهده و ویرایش wrapper.
    """
    # استفاده از prefetch_related برای بهینه‌سازی و جلوگیری از N+1 query
    queryset = Wrapper.objects.prefetch_related('attribute_groups__attributes__options').all()
    serializer_class = WrapperSerializer


class AttributeGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مشاهده و ویرایش گروه‌های ویژگی.
    """
    # استفاده از prefetch_related برای بهینه‌سازی و جلوگیری از N+1 query
    queryset = AttributeGroup.objects.prefetch_related('attributes__options').all()
    serializer_class = AttributeGroupSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مشاهده و ویرایش ویژگی‌ها.
    """
    queryset = Attribute.objects.prefetch_related('options').all()
    serializer_class = AttributeSerializer


class AttributeOptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet برای مشاهده و ویرایش گزینه‌های ویژگی.
    """
    queryset = AttributeOption.objects.all()
    serializer_class = AttributeOptionSerializer


class ConditionalRuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    یک ViewSet فقط-خواندنی برای ارسال لیست تمام قوانین به فرانت‌اند.
    """
    queryset = ConditionalRule.objects.select_related('trigger_option', 'target_content_type').all()
    serializer_class = ConditionalRuleSerializer


def content_type_autocomplete(request):
    q = request.GET.get('q', '')
    content_types = ContentType.objects.filter(
        model__in=['attributegroup', 'attribute', 'attributeoption']
    )

    if q:
        content_types = content_types.filter(model__icontains=q)

    results = [{
        'id': ct.id,
        'text': f"{ct.app_label} - {ct.model}"
    } for ct in content_types]

    return JsonResponse({'results': results})


def object_autocomplete(request):
    content_type_id = request.GET.get('forward')
    try:
        content_type_id = json.loads(content_type_id).get('target_content_type')
    except Exception as e:
        content_type_id = None

    q = request.GET.get('q', '')

    if not content_type_id:
        return JsonResponse({'results': []})

    try:
        content_type = ContentType.objects.get(id=content_type_id)
        model_class = content_type.model_class()
        objects = model_class.objects.all()

        if q:
            objects = objects.filter(display_name__icontains=q)

        results = [{
            'id': obj.id,
            'text': str(obj)
        } for obj in objects]

        return JsonResponse({'results': results})
    except ContentType.DoesNotExist:
        return JsonResponse({'results': []})


@method_decorator(csrf_exempt, name="dispatch")
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('user').prefetch_related('selections')
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        # در زمان ایجاد سفارش، کاربر جاری را ثبت می‌کنیم
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        order_id = self.request.query_params.get('id')
        gte = self.request.query_params.get('created_at__gte')
        lte = self.request.query_params.get('created_at__lte')
        status = self.request.query_params.get('status')
        if order_id:
            queryset = queryset.filter(id=order_id)
        if gte and lte:
            queryset = queryset.filter(created_at__gte=gte, created_at__lte=lte)
        if gte and not lte:
            queryset = queryset.filter(created_at__eq=gte)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class OrderSelectionViewSet(viewsets.ModelViewSet):
    queryset = OrderSelection.objects.all().select_related('order', 'attribute', 'selected_option')
    serializer_class = OrderSelectionSerializer
    # permission_classes = [permissions.IsAuthenticated]

@extend_schema(
        request=inline_serializer(
            name='upload_order_payment_request',
            fields={
                'order': serializers.IntegerField(help_text='شناسه سفارش'),
                'file': serializers.CharField(help_text='فایل رسید پرداخت')
            }
        ),
        responses={
            200: inline_serializer(
                name='upload_order_payment_response',
                fields={
                    'id': serializers.IntegerField(),
                }
            ),
            400: {"description": "order_id and file required"},
            404: {"description": "order not found"},
        }
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_order_payment(request):
    order_id = request.data.get('order')
    file = request.FILES.get('file')

    if not file or not order_id:
        return Response({"description": "order_id and file required"}, status=400)

    try:
        Order.objects.get(pk=order_id, user=request.user)
    except Exception as e:
        return Response({"description": "order not found"}, status=404)

    payment = OrderPayment.objects.create(
        creator_user=request.user,
        editor_user=request.user,
        order_id=order_id,
        file=file
    )
    return Response({"id": payment.id})
