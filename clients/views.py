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
    """
    ViewSet para manejar credenciales de marketplace de clientes
    El client_id se extrae automáticamente del JWT del usuario autenticado
    """
    queryset = ClientMarketplaceCredentials.objects.all()
    serializer_class = ClientMarketplaceCredentialsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marketplace_type', 'connection_status']
    parser_classes = [JSONParser]
    
    def get_queryset(self):
        """Filtrar queryset para mostrar solo las credenciales del cliente del usuario"""
        queryset = super().get_queryset()
        
        # Si el usuario es superuser o admin global, puede ver todas
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return queryset
        
        # Filtrar por el cliente del usuario autenticado
        client_id = self.get_client_from_request(self.request)
        return queryset.filter(client_id=client_id)
    
    def get_serializer_class(self):
        """Retornar el serializer apropiado según la acción"""
        if self.action == 'create':
            return MarketplaceCredentialsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MarketplaceCredentialsUpdateSerializer
        return ClientMarketplaceCredentialsSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Crear o actualizar credenciales de marketplace (upsert)
        Si ya existen credenciales para el mismo marketplace_type, las actualiza
        """
        try:
            with transaction.atomic():
                # Validar que el marketplace_type esté presente
                marketplace_type = request.data.get('marketplace_type')
                if not marketplace_type:
                    return Response({
                        'error': 'marketplace_type_required',
                        'message': 'Debe especificar el tipo de marketplace',
                        'valid_types': ['amazon', 'mercadolibre', 'shopify', 'ebay', 'walmart']
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validar que el tipo de marketplace sea válido
                valid_types = ['amazon', 'mercadolibre', 'shopify', 'ebay', 'walmart']
                if marketplace_type not in valid_types:
                    return Response({
                        'error': 'invalid_marketplace_type',
                        'message': f'Tipo de marketplace inválido. Tipos válidos: {", ".join(valid_types)}',
                        'received_type': marketplace_type
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Obtener el client_id del JWT
                client_id = self.get_client_from_request(request)
                
                # Buscar credenciales existentes para este cliente y marketplace
                existing_credential = ClientMarketplaceCredentials.objects.filter(
                    client_id=client_id,
                    marketplace_type=marketplace_type
                ).first()
                
                if existing_credential:
                    # Actualizar credenciales existentes
                    serializer = MarketplaceCredentialsUpdateSerializer(
                        existing_credential, 
                        data=request.data, 
                        partial=True,
                        context={'request': request}
                    )
                    serializer.is_valid(raise_exception=True)
                    instance = serializer.save()
                    
                    return Response({
                        'status': 'success',
                        'message': f'Credenciales de {marketplace_type} actualizadas exitosamente',
                        'action': 'updated',
                        'data': ClientMarketplaceCredentialsSerializer(instance).data
                    }, status=status.HTTP_200_OK)
                else:
                    # Crear nuevas credenciales
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    instance = serializer.save()
                    
                    return Response({
                        'status': 'success',
                        'message': f'Credenciales de {marketplace_type} creadas exitosamente',
                        'action': 'created',
                        'data': ClientMarketplaceCredentialsSerializer(instance).data
                    }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'upsert_failed',
                'message': f'Error al crear/actualizar credenciales: {str(e)}'
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
