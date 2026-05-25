from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.text import slugify

CustomUser = get_user_model()


class ActiveObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AbstractCommModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = ActiveObjectsManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.delete_date = timezone.now()
        self.save(update_fields=['is_deleted', 'delete_date'])

        # soft delete
        for related in self._meta.related_objects:
            accessor_name = related.get_accessor_name()
            related_manager = getattr(self, accessor_name, None)
            if related_manager:
                related_qs = related_manager.all()
                for obj in related_qs:
                    if hasattr(obj, 'is_deleted'):
                        obj.delete()

    def jcreated_date(self):
        return 'return jalali created date...'

    def jupdate_date(self):
        return 'return jalali update date...'


class AbstractCommWithUserModel(AbstractCommModel):
    creator_user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(app_label)s_creator_%(model_name)s')
    editor_user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(app_label)s_editor_%(model_name)s')

    class Meta:
        abstract = True


class Tag(AbstractCommModel):
    title = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        indexes = [models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:64]
        super().save(*args, **kwargs)


class HeaderImage(AbstractCommModel):
    image = models.ImageField(upload_to='images/')
    text = models.CharField(max_length=200, null=True, blank=True)
    alt = models.CharField(max_length=100, null=True, blank=True)
