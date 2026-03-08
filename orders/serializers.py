from rest_framework import serializers
from .models import Order, OrderItem
from watch_and_buy.models import WatchAndBuyVideo # Ensure this model name is correct

class OrderItemSerializer(serializers.ModelSerializer):
    # Change this from ReadOnlyField to SerializerMethodField to use your logic below
    product_slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_watch_buy = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_slug', 
            'variant_label', 'price', 'quantity', 'image', 'is_watch_buy',
            'product_type' # Added this so frontend knows which route to use
        ]

    def get_is_watch_buy(self, obj):
        return obj.product_type == 'WATCH_BUY'

    def get_product_slug(self, obj):
        # 1. Check Watch & Buy logic first
        if obj.product_type == 'WATCH_BUY':
            # Use the watch_product relationship if it exists
            if hasattr(obj, 'watch_product') and obj.watch_product:
                return obj.watch_product.slug
            # Fallback: if your OrderItem model stores watch_product_id as an integer
            # and doesn't have a formal ForeignKey relationship named 'watch_product'
            # you might need to query it, but usually, the relationship is better.
        
        # 2. Check Regular Product logic
        if obj.product:
            return obj.product.slug
            
        return ""

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = None

        if obj.product_type == 'WATCH_BUY' and hasattr(obj, 'watch_product') and obj.watch_product:
            if obj.watch_product.thumbnail:
                image_url = obj.watch_product.thumbnail.url
        elif obj.product and obj.product.images.exists():
            first_image = obj.product.images.first()
            if first_image.image:
                image_url = first_image.image.url

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
            'state', 'country', 'zip_code', 'items'
        ]