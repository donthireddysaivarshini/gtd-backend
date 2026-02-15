from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class WatchAndBuyVideo(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    video_file = models.FileField(
        upload_to='watch_buy_videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'mkv'])]
    )
    thumbnail = models.ImageField(upload_to='watch_buy_thumbnails/', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Made these optional
    description = models.TextField(blank=True, null=True)
    care_instructions = models.TextField(blank=True, null=True)
    # Simplified from JSON to a regular text box
    features = models.TextField(blank=True, null=True, help_text="Enter features separated by commas")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class VideoVariant(models.Model):
    video_product = models.ForeignKey(WatchAndBuyVideo, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=100, blank=True)
    color_note = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="e.g., 'The 5th saree shown in the video'"
    )
    size = models.CharField(max_length=50, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.video_product.name} - {self.color} ({self.size})"

class VideoProductReview(models.Model):
    video_product = models.ForeignKey(WatchAndBuyVideo, related_name='reviews', on_delete=models.CASCADE)
    # If you want public reviews without login, you can make user optional or use a name field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=100, blank=True) # Added for guest names
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    image = models.ImageField(upload_to='watch_buy_reviews/', blank=True, null=True) # 🔥 Added for photo uploads
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name or self.user} - {self.video_product.name} ({self.rating}*)"