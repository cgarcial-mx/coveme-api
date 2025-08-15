from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.mixins import ClientContextMixin
from .models import MarketplaceListing, ProductMatch, ProductPriceHistory, ProductTracing, ProductTracingHistory
from .serializers import (
    MarketplaceListingSerializer, ProductMatchSerializer, ProductPriceHistorySerializer,
    ProductTracingSerializer, ProductTracingHistorySerializer
)

class MarketplaceListingViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.all()
    serializer_class = MarketplaceListingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marketplace_type', 'status']  # Removed 'client' - auto-filtered
    
    def get_queryset(self):
        """Automatically filter listings by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return MarketplaceListing.objects.filter(client_id=client_id)

class ProductMatchViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = ProductMatch.objects.all()
    serializer_class = ProductMatchSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'match_type', 'status']  # Removed 'client' - auto-filtered
    
    def get_queryset(self):
        """Automatically filter product matches by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return ProductMatch.objects.filter(client_id=client_id)
    
    @action(detail=False, methods=['post'])
    def start_sync(self, request):
        client_id = self.get_client_from_request(request)
        marketplace_types = request.data.get('marketplace_types', [])
        
        # Aquí implementarías la lógica de sincronización
        # y matching automático de productos
        
        return Response({
            'sync_id': 'sync_123456',
            'status': 'started',
            'marketplaces': marketplace_types,
            'client_id': client_id
        })
    
    @action(detail=False)
    def manual_reviews(self, request):
        # Obtener coincidencias que necesitan revisión manual
        client_id = self.get_client_from_request(request)
        reviews = ProductMatch.objects.filter(
            client_id=client_id,
            confidence_score__range=(0.6, 0.85),
            reviewed_by__isnull=True,
            status='active'
        )
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

class ProductPriceHistoryViewSet(ClientContextMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ProductPriceHistory.objects.all()
    serializer_class = ProductPriceHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'marketplace_listing']  # Removed 'client' - auto-filtered
    
    def get_queryset(self):
        """Automatically filter price history by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return ProductPriceHistory.objects.filter(client_id=client_id)

class ProductTracingViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = ProductTracing.objects.all()
    serializer_class = ProductTracingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'marketplace_type', 'is_active']  # Removed 'client' - auto-filtered
    
    def get_queryset(self):
        """Automatically filter product tracing by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return ProductTracing.objects.filter(client_id=client_id)

class ProductTracingHistoryViewSet(ClientContextMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ProductTracingHistory.objects.all()
    serializer_class = ProductTracingHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_tracing']  # Removed 'client' - auto-filtered
    
    def get_queryset(self):
        """Automatically filter tracing history by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return ProductTracingHistory.objects.filter(client_id=client_id)
