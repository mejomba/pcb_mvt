from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreInvoiceViewSet, PreInvoiceItemViewSet, SupplierViewSet, OrderSupplierViewSet

# ساخت یک روتر
router = DefaultRouter()

app_name = 'sls'
# ثبت ViewSet ها در روتر
router.register(r'preinvoice', PreInvoiceViewSet, basename='preinvoice')
router.register(r'preinvoice-item', PreInvoiceItemViewSet, basename='preinvoiceitem')
router.register(r'supplier', SupplierViewSet, basename='supplier')
router.register(r'order-supplier', OrderSupplierViewSet, basename='ordersupplier')


urlpatterns = [
    path('', include(router.urls)),
]


# urlpatterns += router.urls
