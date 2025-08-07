from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MarketplaceListing, ProductMatch, ProductPriceHistory, ProductTracing, ProductTracingHistory
from .serializers import (
    MarketplaceListingSerializer, ProductMatchSerializer, ProductPriceHistorySerializer,
    ProductTracingSerializer, ProductTracingHistorySerializer
)

class MarketplaceListingViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.all()
    serializer_class = MarketplaceListingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'marketplace_type', 'status']

class ProductMatchViewSet(viewsets.ModelViewSet):
    queryset = ProductMatch.objects.all()
    serializer_class = ProductMatchSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'product', 'match_type', 'status']
    
    @action(detail=False, methods=['post'])
    def start_sync(self, request):
        client_id = request.data.get('client_id')
        marketplace_types = request.data.get('marketplace_types', [])
        
        # Aquí implementarías la lógica de sincronización
        # y matching automático de productos
        
        return Response({
            'sync_id': 'sync_123456',
            'status': 'started',
            'marketplaces': marketplace_types
        })
    
    @action(detail=False)
    def manual_reviews(self, request):
        # Obtener coincidencias que necesitan revisión manual
        reviews = ProductMatch.objects.filter(
            confidence_score__range=(0.6, 0.85),
            reviewed_by__isnull=True,
            status='active'
        )
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

class ProductPriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductPriceHistory.objects.all()
    serializer_class = ProductPriceHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'product', 'marketplace_listing']

class ProductTracingViewSet(viewsets.ModelViewSet):
    queryset = ProductTracing.objects.all()
    serializer_class = ProductTracingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'product', 'marketplace_type', 'is_active']

class ProductTracingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductTracingHistory.objects.all()
    serializer_class = ProductTracingHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'product_tracing']
