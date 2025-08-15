from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.mixins import ClientContextMixin
from .models import Product, Brand, SubBrand, Provider
from .serializers import ProductSerializer, BrandSerializer, SubBrandSerializer, ProviderSerializer

class ProductViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()  # Fallback para basename
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand', 'provider', 'category']  # Removido 'client' ya que se filtra automáticamente
    
    def get_queryset(self):
        """Filtrar productos por el cliente del usuario autenticado"""
        client_id = self.get_client_from_request(self.request)
        return Product.objects.filter(client_id=client_id)

class BrandViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = Brand.objects.all()  # Fallback para basename
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []  # Removido 'client'
    
    def get_queryset(self):
        client_id = self.get_client_from_request(self.request)
        return Brand.objects.filter(client_id=client_id)

class SubBrandViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = SubBrand.objects.all()  # Fallback para basename
    serializer_class = SubBrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand']  # Removido 'client' ya que se filtra automáticamente
    
    def get_queryset(self):
        client_id = self.get_client_from_request(self.request)
        return SubBrand.objects.filter(client_id=client_id)

class ProviderViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = Provider.objects.all()  # Fallback para basename
    serializer_class = ProviderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []  # Removido 'client' ya que se filtra automáticamente
    
    def get_queryset(self):
        client_id = self.get_client_from_request(self.request)
        return Provider.objects.filter(client_id=client_id)
