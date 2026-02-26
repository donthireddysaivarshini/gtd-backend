from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
import logging

from .models import Order, OrderItem
from .serializers import OrderSerializer
from payments.razorpay_client import create_order
from store.models import Product

logger = logging.getLogger(__name__)

class OrderListView(generics.ListAPIView):
    """View to list all orders for the logged-in user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class CheckoutView(APIView):
    """View to create a local order and a corresponding Razorpay order."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        cart_items = data.get('items', [])
        
        if not cart_items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Create the Local Order
                order = Order.objects.create(
                    user=user,
                    total_amount=data.get('total_amount'),
                    shipping_address=data.get('shipping_address'),
                    city=data.get('city'),
                    state=data.get('state', 'India'),
                    zip_code=data.get('zip_code'),
                    phone=data.get('phone'),
                )

                # 2. Create Order Items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item.get('id'), 
                        product_name=item.get('title'),
                        variant_label=f"Size: {item.get('size')}, Color: {item.get('color')}",
                        price=item.get('price'),
                        quantity=item.get('quantity')
                    )

                # 3. Generate Razorpay Order
                rzp_order = create_order(order.total_amount)
                order.razorpay_order_id = rzp_order['id']
                order.save()
            
            return Response({
                "order_id": order.id,
                "razorpay_order_id": rzp_order['id'],
                "amount": rzp_order['amount'],
                "currency": rzp_order['currency']
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