from django.contrib import admin
from .models import MarketplaceListing, ProductMatch, ProductPriceHistory, ProductTracing, ProductTracingHistory

@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ['marketplace_type', 'marketplace_id', 'client', 'price', 'status']
    list_filter = ['marketplace_type', 'status', 'client']
    search_fields = ['marketplace_id', 'title']

@admin.register(ProductMatch)
class ProductMatchAdmin(admin.ModelAdmin):
    list_display = ['product', 'marketplace_listing', 'confidence_score', 'match_type', 'status']
    list_filter = ['match_type', 'status', 'client']
    search_fields = ['product__internal_sku', 'marketplace_listing__marketplace_id']

@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'marketplace_listing', 'previous_price', 'new_price', 'change_date']
    list_filter = ['change_date', 'client']
    search_fields = ['product__internal_sku']

@admin.register(ProductTracing)
class ProductTracingAdmin(admin.ModelAdmin):
    list_display = ['product', 'marketplace_type', 'seller_name', 'last_checked_price', 'is_active']
    list_filter = ['marketplace_type', 'is_active', 'client']
    search_fields = ['product__internal_sku', 'seller_name']

@admin.register(ProductTracingHistory)
class ProductTracingHistoryAdmin(admin.ModelAdmin):
    list_display = ['product_tracing', 'price', 'sales_count', 'checked_at']
    list_filter = ['checked_at', 'client']
    search_fields = ['product_tracing__product__internal_sku']
