from django.contrib import admin
from .models import Client, ClientMarketplaceCredentials

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'subscription_plan', 'status', 'created_at']
    list_filter = ['subscription_plan', 'status']
    search_fields = ['name', 'tax_id']

@admin.register(ClientMarketplaceCredentials)
class ClientMarketplaceCredentialsAdmin(admin.ModelAdmin):
    list_display = ['client', 'marketplace_type', 'connection_status', 'last_sync_at']
    list_filter = ['marketplace_type', 'connection_status']
    search_fields = ['client__name']
