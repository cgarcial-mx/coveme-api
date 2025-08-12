from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    User, PermissionScope, Permission, SubscriptionPlan, UserPermission
)

@admin.register(PermissionScope)
class PermissionScopeAdmin(admin.ModelAdmin):
    list_display = ['name', 'hierarchy_level', 'description']
    list_editable = ['hierarchy_level']
    ordering = ['hierarchy_level']
    search_fields = ['name', 'description']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'endpoint_category', 'description']
    list_filter = ['endpoint_category', 'name']
    search_fields = ['name', 'endpoint_category', 'description']
    ordering = ['endpoint_category', 'name']

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'billing_cycle', 'api_quota', 'user_limit', 'storage_limit_gb']
    list_editable = ['price', 'api_quota', 'user_limit', 'storage_limit_gb']
    list_filter = ['name', 'billing_cycle']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'price', 'billing_cycle')
        }),
        ('Límites del Plan', {
            'fields': ('api_quota', 'user_limit', 'storage_limit_gb')
        }),
        ('Configuración de Endpoints', {
            'fields': ('endpoint_config',),
            'description': 'Configura los permisos de endpoints para este plan. Ejemplo: {"clients": {"read": true, "create": false}}'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        from django import forms
        
        class SubscriptionPlanForm(forms.ModelForm):
            class Meta:
                model = SubscriptionPlan
                fields = '__all__'
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
                # Crear campos dinámicos para permisos de endpoints
                if self.instance and self.instance.pk:
                    current_config = self.instance.endpoint_config or {}
                    
                    endpoints = ['clients', 'products', 'orders', 'analytics', 'marketplaces']
                    actions = ['create', 'read', 'update', 'delete', 'sync', 'export', 'import']
                    
                    for endpoint in endpoints:
                        for action in actions:
                            field_name = f"{endpoint}_{action}"
                            current_value = current_config.get(endpoint, {}).get(action, False)
                            
                            self.fields[field_name] = forms.BooleanField(
                                initial=current_value,
                                label=f"{endpoint.title()} - {action.title()}",
                                required=False,
                                help_text=f"Permitir {action} en {endpoint}"
                            )
        
        return SubscriptionPlanForm
    
    def save_model(self, request, obj, form):
        """Guardar configuración de endpoints desde el formulario"""
        endpoint_config = {}
        
        # Recopilar configuración de endpoints desde los campos del formulario
        endpoints = ['clients', 'products', 'orders', 'analytics', 'marketplaces']
        actions = ['create', 'read', 'update', 'delete', 'sync', 'export', 'import']
        
        for endpoint in endpoints:
            endpoint_config[endpoint] = {}
            for action in actions:
                field_name = f"{endpoint}_{action}"
                if field_name in form.cleaned_data:
                    allowed = form.cleaned_data[field_name]
                    endpoint_config[endpoint][action] = allowed
        
        obj.endpoint_config = endpoint_config
        super().save_model(request, obj, form)

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'scope', 'client', 'brands_display', 'subbrands_display', 'is_active', 'granted_at']
    list_filter = ['scope', 'permission__endpoint_category', 'is_active', 'granted_at']
    search_fields = ['user__username', 'permission__name', 'client__name']
    list_editable = ['is_active']
    date_hierarchy = 'granted_at'
    
    fieldsets = (
        ('Usuario y Permiso', {
            'fields': ('user', 'permission', 'scope')
        }),
        ('Contexto del Permiso', {
            'fields': ('client', 'brands', 'subbrands'),
            'description': 'Define el alcance específico del permiso'
        }),
        ('Metadatos', {
            'fields': ('granted_by', 'expires_at', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    def brands_display(self, obj):
        """Mostrar marcas de forma legible"""
        brands = obj.brands.all()[:3]
        if brands:
            return ", ".join([b.name for b in brands])
        return "Todas las marcas"
    brands_display.short_description = "Marcas"
    
    def subbrands_display(self, obj):
        """Mostrar submarcas de forma legible"""
        subbrands = obj.subbrands.all()[:3]
        if subbrands:
            return ", ".join([s.name for s in subbrands])
        return "Todas las submarcas"
    subbrands_display.short_description = "Submarcas"
    
    def save_model(self, request, obj, form):
        """Asignar automáticamente quien otorga el permiso"""
        if not obj.granted_by:
            obj.granted_by = request.user
        super().save_model(request, obj, form)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'client', 'status', 'is_active', 'permissions_count']
    list_filter = ['role', 'status', 'is_active', 'client']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Coveme Settings', {
            'fields': ('client', 'role', 'permissions', 'status')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Coveme Settings', {
            'fields': ('client', 'role', 'permissions', 'status')
        }),
    )
    
    def permissions_count(self, obj):
        """Mostrar cantidad de permisos del usuario"""
        count = obj.custom_user_permissions.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_userpermission_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} permisos</a>', url, count)
        return "0 permisos"
    permissions_count.short_description = "Permisos"
    
    def response_add(self, request, obj, created):
        """Redirigir a gestión de permisos después de crear usuario"""
        if created:
            messages.success(request, f'Usuario {obj.username} creado exitosamente. Ahora puedes asignarle permisos.')
            return HttpResponseRedirect(
                reverse('admin:core_userpermission_add') + f'?user={obj.id}'
            )
        return super().response_add(request, obj, created)
