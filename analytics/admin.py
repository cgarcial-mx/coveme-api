from django.contrib import admin
from .models import ApiLog

@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ['client', 'endpoint', 'method', 'status_code', 'response_time', 'created_at']
    list_filter = ['status_code', 'method', 'client']
    search_fields = ['endpoint']
    readonly_fields = ['created_at']
