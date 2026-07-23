from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from pcb.models.models import Product
from core.permissions import IsSuperuserOrReadOnly
from pcb.serializers.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperuserOrReadOnly]  # فقط کاربران لاگین شده می‌توانند ایجاد/ویرایش/حذف کنند
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title']  # فیلتر بر اساس عنوان
    search_fields = ['title', 'text']  # جستجو در عنوان و متن
    ordering_fields = ['created_at', 'updated_at', 'title']  # مرتب‌سازی
    ordering = ['-created_at']  # مرتب‌سازی پیش‌فرض

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "product با موفقیت ایجاد شد.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        print("partial: ", partial)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "product با موفقیت به‌روزرسانی شد.", "data": serializer.data}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # حذف فایل از سرور قبل از حذف رکورد
        if instance.file:
            instance.file.delete(save=False)
        self.perform_destroy(instance)
        return Response(
            {"message": "prduct با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT
        )