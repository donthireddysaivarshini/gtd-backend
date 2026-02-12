from rest_framework import serializers
from .models import *
from django.db.models import Avg  # <--- ADD THIS LINE



class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'is_navbar_visible', 'is_featured']

class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source='image')
    video_url = serializers.FileField(source='video', allow_null=True) # 🔥 Added
    class Meta:
        model = ProductImage
        fields = ['url','video_url', 'color']

class ProductVariantSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(source='color.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)
    
    # Calculate the total price for this variant
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'color_name', 'size', 'size_name', 'stock', 'price_override', 'final_price']

    def get_final_price(self, obj):
        # Adds base price from Product model to the override from Variant model
        return obj.product.price + obj.price_override

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # 🔥 FIX: Make product read_only so the View can set it manually
        fields = ['id', 'user_name', 'rating', 'comment', 'image', 'created_at', 'product']
        read_only_fields = ['product']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    colors = serializers.SerializerMethodField()

    
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    def get_colors(self, obj):
        color_map = {}
        for variant in obj.variants.all():
            c_id = variant.color.id # 🔥 Extract ID
            if c_id not in color_map:
                color_map[c_id] = {
                    "id": c_id, # 🔥 Use actual ID for matching
                    "name": variant.color.name,
                    "hex": variant.color.hex_code,
                    "sizes": []
                }
            color_map[c_id]["sizes"].append({
                "size": variant.size.name,
                "price": obj.price + variant.price_override,
                "stock": variant.stock,
                "inStock": variant.stock > 0
            })
        return list(color_map.values())

class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = '__all__'