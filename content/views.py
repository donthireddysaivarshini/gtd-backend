from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HeroSlide, BrandStorySettings, Announcement
from .serializers import HeroSlideSerializer, BrandStorySerializer

class WebContentDetailView(APIView):
    def get(self, request):
        slides = HeroSlide.objects.filter(is_active=True)
        story = BrandStorySettings.load()
        announcements = Announcement.objects.filter(is_active=True).values_list('message', flat=True)

        return Response({
            # 🔥 ADD context={'request': request} to both below
            "hero_slides": HeroSlideSerializer(slides, many=True, context={'request': request}).data,
            "brand_story": BrandStorySerializer(story, context={'request': request}).data,
            "announcements": list(announcements)
        })