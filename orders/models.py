from django.db import models
from django.conf import settings
from store.models import Product  # Matching your GTD store app
from watch_and_buy.models import WatchAndBuyVideo
class Order(models.Model):
    PAYMENT_STATUS = [('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')]
    ORDER_STATUS = [('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    # Matching your project's currency needs
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping details
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Processing')
    created_at = models.DateTimeField(auto_now_add=True)
    landmark = models.CharField(max_length=255, blank=True, null=True) # ✅ New
    state = models.CharField(max_length=100, blank=True) # ✅ New
    country = models.CharField(max_length=100, default='India') #
    
    def __str__(self):
        return f"Order {self.id} - {self.user.email}"

# orders/models.py

class OrderItem(models.Model):
    PRODUCT_TYPES = [('REGULAR', 'Regular Product'), ('WATCH_BUY', 'Watch & Buy')]
    
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # Links to both potential sources (both nullable)
    product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True, blank=True)
    watch_product = models.ForeignKey(WatchAndBuyVideo, on_delete=models.SET_NULL, null=True, blank=True)
    
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='REGULAR')
    
    product_name = models.CharField(max_length=255)
    variant_label = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"[{self.product_type}] {self.product_name}"