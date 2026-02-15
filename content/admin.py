from django.contrib import admin
from .models import HeroSlide, BrandStorySettings, Announcement,BrandStoryImage

class BrandStoryImageInline(admin.TabularInline):
    model = BrandStoryImage
    extra = 4 # Shows 4 empty slots for images by default

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    # Removed 'title_main' and replaced with 'link_url'
    list_display = ('link_url', 'is_active', 'order') 
    list_editable = ('is_active', 'order')

@admin.register(BrandStorySettings)
class BrandStoryAdmin(admin.ModelAdmin):
    inlines = [BrandStoryImageInline]
    
    def has_add_permission(self, request):
        return BrandStorySettings.objects.count() == 0

admin.site.register(Announcement)