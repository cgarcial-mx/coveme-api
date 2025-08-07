from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
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
