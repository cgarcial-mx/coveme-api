from django.db import models
from django.utils import timezone
from core.models import TimestampedModel

class SaleChannel(TimestampedModel):
    """Canales de venta disponibles"""
    name = models.CharField(max_length=100)
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sale_channels'
    
    def __str__(self):
        return self.name

class MarketplaceListing(TimestampedModel):
    """Listado específico en un marketplace"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='marketplace_listings')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='marketplace_listings', null=True, blank=True)
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    marketplace_id = models.CharField(max_length=100)
    external_sku = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    inventory_quantity = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    is_fulfillment = models.BooleanField(default=False)
    listing_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipment_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_type = models.CharField(max_length=50, null=True, blank=True)
    official_store_name = models.CharField(max_length=200, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    permalink = models.URLField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'marketplace_listings'
        unique_together = ['client', 'marketplace_type', 'marketplace_id']
    
    def __str__(self):
        return f"{self.marketplace_type} - {self.marketplace_id}"

class ProductMatch(TimestampedModel):
    """Coincidencias entre productos y listados de marketplace"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='product_matches')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='matches')
    marketplace_listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='matches')
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2)
    match_type = models.CharField(max_length=50, default='auto', choices=[
        ('auto', 'Automático'),
        ('manual', 'Manual'),
        ('rejected', 'Rechazado'),
    ])
    match_criteria = models.JSONField(default=dict, blank=True)
    reviewed_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='active', choices=[
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('rejected', 'Rechazado'),
    ])
    
    class Meta:
        db_table = 'product_matches'
        unique_together = ['client', 'product', 'marketplace_listing']
    
    def __str__(self):
        return f"{self.product.internal_sku} ↔ {self.marketplace_listing.marketplace_id}"

class ProductPriceHistory(TimestampedModel):
    """Historial de cambios de precios"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='price_history')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='price_history')
    marketplace_listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='price_history')
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_date = models.DateTimeField(default=timezone.now)
    total_sales = models.IntegerField(null=True, blank=True)
    utility_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    market_share = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'product_price_history'
        ordering = ['-change_date']
    
    def __str__(self):
        return f"{self.product.internal_sku} - {self.change_date}"

class ProductTracing(TimestampedModel):
    """Trazabilidad de productos competidores"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='product_tracing')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='tracing')
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    marketplace_id = models.CharField(max_length=100)
    seller_name = models.CharField(max_length=200, null=True, blank=True)
    seller_id = models.CharField(max_length=100, null=True, blank=True)
    power_seller_status = models.CharField(max_length=50, null=True, blank=True)
    last_checked_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_checked_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_tracing'
        unique_together = ['client', 'product', 'marketplace_type', 'marketplace_id']
    
    def __str__(self):
        return f"{self.product.internal_sku} - {self.marketplace_type} - {self.seller_name}"

class ProductTracingHistory(TimestampedModel):
    """Historial de datos de trazabilidad"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='tracing_history')
    product_tracing = models.ForeignKey(ProductTracing, on_delete=models.CASCADE, related_name='history')
    sales_count = models.IntegerField(null=True, blank=True)
    inventory_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'product_tracing_history'
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.product_tracing} - {self.checked_at}"
