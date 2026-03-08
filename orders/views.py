from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging
from django.conf import settings
from watch_and_buy.models import WatchAndBuyVideo

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

        config = SiteConfig.objects.first()
        shipping_fee = config.shipping_fee if config else Decimal('100.00')
        free_threshold = config.free_shipping_threshold if config else Decimal('2000.00')

        item_subtotal = sum(Decimal(str(item.get('price', 0))) * int(item.get('quantity', 1)) for item in cart_items)
        final_shipping = Decimal('0.00') if item_subtotal >= free_threshold else shipping_fee
        
        discount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                if coupon.valid_from <= now <= coupon.valid_to and item_subtotal >= coupon.min_order_value:
                    if coupon.discount_type == 'percentage':
                        discount = (item_subtotal * coupon.value) / 100
                    else:
                        discount = coupon.value
            except Coupon.DoesNotExist:
                pass 

        total_amount = item_subtotal + final_shipping - discount

        try:
            with transaction.atomic():
                if coupon_code:
                    try:
                        coupon = Coupon.objects.select_for_update().get(code=coupon_code, active=True)
                        if coupon.uses_count < coupon.usage_limit:
                            coupon.uses_count += 1
                            coupon.save()
                        else:
                            return Response({"error": "Coupon limit reached"}, status=400)
                    except Coupon.DoesNotExist:
                        pass 
                
                if data.get('save_address'):
                    SavedAddress.objects.update_or_create(
                        user=user,
                        is_default=True,
                        defaults={
                            'label': 'Home (Checkout)',
                            'first_name': data.get('firstName', ''),
                            'last_name': data.get('lastName', ''),
                            'address': data.get('shipping_address', ''),
                            'landmark': data.get('landmark'),
                            'state': data.get('state', 'Telangana'),
                            'country': data.get('country', 'India'),
                            'city': data.get('city', ''),
                            'zip_code': data.get('zip_code', ''),
                            'phone': data.get('phone', ''),
                        }
                    )

                order = Order.objects.create(
                    user=user,
                    first_name=data.get('firstName'), # Capturing from frontend
                    last_name=data.get('lastName'),
                    total_amount=total_amount,
                    shipping_address=data.get('shipping_address'),
                    landmark=data.get('landmark'),
                    state=data.get('state'),
                    country=data.get('country'),
                    city=data.get('city'),
                    zip_code=data.get('zip_code'),
                    phone=data.get('phone'),
                )
                
                # Inside CheckoutView -> post method
                # Inside CheckoutView -> post method in views.py
                for item in cart_items:
                    # 1. Get details from the frontend payload
                    p_type = item.get('product_type', 'REGULAR')
                    raw_id = item.get('productId')
                    is_watch_buy = (p_type == 'WATCH_BUY')
                    
                    print(f"DEBUG: Processing Item: {item.get('title')} | ID: {raw_id} | Type: {p_type}")

                    # 2. Create the OrderItem with correct table links
                    OrderItem.objects.create(
                        order=order,
                        # If WATCH_BUY, leave 'product' as None so it doesn't link to random store items
                        product=Product.objects.filter(id=raw_id).first() if not is_watch_buy else None,
                        
                        # If WATCH_BUY, link to the Video model so thumbnail/slug works
                        watch_product=WatchAndBuyVideo.objects.filter(id=raw_id).first() if is_watch_buy else None,
                        
                        product_type=p_type,
                        product_name=item.get('title') or item.get('name'),
                        variant_label=f"Size: {item.get('size', 'N/A')}, Color: {item.get('color', 'N/A')}",
                        price=Decimal(str(item.get('price', 0))),
                        quantity=item.get('quantity', 1)
                    )
                    print(f"DEBUG: Processed {item.get('name')} as {item.get('product_type')}")

                rzp_order = create_order(order.total_amount)
                order.razorpay_order_id = rzp_order['id']
                order.save()
            
            return Response({
                "order_id": order.id,
                "razorpay_order_id": rzp_order['id'],
                "amount": rzp_order['amount'],
                "currency": rzp_order['currency'],
                "key": getattr(settings, "RAZORPAY_KEY_ID", ""), 
                "order_status": order.order_status
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
