from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from orders.models import Order
from store.models import ProductVariant
from .razorpay_client import verify_payment_signature
from orders.utils import send_order_confirmation_email

class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        rzp_order_id = data.get('razorpay_order_id')
        
        is_valid = verify_payment_signature(
            rzp_order_id,
            data.get('razorpay_payment_id'),
            data.get('razorpay_signature')
        )

        if not is_valid:
            return Response({"error": "Invalid Signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(razorpay_order_id=rzp_order_id)
                
                if order.payment_status == 'Paid':
                    return Response({"message": "Already processed"}, status=status.HTTP_200_OK)

                # 1. Update Order Status
                order.payment_status = 'Paid'
                order.razorpay_payment_id = data.get('razorpay_payment_id')
                
                # 2. Deduct Stock for each Item
                for item in order.items.all():
                    # Parse labels like "Size: M, Color: Red" to find variant
                    # This assumes your labels are consistent from the CheckoutView
                    parts = item.variant_label.split(', ')
                    size_name = parts[0].split(': ')[1]
                    color_name = parts[1].split(': ')[1]

                    variant = ProductVariant.objects.filter(
                        product=item.product,
                        size__name=size_name,
                        color__name=color_name
                    ).first()

                    if variant and variant.stock >= item.quantity:
                        variant.stock -= item.quantity
                        variant.save()
                
                order.save()
                send_order_confirmation_email(order.id) 

                return Response({"message": "Payment Successful & Email Sent"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)