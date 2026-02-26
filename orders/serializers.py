from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_name', 'variant_label', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'total_amount', 'shipping_address', 'city', 'state', 
            'zip_code', 'phone', 'razorpay_order_id', 'payment_status', 
            'order_status', 'created_at', 'items'
        ]