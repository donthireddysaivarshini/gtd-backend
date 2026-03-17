from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, Color, Size, Category, Review, SiteConfig
from django.utils.html import format_html
from .models import Coupon, SiteConfig
from django.shortcuts import render # Added for custom view
from django.http import HttpResponseRedirect # Added for redirect

# --- Third Party Import ---
from admin_extra_buttons.api import ExtraButtonsMixin, button, link
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'active', 'valid_to')
    list_filter = ('active', 'discount_type')
    search_fields = ('code',)
    readonly_fields = ('uses_count',)

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('shipping_fee', 'free_shipping_threshold', 'tax_percentage')
    
    def has_add_permission(self, request):
        return SiteConfig.objects.count() == 0

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
    fields = ['color', 'size', 'stock', 'price_override']

@admin.register(Product)
# Added ExtraButtonsMixin here
class ProductAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = (
        'sku', 'title', 'category', 'price', 
        'is_new_arrival', 'is_best_seller', 
        'is_featured_lehenga', 'is_saree_collection'
    )
    list_editable = (
        'is_new_arrival', 'is_best_seller', 
        'is_featured_lehenga', 'is_saree_collection'
    )
    prepopulated_fields = {'slug': ('title',)} 
    inlines = [ProductImageInline, ProductVariantInline]

    # --- NEW: Bulk Upload Button Logic ---
    @button(label=' Bulk Upload Images', 
            html_attrs={
                'class': 'btn btn-info btn-sm btn-flat', # Standard Jazzmin button style
                'style': 'background-color: #ec4899; border-color: #ec4899; color: white; margin-top: 10px; font-weight: 600;'
            })
    def bulk_upload(self, request, pk):
        context = self.get_common_context(request, pk, title="Bulk Image Upload")
        obj = self.get_object(request, pk)
        
        if request.method == 'POST':
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(product=obj, image=f)
            self.message_user(request, f"Successfully uploaded {len(files)} images to {obj.title}")
            return HttpResponseRedirectToReferrer(request)
        
        context['product'] = obj
        return render(request, 'admin/store/bulk_upload.html', context)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'product', 'rating', 'is_featured','image_preview')
    list_editable = ('is_featured',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"

admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)