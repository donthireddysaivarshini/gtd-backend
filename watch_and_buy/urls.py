from django.urls import path
from .views import WatchAndBuyListView, WatchAndBuyDetailView, VideoReviewCreateView

urlpatterns = [
    path('', WatchAndBuyListView.as_view(), name='watch-buy-list'),
    path('<slug:slug>/', WatchAndBuyDetailView.as_view(), name='watch-buy-detail'),
    # 🔥 Endpoint for posting a review: /api/watch-and-buy/my-product-slug/review/
    path('<slug:slug>/review/', VideoReviewCreateView.as_view(), name='video-review-create'),
]