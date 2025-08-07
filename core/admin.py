from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'client', 'status', 'is_active']
    list_filter = ['role', 'status', 'is_active', 'client']
    search_fields = ['username', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Coveme Settings', {'fields': ('client', 'role', 'permissions', 'status')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Coveme Settings', {'fields': ('client', 'role', 'permissions', 'status')}),
    )
