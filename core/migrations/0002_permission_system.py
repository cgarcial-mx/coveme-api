from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        ('clients', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        # Crear tablas de permisos
        migrations.CreateModel(
            name='PermissionScope',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('client', 'Cliente'), ('brand', 'Marca'), ('subbrand', 'Submarca'), ('global', 'Global')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('hierarchy_level', models.IntegerField(help_text='Nivel en la jerarquía (1=cliente, 2=marca, 3=submarca, 4=global)')),
            ],
            options={
                'verbose_name': 'Ámbito de Permiso',
                'verbose_name_plural': 'Ámbitos de Permisos',
                'db_table': 'permission_scopes',
                'ordering': ['hierarchy_level'],
            },
        ),
        
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('create', 'Crear'), ('read', 'Leer'), ('update', 'Actualizar'), ('delete', 'Eliminar'), ('sync', 'Sincronizar'), ('export', 'Exportar'), ('import', 'Importar'), ('approve', 'Aprobar'), ('reject', 'Rechazar'), ('list', 'Listar'), ('view', 'Ver detalle')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('endpoint_category', models.CharField(help_text='Categoría del endpoint (clients, products, orders, etc.)', max_length=50)),
            ],
            options={
                'verbose_name': 'Permiso',
                'verbose_name_plural': 'Permisos',
                'db_table': 'permissions',
                'ordering': ['endpoint_category', 'name'],
            },
        ),
        
        # Crear tabla de planes de suscripción
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('basic', 'Básico'), ('premium', 'Premium'), ('enterprise', 'Empresarial'), ('custom', 'Personalizado')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Mensual'), ('quarterly', 'Trimestral'), ('yearly', 'Anual')], default='monthly', max_length=20)),
                ('api_quota', models.IntegerField(default=10000)),
                ('user_limit', models.IntegerField(default=5)),
                ('storage_limit_gb', models.IntegerField(default=10)),
                ('endpoint_config', models.JSONField(default=dict, help_text='Configuración de endpoints del plan')),
            ],
            options={
                'verbose_name': 'Plan de Suscripción',
                'verbose_name_plural': 'Planes de Suscripción',
                'db_table': 'subscription_plans',
            },
        ),
        
        # Crear tabla de permisos de usuario
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
                ('granted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to='core.user')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.permission')),
                ('scope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.permissionscope')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='core.user')),
                ('brands', models.ManyToManyField(blank=True, related_name='user_permissions', to='products.brand')),
                ('subbrands', models.ManyToManyField(blank=True, related_name='user_permissions', to='products.subbrand')),
            ],
            options={
                'verbose_name': 'Permiso de Usuario',
                'verbose_name_plural': 'Permisos de Usuario',
                'db_table': 'user_permissions',
                'unique_together': {('user', 'permission', 'scope', 'client')},
            },
        ),
        
        # Agregar índices
        migrations.AddIndex(
            model_name='userpermission',
            index=models.Index(fields=['user', 'is_active'], name='user_permissions_user_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='userpermission',
            index=models.Index(fields=['client'], name='user_permissions_client_idx'),
        ),
    ]
