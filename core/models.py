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
