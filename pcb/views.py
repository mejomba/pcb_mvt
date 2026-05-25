# products/views.py
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from rest_framework import viewsets, permissions, parsers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (AttributeGroup, Attribute, AttributeOption,
                     ConditionalRule, Order, OrderSelection, OrderPayment)
from .serializers import (AttributeGroupSerializer, AttributeSerializer, AttributeOptionSerializer,
                          ConditionalRuleSerializer, OrderSerializer, OrderSelectionSerializer)


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


class OrderSelectionViewSet(viewsets.ModelViewSet):
    queryset = OrderSelection.objects.all().select_related('order', 'attribute', 'selected_option')
    serializer_class = OrderSelectionSerializer
    # permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_order_payment(request):
    order_id = request.data.get('order')
    file = request.FILES.get('file')

    payment = OrderPayment.objects.create(
        creator_user=request.user,
        editor_user=request.user,
        order_id=order_id,
        file=file
    )
    return Response({"id": payment.id})
