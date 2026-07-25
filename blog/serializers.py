from rest_framework import serializers
from .models import Post, BlogCategory, Notif, WhyUs


class WhyUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyUs
        fields = [
            'id',
            'title',
            'text',
        ]


class NotifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notif
        fields = [
            'id',
            'title',
            'text',
        ]


class GuidPostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    category_name = serializers.CharField(source='category.title', read_only=True)
    breadcrumb = serializers.SerializerMethodField()
    reading_time = serializers.ReadOnlyField(source='reading_time_minutes')
    is_public = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'slug',
            'content',
            'guid_content',
            'excerpt',
            'thumbnail',
            'tags',
            'category',
            'category_name',
            'status',
            'publish_at',
            'view_count',
            'is_featured',
            'reading_time',
            'is_public',
            'seo_title',
            'seo_description',
            'created_at',
            'updated_at',
            'breadcrumb',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_breadcrumb(self, obj):
        try:
            return [cat.title for cat in obj.category.get_ancestors(include_self=True)]
        except Exception as e:
            return []


class GuidPostMiniSerializer(GuidPostSerializer):
    class Meta(GuidPostSerializer.Meta):
        fields = ['id', 'title', 'slug', 'category_name', 'breadcrumb']


class GuidPostContentSerializer(GuidPostSerializer):
    class Meta(GuidPostSerializer.Meta):
        fields = ['id', 'slug', 'title', 'guid_content', 'content', 'breadcrumb']


class BlogCategorySerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = [
            'id', 'title', 'slug', 'child', 'level',
        ]

    def get_child(self, obj):
        """
        فقط اولین زیرشاخه در مسیر تا برگ را برمی‌گرداند
        (مسیر یکتا از ریشه تا برگ)
        """
        children = obj.get_children()
        if not children.exists():
            return None

        child = children.all()
        return BlogCategorySerializer(child, many=True).data
