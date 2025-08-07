from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Brand, SubBrand, Provider
from .serializers import ProductSerializer, BrandSerializer, SubBrandSerializer, ProviderSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'brand', 'provider', 'category']

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client']

class SubBrandViewSet(viewsets.ModelViewSet):
    queryset = SubBrand.objects.all()
    serializer_class = SubBrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client', 'brand']

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client']
