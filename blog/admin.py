from dal import autocomplete
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.text import slugify
from mptt.admin import MPTTModelAdmin
from .models import Post, Tag, BlogCategory
from mptt.forms import TreeNodeChoiceField


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # =====================
    # تنظیمات نمایش لیست
    # =====================
    list_display = (
        "thumbnail_tag",
        "title",
        "category",
        "status_colored",
        "is_featured",
        "view_count",
        "publish_at",
        "created_at",
        "status",
    )
    list_filter = (
        "status",
        "is_featured",
        "category",
        "tags",
        ("publish_at", admin.DateFieldListFilter),
    )
    search_fields = ("title", "excerpt", "content", "seo_title", "seo_description")
    list_editable = ("status", "is_featured")
    date_hierarchy = "publish_at"
    ordering = ("-publish_at",)
    readonly_fields = ("view_count", "created_at", "updated_at", "reading_time_minutes")

    # =====================
    # تنظیمات فرم
    # =====================
    fieldsets = (
        ("محتوا", {
            "fields": (
                "title",
                "slug",
                "category",
                "tags",
                "thumbnail",
                "content",
                "guid_content",
                "excerpt",
            )
        }),
        ("وضعیت و زمان انتشار", {
            "fields": (
                "status",
                "publish_at",
                "is_featured",
            )
        }),
        ("SEO", {
            "fields": (
                "seo_title",
                "seo_description",
            ),
            "classes": ("collapse",)
        }),
        ("آمار و متفرقه", {
            "fields": (
                "view_count",
                "reading_time_minutes",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )

    prepopulated_fields = {"slug": ("title",)}

    # =====================
    # متدهای کمکی برای نمایش
    # =====================

    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; object-fit:cover; border-radius:4px;" />',
                obj.thumbnail.url,
            )
        return "—"
    thumbnail_tag.short_description = "Thumbnail"

    def status_colored(self, obj):
        colors = {
            Post.STATUS_DRAFT: "#888",
            Post.STATUS_PUBLISHED: "#28a745",
            Post.STATUS_ARCHIVED: "#dc3545",
        }
        color = colors.get(obj.status, "#000")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_colored.short_description = "وضعیت"

    # =====================
    # رفتارهای سفارشی
    # =====================
    def save_model(self, request, obj, form, change):
        # اگر انتشار انتخاب شده و publish_at خالی بود → پر شود
        if obj.status == Post.STATUS_PUBLISHED and not obj.publish_at:
            obj.publish_at = timezone.now()
        super().save_model(request, obj, form, change)

    # برای جلوگیری از خطای ذخیره تصویر در inline ها
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    # تنظیمات UI
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category").prefetch_related("tags")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["widget"] = autocomplete.ModelSelect2(
                url="blog:category-autocomplete",
                attrs={
                    "data-placeholder": "انتخاب دسته‌بندی...",
                    "data-minimum-input-length": 0,
                },
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # # فقط نمایش دسته‌های لایه آخر در فیلد category:
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "category":
    #         # نمایش درختی
    #         kwargs["queryset"] = BlogCategory.objects.all()
    #         # kwargs["queryset"] = BlogCategory.objects.filter(children__isnull=True)
    #         kwargs["form_class"] = TreeNodeChoiceField
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


# =====================
# مدل‌های مرتبط
# =====================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(MPTTModelAdmin):
    list_display = ("title", "parent", "is_menu")
    search_fields = ("title",)
    list_filter = ("is_menu",)
    fields = ("title", "parent", "is_menu", "slug")
    prepopulated_fields = {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        if not obj.creator_user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

