from django.db import models
from core.models import TimestampedModel

class Order(TimestampedModel):
    """Órdenes de todos los marketplaces"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='orders')
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    marketplace_order_id = models.CharField(max_length=100)
    order_status = models.CharField(max_length=50, null=True, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    purchase_date = models.DateTimeField(null=True, blank=True)
    last_update_date = models.DateTimeField(null=True, blank=True)
    logistic_type = models.CharField(max_length=50, null=True, blank=True)
    customer_info = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    payment_info = models.JSONField(default=dict, blank=True)
    fulfillment_status = models.CharField(max_length=50, null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'orders'
        unique_together = ['client', 'marketplace_type', 'marketplace_order_id']
    
    def __str__(self):
        return f"{self.marketplace_type} - {self.marketplace_order_id}"

class OrderItem(TimestampedModel):
    """Productos específicos en cada orden"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    marketplace_item_id = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipment_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_variation = models.BooleanField(default=False)
    variations_attributes = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.order.marketplace_order_id} - {self.title}"
