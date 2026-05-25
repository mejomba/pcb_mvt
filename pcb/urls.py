# products/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AttributeGroupViewSet, AttributeViewSet, AttributeOptionViewSet,
                    ConditionalRuleViewSet, content_type_autocomplete, object_autocomplete, OrderViewSet,
                    OrderSelectionViewSet, upload_order_payment)

from .template_view import views as template_views

# ساخت یک روتر
router = DefaultRouter()

app_name = 'pcb'
# ثبت ViewSet ها در روتر
router.register(r'groups', AttributeGroupViewSet, basename='group')
router.register(r'attributes', AttributeViewSet, basename='attribute')
router.register(r'options', AttributeOptionViewSet, basename='option')
router.register(r'rules', ConditionalRuleViewSet, basename='rule')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-selections', OrderSelectionViewSet, basename='orderselection')


# URLهای برنامه شما توسط روتر به صورت خودکار ساخته می‌شوند
urlpatterns = [
    path('', include(router.urls)),
    path('content-type-autocomplete/', content_type_autocomplete, name='target-content-type-autocomplete'),
    path('object-id-autocomplete/', object_autocomplete, name='target-object-id-autocomplete'),
    path('order_payment_receipt/upload/', upload_order_payment, name='order_payment_receipt.upload'),
    path('template/order/', template_views.pcb_order, name='template.new-order'),
]


# urlpatterns += router.urls
