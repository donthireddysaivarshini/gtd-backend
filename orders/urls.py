from django.urls import path
from .views import CheckoutView, OrderListView, update_order_status

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/update-status/', update_order_status, name='update-order-status'),
]