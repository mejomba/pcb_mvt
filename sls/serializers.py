from rest_framework import serializers

from sls.models import PreInvoice, PreInvoiceItem, Supplier, OrderSupplier


class PreInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreInvoice
        fields = ["id", "user", "currency", "total_net_price", "total_discount", "total_tax",
                  "total_addition", "total_price", ]


class PreInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreInvoiceItem
        fields = ["id", "created_at", "updated_at", "order", "pre_invoice", "row_net_price",
                  "row_discount", "row_tax", "row_addition", "row_price"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "country", "city", "full_address"]


class OrderSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderSupplier
        fields = ["id", "order", "supplier", "supply_for"]

