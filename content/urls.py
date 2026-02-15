from django.urls import path
from .views import WebContentDetailView  # Changed from PublicContentView

urlpatterns = [
    path('', WebContentDetailView.as_view(), name='web-content-detail'),
]