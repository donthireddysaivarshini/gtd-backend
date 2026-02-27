from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'variant_label', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # ✅ FREEZE REQUIREMENT: Exactly 20 orders per page
    list_per_page = 20 

    # UI Columns
    list_display = ['id', 'get_user_email', 'total_amount', 'payment_status', 'order_status', 'created_at']
    list_editable = ['order_status'] 
    list_filter = ['payment_status', 'order_status', 'created_at']
    search_fields = ['id', 'razorpay_order_id', 'user__email', 'phone']
    
    # Organize fields in the Detail View to include full address columns
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'total_amount', 'razorpay_order_id', 'payment_status', 'order_status')
        }),
        ('Shipping Details', {
            'fields': ('phone', 'country', 'state', 'city', 'shipping_address', 'landmark', 'zip_code')
        }),
        ('Timestamps', {
            'fields': ('created_at',), # Removed updated_at to fix the error
        }),
    )
    readonly_fields = ['created_at']
    
    inlines = [OrderItemInline]

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Customer Email'

    # Ensure the newest orders always appear at the top
    ordering = ['-created_at']