from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'variant_label', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_email', 'total_amount', 'payment_status', 'order_status', 'created_at']
    list_editable = ['order_status'] 
    list_filter = ['payment_status', 'order_status', 'created_at']
    search_fields = ['razorpay_order_id', 'user__email']
    inlines = [OrderItemInline]

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Customer Email'