from django.db import models
from core.models import TimestampedModel

class Client(TimestampedModel):
    """Cliente/empresa que usa la plataforma"""
    name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    subscription_plan = models.CharField(max_length=50, default='basic', choices=[
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    ])
    api_quota = models.IntegerField(default=10000)
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
    ])
    
    class Meta:
        db_table = 'clients'
    
    def __str__(self):
        return self.name

class ClientMarketplaceCredentials(TimestampedModel):
    """Credenciales de marketplace por cliente"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='marketplace_credentials')
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    marketplace_name = models.CharField(max_length=100, null=True, blank=True)
    credentials = models.JSONField()  # Credenciales encriptadas
    settings = models.JSONField(default=dict, blank=True)
    webhook_url = models.URLField(max_length=500, null=True, blank=True)
    connection_status = models.CharField(max_length=50, default='disconnected', choices=[
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('error', 'Error'),
    ])
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'client_marketplace_credentials'
        unique_together = ['client', 'marketplace_type']
    
    def __str__(self):
        return f"{self.client.name} - {self.get_marketplace_type_display()}"
