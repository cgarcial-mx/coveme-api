from django.core.management.base import BaseCommand
from core.models import PermissionScope, Permission, SubscriptionPlan
from django.db import transaction

class Command(BaseCommand):
    help = 'Setup initial permission system'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("🔐 Setting up permission system...")
            
            # Create permission scopes
            scopes = [
                {'name': 'client', 'description': 'Client level access', 'hierarchy_level': 1},
                {'name': 'brand', 'description': 'Brand level access', 'hierarchy_level': 2},
                {'name': 'subbrand', 'description': 'Subbrand level access', 'hierarchy_level': 3},
                {'name': 'global', 'description': 'Global system access', 'hierarchy_level': 4},
            ]
            
            for scope_data in scopes:
                scope, created = PermissionScope.objects.get_or_create(
                    name=scope_data['name'],
                    defaults=scope_data
                )
                if created:
                    self.stdout.write(f"✅ Created scope: {scope.name}")
                else:
                    self.stdout.write(f"ℹ️  Scope already exists: {scope.name}")
            
            # Create basic permissions with unique names
            permissions_data = [
                # Clients
                {'name': 'clients_create', 'endpoint_category': 'clients', 'description': 'Create clients'},
                {'name': 'clients_read', 'endpoint_category': 'clients', 'description': 'Read clients'},
                {'name': 'clients_update', 'endpoint_category': 'clients', 'description': 'Update clients'},
                {'name': 'clients_delete', 'endpoint_category': 'clients', 'description': 'Delete clients'},
                
                # Products
                {'name': 'products_create', 'endpoint_category': 'products', 'description': 'Create products'},
                {'name': 'products_read', 'endpoint_category': 'products', 'description': 'Read products'},
                {'name': 'products_update', 'endpoint_category': 'products', 'description': 'Update products'},
                {'name': 'products_delete', 'endpoint_category': 'products', 'description': 'Delete products'},
                
                # Orders
                {'name': 'orders_create', 'endpoint_category': 'orders', 'description': 'Create orders'},
                {'name': 'orders_read', 'endpoint_category': 'orders', 'description': 'Read orders'},
                {'name': 'orders_update', 'endpoint_category': 'orders', 'description': 'Update orders'},
                {'name': 'orders_delete', 'endpoint_category': 'orders', 'description': 'Delete orders'},
                
                # Analytics
                {'name': 'analytics_create', 'endpoint_category': 'analytics', 'description': 'Create reports'},
                {'name': 'analytics_read', 'endpoint_category': 'analytics', 'description': 'Read reports'},
                {'name': 'analytics_update', 'endpoint_category': 'analytics', 'description': 'Update reports'},
                {'name': 'analytics_delete', 'endpoint_category': 'analytics', 'description': 'Delete reports'},
                
                # Marketplaces
                {'name': 'marketplaces_create', 'endpoint_category': 'marketplaces', 'description': 'Create marketplaces'},
                {'name': 'marketplaces_read', 'endpoint_category': 'marketplaces', 'description': 'Read marketplaces'},
                {'name': 'marketplaces_update', 'endpoint_category': 'marketplaces', 'description': 'Update marketplaces'},
                {'name': 'marketplaces_delete', 'endpoint_category': 'marketplaces', 'description': 'Delete marketplaces'},
            ]
            
            for perm_data in permissions_data:
                # Now each permission has a unique name
                permission, created = Permission.objects.get_or_create(
                    name=perm_data['name'],
                    defaults={
                        'endpoint_category': perm_data['endpoint_category'],
                        'description': perm_data['description']
                    }
                )
                if created:
                    self.stdout.write(f"✅ Created permission: {permission.name}")
                else:
                    self.stdout.write(f"ℹ️  Permission already exists: {permission.name}")
            
            # Create basic subscription plans
            subscription_plans = [
                {
                    'name': 'basic',
                    'description': 'Basic plan with limited functionality',
                    'price': 29.99,
                    'billing_cycle': 'monthly',
                },
                {
                    'name': 'premium',
                    'description': 'Premium plan with full functionality',
                    'price': 79.99,
                    'billing_cycle': 'monthly',
                },
                {
                    'name': 'enterprise',
                    'description': 'Enterprise plan with complete access',
                    'price': 199.99,
                    'billing_cycle': 'yearly',
                }
            ]
            
            for plan_data in subscription_plans:
                plan, created = SubscriptionPlan.objects.get_or_create(
                    name=plan_data['name'],
                    defaults=plan_data
                )
                if created:
                    self.stdout.write(f"✅ Created plan: {plan.name}")
                else:
                    self.stdout.write(f"ℹ️  Plan already exists: {plan.name}")
            
            self.stdout.write("🎉 Permission system setup completed successfully!")
