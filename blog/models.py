from django.core.exceptions import ValidationError
from django.db import models


from django.db import models
from core.models import AbstractCommWithUserModel, Tag
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from core.utils import Utils
from mptt.models import MPTTModel, TreeForeignKey


try:
    from ckeditor_uploader.fields import RichTextUploadingField as RichTextField
except Exception:
    # fallback برای محیط‌هایی که CKEditor نصب نیست
    RichTextField = models.TextField


User = get_user_model()


class BlogCategory(AbstractCommWithUserModel, MPTTModel):
    title = models.CharField(max_length=128)
    parent = TreeForeignKey(
        'self',
        on_delete=models.DO_NOTHING,
        related_name='children',
        null=True,
        blank=True
    )
    is_menu = models.BooleanField(default=False)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{'—' * self.level} {self.title}"



class PublishedManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(
            is_deleted=False, is_active=True, status=Post.STATUS_PUBLISHED
        )
        now = timezone.now()
        return qs.filter(models.Q(publish_at__isnull=True) | models.Q(publish_at__lte=now))


class Post(AbstractCommWithUserModel):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    tags = models.ManyToManyField(Tag, related_name='posts')
    title = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to=Utils.generic_image_path, null=True, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, null=True, blank=True,
                                 on_delete=models.DO_NOTHING, related_name="posts")
    # CKEditor:
    content = RichTextField()
    guid_content = RichTextField(null=True, blank=True)
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    publish_at = models.DateTimeField(null=True, blank=True)

    # متادیتا/سئو:
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)

    # آمار پایه:
    view_count = models.PositiveIntegerField(default=0)
    # فیلد اختیاری برای پین‌کردن در لیست:
    is_featured = models.BooleanField(default=False)

    # منیجرها:
    # active_objects = ActiveObjectsManager()  # از AbstractCommWithUserModel → ActiveObjectsManager
    objects = models.Manager()
    published = PublishedManager()        # دسترسی سریع به پست‌های منتشرشده

    class Meta:
        ordering = ("-publish_at", "-created_at")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["publish_at"]),
        ]

    def clean(self):
        # بررسی اینکه دسته انتخابی لایه آخر باشد
        if self.category and self.category.get_children().exists():
            raise ValidationError({
                "category": "شما فقط می‌توانید دسته‌ای را انتخاب کنید که زیرمجموعه ندارد."
            })
        super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            self.slug = base
        if not self.excerpt and isinstance(self.content, str):
            # خلاصه‌ی ساده (می‌تونی با strip_tags قوی‌ترش کنی)
            self.excerpt = self.content[:300]
        # اگر منتشر است و publish_at خالی، الان را ست کن:
        if self.status == self.STATUS_PUBLISHED and not self.publish_at:
            self.publish_at = self.publish_at or timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_public(self):
        if self.status != self.STATUS_PUBLISHED:
            return False
        return not self.publish_at or self.publish_at <= timezone.now()

    @property
    def reading_time_minutes(self):
        import re
        txt = self.content if isinstance(self.content, str) else ""
        words = len(re.findall(r"\w+", txt))
        return max(1, round(words/200))

    def __str__(self):
        return self.title