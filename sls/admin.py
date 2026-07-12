from django.contrib import admin

from .models import PreInvoice, PreInvoiceItem, Supplier, OrderSupplier


admin.site.register([PreInvoice, PreInvoiceItem, Supplier, OrderSupplier])