from django.contrib import admin
from django.http import HttpResponse
from .models import Order, OrderItem
import openpyxl
from openpyxl.styles import Font

# 1. EXCEL EXPORT FUNCTION
def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders_export.xlsx'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"
    
    # Updated Headers with separate Location columns
    columns = [
        'Order ID', 'First Name', 'Last Name', 'Email', 'Phone', 
        'Amount', 'Status', 'Payment', 'Date', 
        'Shipping Address', 'Landmark', 'City', 'State', 'Country', 'Zip Code'
    ]
    ws.append(columns)
    
    # Apply bold font to headers
    for cell in ws[1]:
        cell.font = Font(bold=True)
    
    for obj in queryset:
        ws.append([
            obj.id,
            obj.first_name or "",
            obj.last_name or "",
            obj.user.email if obj.user else "N/A",
            obj.phone,
            obj.total_amount,
            obj.order_status,
            obj.payment_status,
            obj.created_at.strftime("%Y-%m-%d %H:%M") if obj.created_at else "",
            obj.shipping_address,
            obj.landmark or "",
            obj.city or "",
            obj.state or "",
            obj.country or "",
            obj.zip_code or ""
        ])
    
    # Optional: Auto-adjust column width for better readability
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(response)
    return response

export_to_excel.short_description = "Export Selected to Excel"

# 2. ORDER ITEM INLINE (Products inside Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product_type', 'product', 'watch_product', 'product_name', 'variant_label', 'price', 'quantity']
    readonly_fields = ['product_type', 'product', 'watch_product', 'product_name', 'variant_label', 'price', 'quantity']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'watch_product')

# 3. MAIN ORDER ADMIN
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 20 
    ordering = ['-created_at']
    actions = [export_to_excel] # Added the export action here

    # UI Columns in the main list
    list_display = ['id', 'customer_name', 'get_user_email', 'total_amount', 'payment_status', 'order_status', 'created_at']
    list_editable = ['order_status'] 
    list_filter = ['payment_status', 'order_status', 'created_at']
    search_fields = ['id', 'first_name', 'last_name', 'user__email', 'phone', 'razorpay_order_id']
    
    # Order Detail View Organization
    fieldsets = (
        ('Customer Info', {
            'fields': (('first_name', 'last_name'), 'user', 'phone')
        }),
        ('Order Financials', {
            'fields': ('total_amount', 'razorpay_order_id', 'payment_status', 'order_status')
        }),
        ('Shipping & Tracking', {
            'fields': ('tracking_link','country', 'state', 'city', 'shipping_address', 'landmark', 'zip_code')
        }),
        ('System Timestamps', {
            'fields': ('created_at',),
        }),
    )
    readonly_fields = ['created_at']
    inlines = [OrderItemInline]

    # Helper to show full name in the list
    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = 'Customer Name'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Account Email'