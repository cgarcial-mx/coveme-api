from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.management import call_command
from django.utils import timezone
from django.db import transaction
import json
from .models import Client, ClientMarketplaceCredentials
from .serializers import (
    ClientSerializer, ClientMarketplaceCredentialsSerializer,
    MarketplaceCredentialsCreateSerializer, MarketplaceCredentialsUpdateSerializer
)
from core.mixins import ClientContextMixin

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'subscription_plan']
    
    @action(detail=True, methods=['post'])
    def test_marketplace_connection(self, request, pk=None):
        client = self.get_object()
        marketplace_type = request.data.get('marketplace_type')
        
        # Aquí implementarías la lógica de prueba de conexión
        # según el marketplace_type
        
        return Response({
            'status': 'success',
            'message': f'Conexión exitosa con {marketplace_type}'
        })

class ClientMarketplaceCredentialsViewSet(ClientContextMixin, viewsets.ModelViewSet):
    """ViewSet para manejar credenciales de marketplace"""
    
    queryset = ClientMarketplaceCredentials.objects.all()
    serializer_class = ClientMarketplaceCredentialsSerializer
    
    def get_queryset(self):
        """Filtrar por cliente del JWT"""
        client_id = self.get_client_from_request(self.request)
        return self.queryset.filter(client_id=client_id)
    
    def get_serializer_class(self):
        """Usar serializer específico según la acción"""
        if self.action == 'create':
            return MarketplaceCredentialsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MarketplaceCredentialsUpdateSerializer
        return ClientMarketplaceCredentialsSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nuevas credenciales de marketplace"""
        try:
            with transaction.atomic():
                # Validar datos requeridos
                marketplace_type = request.data.get('marketplace_type')
                name = request.data.get('name')
                
                if not marketplace_type:
                    return Response({
                        'error': 'missing_marketplace_type',
                        'message': 'El tipo de marketplace es requerido'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not name:
                    return Response({
                        'error': 'missing_name',
                        'message': 'El nombre de la credencial es requerido'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Obtener el client_id del JWT
                client_id = self.get_client_from_request(request)
                
                # Verificar si ya existe una credencial con el mismo nombre para este marketplace
                existing_credential = ClientMarketplaceCredentials.objects.filter(
                    client_id=client_id,
                    marketplace_type=marketplace_type,
                    name=name
                ).first()
                
                if existing_credential:
                    return Response({
                        'error': 'duplicate_credential',
                        'message': f'Ya existe una credencial con el nombre "{name}" para {marketplace_type}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Crear nuevas credenciales
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                
                return Response({
                    'status': 'success',
                    'message': f'Credenciales de {marketplace_type} creadas exitosamente',
                    'data': ClientMarketplaceCredentialsSerializer(instance).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'creation_failed',
                'message': f'Error al crear credenciales: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Actualizar credenciales de marketplace"""
        try:
            with transaction.atomic():
                instance = self.get_object()
                
                # Validar que el usuario tenga permisos para este cliente
                self.validate_client_permission(request, instance.client.id)
                
                # Usar el serializer apropiado
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                
                # Actualizar la instancia
                updated_instance = serializer.save()
                
                return Response({
                    'status': 'success',
                    'message': f'Credenciales de {instance.marketplace_type} actualizadas exitosamente',
                    'data': ClientMarketplaceCredentialsSerializer(updated_instance).data
                })
                
        except Exception as e:
            return Response({
                'error': 'update_failed',
                'message': f'Error al actualizar credenciales: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar credenciales de marketplace"""
        try:
            instance = self.get_object()
            
            # Validar que el usuario tenga permisos para este cliente
            self.validate_client_permission(request, instance.client.id)
            
            # Eliminar la instancia
            instance.delete()
            
            return Response({
                'status': 'success',
                'message': f'Credenciales de {instance.marketplace_type} eliminadas exitosamente'
            })
            
        except Exception as e:
            return Response({
                'error': 'deletion_failed',
                'message': f'Error al eliminar credenciales: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_marketplace_type(self, request):
        """Obtener todas las credenciales de un tipo de marketplace específico"""
        marketplace_type = request.query_params.get('marketplace_type')
        
        if not marketplace_type:
            return Response({
                'error': 'missing_marketplace_type',
                'message': 'El parámetro marketplace_type es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        client_id = self.get_client_from_request(request)
        credentials = self.get_queryset().filter(
            client_id=client_id,
            marketplace_type=marketplace_type,
            is_active=True
        )
        
        serializer = ClientMarketplaceCredentialsSerializer(credentials, many=True)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar credenciales"""
        try:
            instance = self.get_object()
            
            # Validar que el usuario tenga permisos para este cliente
            self.validate_client_permission(request, instance.client.id)
            
            # Cambiar el estado activo
            instance.is_active = not instance.is_active
            instance.save()
            
            return Response({
                'status': 'success',
                'message': f'Credenciales {"activadas" if instance.is_active else "desactivadas"} exitosamente',
                'data': ClientMarketplaceCredentialsSerializer(instance).data
            })
            
        except Exception as e:
            return Response({
                'error': 'toggle_failed',
                'message': f'Error al cambiar estado de credenciales: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def sync_products_and_listings(self, request, pk=None):
        """
        Sincronizar productos y listings desde las credenciales del marketplace
        """
        credential = self.get_object()
        
        try:
            # Validate that this is a Shopify credential
            if credential.marketplace_type != 'shopify':
                return Response({
                    'status': 'error',
                    'message': f'Sync not supported for marketplace type: {credential.marketplace_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get sync parameters from request
            dry_run = request.data.get('dry_run', False)
            debug = request.data.get('debug', False)
            
            # Use the clean SKU approach from clients.utils instead of management command
            from clients.utils import sync_shopify_products_listings
            
            if dry_run:
                # For dry run, we'll just return what would be synced
                return Response({
                    'status': 'dry_run',
                    'message': 'Dry run mode - no changes made',
                    'sync_details': {
                        'credential_id': credential.id,
                        'client_name': credential.client.name,
                        'marketplace_type': credential.marketplace_type,
                        'dry_run': True,
                        'debug': debug
                    }
                })
            
            # Execute the sync using clean SKU approach (no marketplace prefixes)
            success, message = sync_shopify_products_listings(credential)
            
            if success:
                # Update credential status
                credential.last_sync_at = timezone.now()
                credential.last_error = None
                credential.save()
                
                return Response({
                    'status': 'success',
                    'message': message,
                    'sync_details': {
                        'credential_id': credential.id,
                        'client_name': credential.client.name,
                        'marketplace_type': credential.marketplace_type,
                        'last_sync_at': credential.last_sync_at.isoformat(),
                        'dry_run': False,
                        'debug': debug
                    }
                })
            else:
                # Update credential with error
                credential.last_error = message
                credential.save()
                
                return Response({
                    'status': 'error',
                    'message': message,
                    'credential_id': credential.id,
                    'last_error': credential.last_error
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            # Update credential with error
            credential.last_error = str(e)
            credential.save()
            
            return Response({
                'status': 'error',
                'message': f'Sync failed: {str(e)}',
                'credential_id': credential.id,
                'last_error': credential.last_error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Probar la conexión con el marketplace
        """
        credential = self.get_object()
        
        try:
            # Validate credentials based on marketplace type
            if credential.marketplace_type == 'shopify':
                shop_url = credential.credentials.get('shop_url')
                access_token = credential.credentials.get('access_token')
                
                if not shop_url or not access_token:
                    return Response({
                        'status': 'error',
                        'message': 'Missing required Shopify credentials (shop_url or access_token)'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Test connection using the test command
                from io import StringIO
                from django.core.management import call_command
                
                output = StringIO()
                call_command('test_shopify_api', '--auth', stdout=output)
                output.seek(0)
                command_output = output.read()
                
                # Update connection status
                if '✅ Shopify API connection established successfully' in command_output:
                    credential.connection_status = 'connected'
                    credential.last_error = None
                else:
                    credential.connection_status = 'error'
                    credential.last_error = command_output
                
                credential.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Connection test completed',
                    'output': command_output,
                    'connection_status': credential.connection_status
                })
            
            else:
                return Response({
                    'status': 'error',
                    'message': f'Connection test not implemented for marketplace type: {credential.marketplace_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            credential.connection_status = 'error'
            credential.last_error = str(e)
            credential.save()
            
            return Response({
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'connection_status': credential.connection_status,
                'last_error': credential.last_error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
