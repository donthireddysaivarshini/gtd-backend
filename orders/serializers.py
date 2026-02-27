from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.ReadOnlyField(source='product.slug')
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_slug', 'variant_label', 'price', 'quantity', 'image']

    def get_image(self, obj):
        # ✅ Check if product and images exist, then use .image.url
        if obj.product and obj.product.images.exists():
            first_image = obj.product.images.first()
            if first_image.image:  # Ensure the image file exists
                return first_image.image.url
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'total_amount', 'shipping_address', 'city', 'state', 
            'zip_code', 'phone', 'razorpay_order_id', 'payment_status', 
            'order_status', 'created_at', 'items'
        ]