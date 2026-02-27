from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

from store.models import SiteConfig, Coupon, Product
from accounts.models import SavedAddress
from .models import Order, OrderItem
from .serializers import OrderSerializer
from payments.razorpay_client import create_order

logger = logging.getLogger(__name__)

class OrderListView(generics.ListAPIView):
    """View to list all orders for the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')

class CheckoutView(APIView):
    """View to handle checkout, coupon application, and optional address saving."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        cart_items = data.get('items', [])
        coupon_code = data.get('coupon_code')
        
        if not cart_items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch Dynamic Charges from SiteConfig
        config = SiteConfig.objects.first()
        shipping_fee = config.shipping_fee if config else Decimal('100.00')
        free_threshold = config.free_shipping_threshold if config else Decimal('2000.00')

        # 2. Calculate Subtotal
        item_subtotal = sum(Decimal(str(item.get('price', 0))) * int(item.get('quantity', 1)) for item in cart_items)
        
        # 3. Apply Shipping Logic
        final_shipping = Decimal('0.00') if item_subtotal >= free_threshold else shipping_fee
        
        # 4. Apply Coupon Logic
        discount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                # Check validity dates and minimum order value
                if coupon.valid_from <= now <= coupon.valid_to and item_subtotal >= coupon.min_order_value:
                    if coupon.discount_type == 'percentage':
                        discount = (item_subtotal * coupon.value) / 100
                    else:
                        discount = coupon.value
            except Coupon.DoesNotExist:
                pass # If coupon invalid, we just don't apply a discount

        total_amount = item_subtotal + final_shipping - discount

        try:
            with transaction.atomic():
                # ✅ FIX 1: Auto-Save Address to Profile if requested
                if data.get('save_address'):
                    SavedAddress.objects.update_or_create(
                        user=user,
                        is_default=True,
                        defaults={
                            'label': 'Home (Checkout)',
                            'first_name': data.get('firstName', ''),
                            'last_name': data.get('lastName', ''),
                            'address': data.get('shipping_address', ''),
                            'city': data.get('city', ''),
                            'state': data.get('state', 'Telangana'),
                            'zip_code': data.get('zip_code', ''),
                            'phone': data.get('phone', ''),
                        }
                    )

                # 5. Create the Local Order
                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    shipping_address=data.get('shipping_address'),
                    city=data.get('city'),
                    state=data.get('state', 'India'),
                    zip_code=data.get('zip_code'),
                    phone=data.get('phone'),
                )

                # 6. Create Order Items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item.get('id'), 
                        product_name=item.get('title'),
                        variant_label=f"Size: {item.get('size')}, Color: {item.get('color')}",
                        price=Decimal(str(item.get('price'))),
                        quantity=item.get('quantity')
                    )

                # 7. Generate Razorpay Order (Create in Paise)
                rzp_order = create_order(order.total_amount)
                order.razorpay_order_id = rzp_order['id']
                order.save()
            
            return Response({
                "order_id": order.id,
                "razorpay_order_id": rzp_order['id'],
                "amount": rzp_order['amount'], # Paise
                "currency": rzp_order['currency'],
                "key": rzp_order.get('key', '') # Optional: send key from backend
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Checkout Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def update_order_status(request, pk):
    """Admin-only view to update order status."""
    try:
        order = Order.objects.get(pk=pk)
        new_status = request.data.get('order_status')
        if new_status:
            order.order_status = new_status
            order.save()
            return Response({"message": f"Status updated to {new_status}"})
        return Response({"error": "No status provided"}, status=400)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_status(request, pk):
    """Endpoint for frontend to check order payment/shipping status."""
    try:
        order = Order.objects.get(pk=pk, user=request.user)
        return Response({
            "id": order.id,
            "payment_status": order.payment_status,
            "order_status": order.order_status
        })
    except Order.DoesNotExist:
        return Response({"error": "Not found"}, status=404)