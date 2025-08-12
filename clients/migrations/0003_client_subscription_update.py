from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

def create_default_subscription_plans(apps, schema_editor):
    """Crear planes de suscripción por defecto"""
    SubscriptionPlan = apps.get_model('core', 'SubscriptionPlan')
    
    # Crear plan básico
    basic_plan, created = SubscriptionPlan.objects.get_or_create(
        name='basic',
        defaults={
            'description': 'Plan básico con funcionalidades limitadas',
            'price': 29.99,
            'billing_cycle': 'monthly',
        }
    )
    
    # Crear plan premium
    premium_plan, created = SubscriptionPlan.objects.get_or_create(
        name='premium',
        defaults={
            'description': 'Plan premium con funcionalidades completas',
            'price': 79.99,
            'billing_cycle': 'monthly',
        }
    )
    
    # Crear plan enterprise
    enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
        name='enterprise',
        defaults={
            'description': 'Plan empresarial con acceso completo',
            'price': 199.99,
            'billing_cycle': 'monthly',
        }
    )

def update_existing_clients(apps, schema_editor):
    """Actualizar clientes existentes con plan premium por defecto"""
    Client = apps.get_model('clients', 'Client')
    SubscriptionPlan = apps.get_model('core', 'SubscriptionPlan')
    
    # Obtener plan premium por defecto
    premium_plan = SubscriptionPlan.objects.get(name='premium')
    
    # Actualizar todos los clientes existentes
    Client.objects.update(subscription_plan=premium_plan)

class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0002_initial'),
        ('core', '0002_permission_system'),
    ]

    operations = [
        # Primero crear los planes de suscripción
        migrations.RunPython(create_default_subscription_plans, reverse_code=migrations.RunPython.noop),
        
        # Agregar campos de suscripción
        migrations.AddField(
            model_name='client',
            name='subscription_start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='client',
            name='subscription_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='client',
            name='auto_renew',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='client',
            name='api_quota',
            field=models.IntegerField(default=10000),
        ),
        migrations.AddField(
            model_name='client',
            name='api_usage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='user_count',
            field=models.IntegerField(default=0),
        ),
        
        # Cambiar subscription_plan a ForeignKey
        migrations.AlterField(
            model_name='client',
            name='subscription_plan',
            field=models.ForeignKey(
                'core.SubscriptionPlan',
                on_delete=django.db.models.deletion.PROTECT,
                default=1  # ID del plan premium
            ),
        ),
        
        # Actualizar clientes existentes
        migrations.RunPython(update_existing_clients, reverse_code=migrations.RunPython.noop),
        
        # Hacer el campo obligatorio
        migrations.AlterField(
            model_name='client',
            name='subscription_plan',
            field=models.ForeignKey(
                'core.SubscriptionPlan',
                on_delete=django.db.models.deletion.PROTECT,
            ),
        ),
        
        # Actualizar ClientMarketplaceCredentials
        migrations.AlterField(
            model_name='clientmarketplacecredentials',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.user'
            ),
        ),
    ]
