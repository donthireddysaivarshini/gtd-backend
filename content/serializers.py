from rest_framework import serializers
from .models import HeroSlide, BrandStorySettings,BrandStoryImage

class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = ['image', 'link_url']

class BrandStoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandStoryImage
        fields = ['image']
class BrandStorySerializer(serializers.ModelSerializer):
    # This automatically collects all related images
    images = BrandStoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = BrandStorySettings
        fields = ['tagline', 'heading', 'content', 'experience_years', 'images']