from rest_framework import generics, status
from rest_framework.response import Response
from .models import WatchAndBuyVideo, VideoProductReview
from .serializers import WatchAndBuySerializer, VideoProductReviewSerializer

class WatchAndBuyListView(generics.ListAPIView):
    queryset = WatchAndBuyVideo.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = WatchAndBuySerializer

class WatchAndBuyDetailView(generics.RetrieveAPIView):
    queryset = WatchAndBuyVideo.objects.all()
    serializer_class = WatchAndBuySerializer
    lookup_field = 'slug'

# 🔥 NEW: View to handle review submission
class VideoReviewCreateView(generics.CreateAPIView):
    serializer_class = VideoProductReviewSerializer

    def perform_create(self, serializer):
        # Link the review to the correct video based on the slug in the URL
        video_slug = self.kwargs.get('slug')
        video = WatchAndBuyVideo.objects.get(slug=video_slug)
        serializer.save(video_product=video)