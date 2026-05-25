from rest_framework import serializers
from .models import HeaderImage


class HeaderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderImage
        fields = ['id', 'image', 'text', 'alt']
