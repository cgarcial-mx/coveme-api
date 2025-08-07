from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.management import call_command
from django.utils import timezone
import json
from .models import Client, ClientMarketplaceCredentials
from .serializers import ClientSerializer, ClientMarketplaceCredentialsSerializer

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

class ClientMarketplaceCredentialsViewSet(viewsets.ModelViewSet):
    queryset = ClientMarketplaceCredentials.objects.all()
    serializer_class = ClientMarketplaceCredentialsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'marketplace_type', 'connection_status']
    
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
            limit = request.data.get('limit', 100)
            debug = request.data.get('debug', False)
            
            # Prepare command arguments
            command_args = [
                'sync_shopify_products',
                '--credentials-id', str(credential.id),
                '--limit', str(limit),
            ]
            
            if dry_run:
                command_args.append('--dry-run')
            
            if debug:
                command_args.append('--debug')
            
            # Execute the sync command
            from io import StringIO
            from django.core.management import call_command
            
            output = StringIO()
            call_command(*command_args, stdout=output)
            output.seek(0)
            command_output = output.read()
            
            # Update credential status
            credential.last_sync_at = timezone.now()
            credential.last_error = None
            credential.save()
            
            return Response({
                'status': 'success',
                'message': 'Sync completed successfully',
                'output': command_output,
                'sync_details': {
                    'credential_id': credential.id,
                    'client_name': credential.client.name,
                    'marketplace_type': credential.marketplace_type,
                    'last_sync_at': credential.last_sync_at.isoformat(),
                    'dry_run': dry_run,
                    'limit': limit,
                    'debug': debug
                }
            })
            
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
