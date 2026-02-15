from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, Color, Size, Category, Review, SiteConfig
from django.utils.html import format_html

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_preview', 'video', 'color']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    # Added price_override here so you can set extra charges for sizes
    fields = ['color', 'size', 'stock', 'price_override']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'title', 'category', 'price', 
        'is_new_arrival', 'is_best_seller', 'is_watch_and_buy', 
        'is_featured_lehenga', 'is_saree_collection', 'is_kids_collection'
    )
    list_editable = (
        'is_new_arrival', 'is_best_seller', 'is_watch_and_buy', 
        'is_featured_lehenga', 'is_saree_collection', 'is_kids_collection'
    )
    prepopulated_fields = {'slug': ('title',)} 
    inlines = [ProductImageInline, ProductVariantInline] # They will appear at the bottom
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'product', 'rating', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
# Register models only once to avoid the "AlreadyRegistered" crash
admin.site.register(Category)


admin.site.register(Color)
admin.site.register(Size)

admin.site.register(SiteConfig)