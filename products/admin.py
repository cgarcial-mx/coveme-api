from django.contrib import admin
from .models import Product, Brand, SubBrand, Provider

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['internal_sku', 'title', 'client', 'brand', 'created_at']
    list_filter = ['client', 'brand', 'category']
    search_fields = ['internal_sku', 'title']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'client']
    list_filter = ['client']
    search_fields = ['name']

@admin.register(SubBrand)
class SubBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'client']
    list_filter = ['brand', 'client']
    search_fields = ['name']

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'client']
    list_filter = ['client']
    search_fields = ['name', 'email']
