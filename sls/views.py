from rest_framework import viewsets

from sls.models import PreInvoice, PreInvoiceItem, Supplier, OrderSupplier
from sls.serializers import PreInvoiceSerializer, PreInvoiceItemSerializer, SupplierSerializer, OrderSupplierSerializer


class PreInvoiceViewSet(viewsets.ModelViewSet):
    queryset = PreInvoice.objects.all() #prefetch_related('attribute_groups__attributes__options').all()
    serializer_class = PreInvoiceSerializer


class PreInvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = PreInvoiceItem.objects.all() #prefetch_related('attribute_groups__attributes__options').all()
    serializer_class = PreInvoiceItemSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all() #prefetch_related('attribute_groups__attributes__options').all()
    serializer_class = SupplierSerializer


class OrderSupplierViewSet(viewsets.ModelViewSet):
    queryset = OrderSupplier.objects.all() #.prefetch_related('attribute_groups__attributes__options').all()
    serializer_class = OrderSupplierSerializer

