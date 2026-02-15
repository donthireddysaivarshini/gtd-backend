from rest_framework import serializers
from .models import WatchAndBuyVideo, VideoVariant, VideoProductReview

class VideoVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoVariant
        fields = ['id', 'color', 'color_note', 'size', 'stock']
class VideoProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProductReview
        fields = ['id', 'user_name', 'rating', 'comment', 'image', 'created_at']
class WatchAndBuySerializer(serializers.ModelSerializer):
    variants = VideoVariantSerializer(many=True, read_only=True)
    # Nest the review serializer here
    reviews = VideoProductReviewSerializer(many=True, read_only=True)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = WatchAndBuyVideo
        fields = [
            'id', 'name', 'slug', 'video_url', 'thumbnail', 
            'price', 'original_price', 'description', 
            'care_instructions', 'features', 'variants',
            'reviews' # 🔥 This must be present
        ]

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return obj.video_file.url if obj.video_file else None
    

