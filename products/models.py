from django.db import models
from core.models import TimestampedModel

class Brand(TimestampedModel):
    """Marcas de productos"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='brands')
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'brands'
        unique_together = ['client', 'name']
    
    def __str__(self):
        return self.name

class SubBrand(TimestampedModel):
    """Sub-marcas o líneas de productos"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='subbrands')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='subbrands')
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'subbrands'
        unique_together = ['client', 'brand', 'name']
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"

class Provider(TimestampedModel):
    """Proveedores o fabricantes"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='providers')
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'providers'
        unique_together = ['client', 'name']
    
    def __str__(self):
        return self.name

class Product(TimestampedModel):
    """Producto maestro del cliente"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='products')
    internal_sku = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    subbrand = models.ForeignKey(SubBrand, on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_with_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_iva_included = models.BooleanField(default=False)
    is_supermarket = models.BooleanField(default=False)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'products'
        unique_together = ['client', 'internal_sku']
    
    def __str__(self):
        return f"{self.internal_sku} - {self.title}"
