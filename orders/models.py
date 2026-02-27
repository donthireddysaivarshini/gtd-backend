from django.db import models
from django.conf import settings
from store.models import Product  # Matching your GTD store app

class Order(models.Model):
    PAYMENT_STATUS = [('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')]
    ORDER_STATUS = [('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
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

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Store these as text in case the product is deleted later
    product_name = models.CharField(max_length=255) # Matches Product.title
    variant_label = models.CharField(max_length=100) # Matches "Size: {name}, Color: {name}"
    price = models.DecimalField(max_digits=10, decimal_places=2) # Matches Product.price or final_price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"