import django_filters

from pcb.models import Order


class OrderFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains',
        label='نام کاربری'
    )
    email = django_filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains',
        label='ایمیل'
    )
    created_date = django_filters.DateFromToRangeFilter(
        field_name='created_at',
        label='تاریخ ایجاد (از - تا)'
    )

    class Meta:
        model = Order
        fields = ['status']
