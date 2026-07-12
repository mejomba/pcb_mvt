# products/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import (AttributeGroupViewSet, AttributeViewSet, AttributeOptionViewSet,
                          ConditionalRuleViewSet, content_type_autocomplete, object_autocomplete, OrderViewSet,
                          OrderSelectionViewSet, upload_order_payment, WrapperViewSet)

from .template_view import views as template_views
from .views.help_views import HelpCategoryView, HelpPostView, NewOrderView, HelpMainView

# ساخت یک روتر
router = DefaultRouter()

app_name = 'pcb'
# ثبت ViewSet ها در روتر
router.register(r'wrapper', WrapperViewSet, basename='wrapper')
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
    # === urls.py (اضافه کن) ===
    path('help/<slug:slug>/',       HelpCategoryView.as_view(), name='help_category'),
    path('help/post/<slug:slug>/',  HelpPostView.as_view(),     name='help_post'),
    path('new-order/',              NewOrderView.as_view(),      name='new_order'),
    path('help/', HelpMainView.as_view(), name='help_main'),
]


# urlpatterns += router.urls
