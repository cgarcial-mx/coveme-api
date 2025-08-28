from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite
from .models import Client, ClientMarketplaceCredentials
from .utils import test_marketplace_connection, sync_products_listings

class CustomAdminSite(AdminSite):
    """Custom admin site with additional CSS"""
    
    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = ['clients/admin.css']
        return context

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'subscription_plan', 'status', 'api_quota', 'api_usage', 'user_count', 'created_at']
    list_filter = ['subscription_plan', 'status']
    search_fields = ['name', 'tax_id']
    readonly_fields = ['subscription_start', 'api_usage', 'user_count']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'tax_id', 'status')
        }),
        ('Suscripción', {
            'fields': ('subscription_plan', 'subscription_start', 'subscription_end', 'auto_renew')
        }),
        ('Límites y Uso', {
            'fields': ('api_quota', 'api_usage', 'user_count'),
            'description': 'El uso de API se actualiza automáticamente'
        }),
    )

@admin.register(ClientMarketplaceCredentials)
class ClientMarketplaceCredentialsAdmin(admin.ModelAdmin):
    list_display = ['client', 'name', 'marketplace_type', 'connection_status_display', 'last_sync_at', 'test_connection_button', 'sync_products_button']
    list_filter = ['marketplace_type', 'connection_status']
    search_fields = ['client__name']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at', 'last_error']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'name', 'marketplace_type', 'marketplace_name')
        }),
        ('Credentials', {
            'fields': ('credentials', 'settings', 'webhook_url'),
            'classes': ('collapse',)
        }),
        ('Connection Status', {
            'fields': ('connection_status', 'last_sync_at', 'last_error'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('clients/admin.css',)
        }
    
    def connection_status_display(self, obj):
        """Display connection status with color coding"""
        status_classes = {
            'connected': 'connection-status-connected',
            'disconnected': 'connection-status-disconnected',
            'error': 'connection-status-error'
        }
        css_class = status_classes.get(obj.connection_status, '')
        return format_html(
            '<span class="{}">{}</span>',
            css_class,
            obj.get_connection_status_display()
        )
    connection_status_display.short_description = 'Status'
    connection_status_display.admin_order_field = 'connection_status'
    
    def test_connection_button(self, obj):
        """Display test connection button"""
        if obj.pk:
            return format_html(
                '<a class="test-connection-button" href="{}">Test Connection</a>',
                f'/admin/clients/clientmarketplacecredentials/{obj.pk}/test-connection/'
            )
        return "Save first to test"
    test_connection_button.short_description = 'Test Connection'
    test_connection_button.allow_tags = True
    
    def sync_products_button(self, obj):
        """Display sync products button"""
        if obj.pk:
            return format_html(
                '<a class="sync-products-button" href="{}">Sync Products</a>',
                f'/admin/clients/clientmarketplacecredentials/{obj.pk}/sync-products/'
            )
        return "Save first to sync"
    sync_products_button.short_description = 'Sync Products'
    sync_products_button.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/test-connection/',
                self.admin_site.admin_view(self.test_connection_view),
                name='clients_clientmarketplacecredentials_test_connection',
            ),
            path(
                '<int:object_id>/sync-products/',
                self.admin_site.admin_view(self.sync_products_view),
                name='clients_clientmarketplacecredentials_sync_products',
            ),
        ]
        return custom_urls + urls
    
    def test_connection_view(self, request, object_id):
        """Handle test connection request"""
        try:
            credentials = ClientMarketplaceCredentials.objects.get(pk=object_id)
            
            # Test the connection
            success, message = test_marketplace_connection(credentials)
            
            if success:
                # Update connection status
                credentials.connection_status = 'connected'
                credentials.last_error = None
                messages.success(request, f"✅ {message}")
            else:
                # Update connection status
                credentials.connection_status = 'error'
                credentials.last_error = message
                messages.error(request, f"❌ {message}")
            
            credentials.save()
            
        except ClientMarketplaceCredentials.DoesNotExist:
            messages.error(request, "Credential not found")
        except Exception as e:
            messages.error(request, f"Error testing connection: {str(e)}")
        
        # Redirect back to the change form
        return HttpResponseRedirect(
            f'/admin/clients/clientmarketplacecredentials/{object_id}/change/'
        )
    
    def sync_products_view(self, request, object_id):
        """Handle sync products request"""
        try:
            credentials = ClientMarketplaceCredentials.objects.get(pk=object_id)
            
            # Sync products and listings
            success, message = sync_products_listings(credentials)
            
            if success:
                # Update last sync timestamp
                from django.utils import timezone
                credentials.last_sync_at = timezone.now()
                credentials.last_error = None
                messages.success(request, f"✅ {message}")
            else:
                # Update error status
                credentials.last_error = message
                messages.error(request, f"❌ {message}")
            
            credentials.save()
            
        except ClientMarketplaceCredentials.DoesNotExist:
            messages.error(request, "Credential not found")
        except Exception as e:
            messages.error(request, f"Error syncing products: {str(e)}")
        
        # Redirect back to the change form
        return HttpResponseRedirect(
            f'/admin/clients/clientmarketplacecredentials/{object_id}/change/'
        )
