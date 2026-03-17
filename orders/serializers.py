from rest_framework import serializers
from .models import Order, OrderItem
from watch_and_buy.models import WatchAndBuyVideo 
from store.models import ProductImage, ProductVariant

class OrderItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_watch_buy = serializers.SerializerMethodField()
    color_details = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_slug', 
            'variant_label', 'price', 'quantity', 'image', 'is_watch_buy',
            'product_type', 'color_details'
        ]

    def get_is_watch_buy(self, obj):
        return obj.product_type == 'WATCH_BUY'

    def get_color_details(self, obj):
        """Extracts color name and hex from the variant label string"""
        try:
            # Parses "Size: M, Color: Pink" -> "Pink"
            parts = obj.variant_label.split(', ')
            color_name = parts[1].split(': ')[1].strip()
            
            # Find the actual color object to get the HEX code
            variant = ProductVariant.objects.filter(
                product=obj.product, 
                color__name__iexact=color_name
            ).first()
            
            if variant and variant.color:
                return {
                    "name": variant.color.name,
                    "hex": variant.color.hex_code
                }
        except:
            return None
        return None

    def get_product_slug(self, obj):
        if obj.product_type == 'WATCH_BUY' and obj.watch_product:
            return obj.watch_product.slug
        if obj.product:
            return obj.product.slug
        return ""

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = None

        # 1. Logic for Watch & Buy
        if obj.product_type == 'WATCH_BUY' and obj.watch_product:
            if obj.watch_product.thumbnail:
                image_url = obj.watch_product.thumbnail.url
        
        # 2. Logic for Regular Products (Color-Specific)
        elif obj.product:
            try:
                # Extract color name from "Size: M, Color: Pink"
                parts = obj.variant_label.split(', ')
                color_name = parts[1].split(': ')[1].strip()
                
                # Find image linked to this specific color ID
                image_obj = ProductImage.objects.filter(
                    product=obj.product, 
                    color__name__iexact=color_name
                ).first()

                if image_obj and image_obj.image:
                    image_url = image_obj.image.url
                else:
                    # Fallback to the first image if color-specific one isn't found
                    first_img = obj.product.images.first()
                    if first_img:
                        image_url = first_img.image.url
            except:
                # General fallback
                first_img = obj.product.images.first()
                if first_img:
                    image_url = first_img.image.url

        if image_url and request:
            return request.build_absolute_uri(image_url)
        return image_url

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'total_amount', 
            'payment_status', 'order_status', 'created_at', 
            'shipping_address', 'phone', 'landmark', 'city', 
            'state', 'country', 'zip_code', 'items', 'tracking_link','tracking_note'
        ]