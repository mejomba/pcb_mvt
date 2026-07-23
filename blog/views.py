from dal import autocomplete
from django.utils import timezone
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from core.pagination import XLargeResultsSetPagination
from .models import BlogCategory, Post, Notif
from .serializers import GuidPostSerializer, BlogCategorySerializer, GuidPostMiniSerializer, GuidPostContentSerializer, \
    NotifSerializer
from rest_framework import viewsets, permissions


class NotifViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing blog Notif.
    """
    serializer_class = NotifSerializer
    # permission_classes = [permissions.AllowAny]
    pagination_class = XLargeResultsSetPagination  # 250 item per page

    def get_permissions(self):
        """
        بر اساس نوع متد، سطح دسترسی را تعیین می‌کند
        """
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # برای متدهای نوشتاری، احراز هویت اجباری است
            return [permissions.IsAuthenticated()]
        # برای متدهای GET، همه می‌توانند ببینند
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Notif.objects.filter(is_active=True, from_date__lte=timezone.now(), to_date__gte=timezone.now())


class BlogCategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = BlogCategory.objects.all().order_by('tree_id', 'lft')

        # حالت عادی: فقط دسته‌های لایه آخر
        if not self.q:
            return qs.filter(children__isnull=True)

        # مرحله ۱: پیدا کردن دسته‌هایی که عنوان‌شون با عبارت جستجو match می‌کنه
        matched_parents = BlogCategory.objects.filter(title__icontains=self.q)

        # مرحله ۲: جمع‌آوری همه‌ی فرزندانِ اون‌ها
        descendant_ids = set()
        for parent in matched_parents:
            descendant_ids.update(
                parent.get_descendants().values_list('id', flat=True)
            )

        # مرحله ۳: فقط لایه آخر از اون subtreeها
        return qs.filter(id__in=descendant_ids, children__isnull=True).order_by('tree_id', 'lft')


    def get_result_label(self, item):
        try:
            return ' / '.join(ancestor.title for ancestor in item.get_ancestors(include_self=True))
        except Exception as e:
            return ''


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing blog categories.
    """
    queryset = BlogCategory.objects.all().order_by('tree_id', 'lft')
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = XLargeResultsSetPagination  # 250 item per page
    lookup_field = "slug"

    def get_queryset(self):
        return BlogCategory.objects.filter(parent__isnull=True).order_by('tree_id', 'lft')

    @action(detail=False, methods=["get"], url_path=r"slug/(?P<slug>[^/.]+)")
    def by_slug(self, request, slug=None):
        """
        دریافت پست‌های مرتبط با یک دسته خاص (و زیرمجموعه‌هایش) با استفاده از slug
        """
        category = get_object_or_404(BlogCategory, slug=slug)

        # همه زیرشاخه‌ها را هم بگیر (اگر از django-mptt استفاده می‌کنی)
        subcategories = category.get_descendants(include_self=True)

        # همه پست‌هایی که در این دسته‌ها هستند
        posts = Post.objects.filter(category__in=subcategories, status=Post.STATUS_PUBLISHED)

        # page = self.paginate_queryset(posts)
        # if page is not None:
        #     serializer = GuidPostSerializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = GuidPostMiniSerializer(posts, many=True)
        return Response(serializer.data)


class GuidPostDetailApiView(RetrieveAPIView):
    serializer_class = GuidPostContentSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        # فقط پست‌های منتشر شده را نشان می‌دهد
        queryset = Post.published.all()

        # اگر کاربر ادمین است، همه پست‌ها را نشان بده
        if self.request.user.is_staff:
            queryset = Post.objects.all()

        return queryset

    def get_object(self):
        slug = self.kwargs.get('slug')
        queryset = self.get_queryset()

        obj = get_object_or_404(queryset, slug=slug)

        # افزایش بازدید فقط برای پست‌های منتشر شده
        # if obj.status == Post.STATUS_PUBLISHED:
        #     Post.objects.filter(pk=obj.pk).update(
        #         view_count=models.F('view_count') + 1
        #     )
        #     obj.view_count += 1  # برای نمایش در همین درخواست

        return obj