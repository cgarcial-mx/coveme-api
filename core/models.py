from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class TimestampedModel(models.Model):
    """Modelo base con timestamps automáticos"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class PermissionScope(models.Model):
    """Ámbitos de permisos en el sistema"""
    SCOPE_CHOICES = [
        ('client', 'Cliente'),
        ('brand', 'Marca'),
        ('subbrand', 'Submarca'),
        ('global', 'Global'),
    ]
    
    name = models.CharField(max_length=50, choices=SCOPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    hierarchy_level = models.IntegerField(help_text="Nivel en la jerarquía (1=cliente, 2=marca, 3=submarca, 4=global)")
    
    class Meta:
        db_table = 'permission_scopes'
        ordering = ['hierarchy_level']
        verbose_name = 'Permission Scope'
        verbose_name_plural = 'Permission Scopes'
    
    def __str__(self):
        return f"{self.get_name_display()} (Nivel {self.hierarchy_level})"

class Permission(models.Model):
    """Permisos específicos del sistema"""
    PERMISSION_TYPES = [
        # CRUD básico
        ('create', 'Crear'),
        ('read', 'Leer'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        
        # Operaciones especiales
        ('sync', 'Sincronizar'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
        ('approve', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('list', 'Listar'),
        ('view', 'Ver detalle'),
    ]
    
    name = models.CharField(max_length=50, choices=PERMISSION_TYPES, unique=True)
    description = models.TextField(blank=True)
    endpoint_category = models.CharField(max_length=50, help_text="Categoría del endpoint (clients, products, orders, etc.)")
    
    class Meta:
        db_table = 'permissions'
        ordering = ['endpoint_category', 'name']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.endpoint_category}"

class SubscriptionPlan(models.Model):
    """Planes de suscripción con permisos de endpoints"""
    PLAN_TYPES = [
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_TYPES, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ], default='monthly')
    
    # Límites del plan
    api_quota = models.IntegerField(default=10000)
    user_limit = models.IntegerField(default=5)
    storage_limit_gb = models.IntegerField(default=10)
    
    # Configuración de endpoints por plan
    endpoint_config = models.JSONField(default=dict, help_text="Configuración de endpoints del plan")
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
    
    def __str__(self):
        return f"{self.get_name_display()} - ${self.price}/{self.get_billing_cycle_display()}"
    
    def get_endpoint_permissions(self):
        """Obtener permisos del plan en formato para JWT"""
        return self.endpoint_config

class UserPermission(models.Model):
    """Permisos específicos de un usuario en un contexto"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='custom_user_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    scope = models.ForeignKey(PermissionScope, on_delete=models.CASCADE)
    
    # Contexto específico del permiso (1:N)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, null=True, blank=True)
    brands = models.ManyToManyField('products.Brand', blank=True, related_name='user_permissions')
    subbrands = models.ManyToManyField('products.SubBrand', blank=True, related_name='user_permissions')
    
    # Metadatos
    granted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_permissions'
        unique_together = ['user', 'permission', 'scope', 'client']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['client']),
        ]
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
    
    def __str__(self):
        context = []
        if self.client:
            context.append(f"Cliente: {self.client.name}")
        if self.brands.exists():
            context.append(f"Marcas: {', '.join([b.name for b in self.brands.all()[:3]])}")
        if self.subbrands.exists():
            context.append(f"Submarcas: {', '.join([s.name for s in self.subbrands.all()[:3]])}")
        
        context_str = " - ".join(context) if context else "Global"
        return f"{self.user.username} - {self.permission.get_name_display()} - {self.scope.get_name_display()} - {context_str}"

class User(AbstractUser, TimestampedModel):
    """Usuario extendido con funcionalidades multi-tenant"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, default='operator', choices=[
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('operator', 'Operador'),
        ('viewer', 'Visualizador'),
    ])
    permissions = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
    ])
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.client.name if self.client else 'Sin cliente'}"
    
    def get_jwt_permissions(self):
        """Obtener permisos del usuario en formato para JWT"""
        permissions = {
            'user_id': self.id,
            'username': self.username,
            'role': self.role,
            'client_id': self.client.id if self.client else None,
            'subscription_plan': self.client.subscription_plan if self.client else None,
            'endpoints': {},
            'scopes': {
                'client': None,
                'brands': [],
                'subbrands': []
            }
        }
        
        # Obtener permisos activos del usuario
        user_perms = UserPermission.objects.filter(
            user=self,
            is_active=True
        ).select_related('permission', 'scope', 'client').prefetch_related('brands', 'subbrands')
        
        # Organizar permisos por endpoint
        for user_perm in user_perms:
            endpoint = user_perm.permission.endpoint_category
            action = user_perm.permission.name
            
            if endpoint not in permissions['endpoints']:
                permissions['endpoints'][endpoint] = {}
            
            permissions['endpoints'][endpoint][action] = {
                'scope': user_perm.scope.name,
                'client_id': user_perm.client.id if user_perm.client else None,
                'brands': list(user_perm.brands.values_list('id', flat=True)),
                'subbrands': list(user_perm.subbrands.values_list('id', flat=True))
            }
        
        # Agregar permisos del plan de suscripción
        if self.client and hasattr(self.client, 'subscription_plan'):
            plan_permissions = self.client.subscription_plan.get_endpoint_permissions()
            for endpoint, actions in plan_permissions.items():
                if endpoint not in permissions['endpoints']:
                    permissions['endpoints'][endpoint] = {}
                
                for action, allowed in actions.items():
                    if allowed and action not in permissions['endpoints'][endpoint]:
                        permissions['endpoints'][endpoint][action] = {
                            'scope': 'subscription',
                            'client_id': self.client.id,
                            'brands': [],
                            'subbrands': []
                        }
        
        return permissions
