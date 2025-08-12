from django.db import models
from core.models import TimestampedModel
from django.utils import timezone

class Client(TimestampedModel):
    """Cliente/empresa que usa la plataforma"""
    name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Suscripción
    subscription_plan = models.ForeignKey('core.SubscriptionPlan', on_delete=models.PROTECT)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    # Límites y uso
    api_quota = models.IntegerField(default=10000)
    api_usage = models.IntegerField(default=0)
    user_count = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
        ('expired', 'Expirado'),
        ('trial', 'En prueba'),
    ])
    
    class Meta:
        db_table = 'clients'
    
    def __str__(self):
        return self.name
    
    @property
    def is_subscription_active(self):
        """Verificar si la suscripción está activa"""
        if self.status in ['suspended', 'expired']:
            return False
        
        # Si no hay fecha de inicio, considerar como activa (cliente nuevo)
        if not self.subscription_start:
            return True
        
        if self.subscription_end and timezone.now() > self.subscription_end:
            return False
        
        return True
    
    @property
    def remaining_api_quota(self):
        """Quota de API restante"""
        return max(0, self.api_quota - self.api_usage)
    
    def can_access_endpoint(self, endpoint_path, action):
        """Verificar si puede acceder a un endpoint específico"""
        if not self.is_subscription_active:
            return False
        
        # Extraer categoría del endpoint (ej: /api/v1/products/ -> products)
        endpoint_parts = endpoint_path.strip('/').split('/')
        if len(endpoint_parts) >= 3:
            endpoint_category = endpoint_parts[2]
        else:
            return False
        
        # Verificar permisos del plan
        plan_permissions = self.subscription_plan.get_endpoint_permissions()
        if endpoint_category in plan_permissions:
            return plan_permissions[endpoint_category].get(action, False)
        
        return False

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
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'client_marketplace_credentials'
        unique_together = ['client', 'marketplace_type']
    
    def __str__(self):
        return f"{self.client.name} - {self.get_marketplace_type_display()}"
