from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, Color, Size, Category, Review, SiteConfig

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'video', 'color']

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

# Register models only once to avoid the "AlreadyRegistered" crash
admin.site.register(Category)


admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Review)
admin.site.register(SiteConfig)