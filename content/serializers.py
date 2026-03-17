from rest_framework import serializers
from .models import HeroSlide, BrandStorySettings, BrandStoryImage

class HeroSlideSerializer(serializers.ModelSerializer):
    # This ensures the full URL (http://127.0.0.1:8000/media/...) is sent
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = HeroSlide
        fields = ['image', 'link_url', 'is_active', 'order']

class BrandStoryImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = BrandStoryImage
        fields = ['image', 'order']

class BrandStorySerializer(serializers.ModelSerializer):
    # 'images' matches the related_name='images' in your BrandStoryImage model
    images = BrandStoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = BrandStorySettings
        fields = ['tagline', 'heading', 'content', 'experience_years', 'images']