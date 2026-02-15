from django.contrib import admin
from .models import WatchAndBuyVideo, VideoVariant, VideoProductReview

class VideoVariantInline(admin.TabularInline):
    model = VideoVariant
    fields = ('color', 'color_note', 'size', 'stock')
    extra = 1

@admin.register(WatchAndBuyVideo)
class WatchAndBuyAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VideoVariantInline]

admin.site.register(VideoProductReview)