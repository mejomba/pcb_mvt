from decimal import Decimal

from django.conf import settings
from django.db import models

from accounting.models import Currency
# from core.models import TimeStampedModel
from core.models import AbstractCommModel, AbstractCommWithUserModel
from pcb.models.models import Order
from django.db.models import Sum


class PreInvoice(AbstractCommWithUserModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # اگر کاربر حذف شد، پیش فاکتور باقی بماند
        null=True,
        blank=True,
        verbose_name="کاربر"
    )
    # created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    # updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="preinvoices")
    total_net_price = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="ارزش خالص")
    total_discount = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="تخفیف کل")
    total_tax = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="مالیات کل")
    total_addition = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="اضافات کل")
    total_price = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="قابل پرداخت")

    class Meta:
        ordering = ['id']

    @property
    def item_count(self):
        return self.items.count()

    @property
    def is_empty(self):
        return self.item_count == 0

    def clear_items(self):
        self.items.all().delete()
        self.recalculate_totals()

    def recalculate_totals(self):
        aggregates = self.items.aggregate(

            net=Sum("row_net_price"),

            discount=Sum("row_discount"),

            tax=Sum("row_tax"),

            addition=Sum("row_addition"),

            total=Sum("row_price"),
        )

        self.total_net_price = aggregates["net"] or Decimal("0")

        self.total_discount = aggregates["discount"] or Decimal("0")

        self.total_tax = aggregates["tax"] or Decimal("0")

        self.total_addition = aggregates["addition"] or Decimal("0")

        self.total_price = aggregates["total"] or Decimal("0")

    def clear():
        pass

    def finalize():
        pass


class PreInvoiceItem(AbstractCommModel):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='preinvoiceitems')
    pre_invoice = models.ForeignKey(PreInvoice, on_delete=models.DO_NOTHING, related_name='items')
    row_net_price = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="قیمت ردیف")
    row_discount = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="تخفیف ردیف")
    row_tax = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="مالیات ردیف")
    row_addition = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="اضافات ردیف")
    row_price = models.DecimalField(max_digits=25, decimal_places=4, verbose_name="قابل پرداخت")

    class Meta:
        ordering = ['id']


class Supplier(AbstractCommWithUserModel):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=64, null=True, blank=True)
    full_address = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=4000, null=True, blank=True)

    class Meta:
        ordering = ("name",)

    @property
    def address(self):
        return f'[{self.country}, {self.city}]: {self.full_address}'

    class Meta:
        ordering = ['id']


class OrderSupplier(AbstractCommWithUserModel):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='ordersuppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING, related_name='supplierorders')
    supply_for = models.TextField(max_length=1000, null=True, blank=True, verbose_name="اگر تامین کننده فقط بخش خاصی از سفارش را تامین میکند در این بخش درج کنید")

    class Meta:
        ordering = ['id']

