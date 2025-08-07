from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['marketplace_type', 'marketplace_order_id', 'client', 'order_status', 'order_total', 'purchase_date']
    list_filter = ['marketplace_type', 'order_status', 'fulfillment_status', 'client']
    search_fields = ['marketplace_order_id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'sku', 'quantity', 'unit_price', 'total_price']
    list_filter = ['client', 'is_variation']
    search_fields = ['title', 'sku']
