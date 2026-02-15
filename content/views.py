from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HeroSlide, BrandStorySettings, Announcement
from .serializers import HeroSlideSerializer, BrandStorySerializer

class WebContentDetailView(APIView):
    def get(self, request):
        slides = HeroSlide.objects.filter(is_active=True)
        story = BrandStorySettings.load()
        # Fetch active announcements and return just the text
        announcements = Announcement.objects.filter(is_active=True).values_list('message', flat=True)

        return Response({
            "hero_slides": HeroSlideSerializer(slides, many=True).data,
            "brand_story": BrandStorySerializer(story).data,
            "announcements": list(announcements) # One-by-one strings for the header
        })