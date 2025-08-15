"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clients.views import ClientViewSet, ClientMarketplaceCredentialsViewSet
from products.views import ProductViewSet, BrandViewSet, SubBrandViewSet, ProviderViewSet
from marketplaces.views import (
    MarketplaceListingViewSet, ProductMatchViewSet, ProductPriceHistoryViewSet,
    ProductTracingViewSet, ProductTracingHistoryViewSet
)
from orders.views import OrderViewSet, OrderItemViewSet
from feedback.views import CustomerFeedbackViewSet
from analytics.views import ApiLogViewSet

# Importar las vistas de autenticación (NO CoreViewSet)
from core.views import login_view, logout_view, user_profile
from rest_framework_simplejwt.views import TokenRefreshView

# Create router and register viewsets
router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'marketplace-credentials', ClientMarketplaceCredentialsViewSet)
router.register(r'products', ProductViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'subbrands', SubBrandViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'marketplace-listings', MarketplaceListingViewSet)
router.register(r'product-matches', ProductMatchViewSet)
router.register(r'price-history', ProductPriceHistoryViewSet)
router.register(r'product-tracing', ProductTracingViewSet)
router.register(r'tracing-history', ProductTracingHistoryViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'customer-feedback', CustomerFeedbackViewSet)
router.register(r'api-logs', ApiLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    
    # 🔐 Endpoints de Autenticación JWT
    path('api/v1/auth/login/', login_view, name='auth_login'),
    path('api/v1/auth/logout/', logout_view, name='auth_logout'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('api/v1/auth/profile/', user_profile, name='auth_profile'),
    
    path('api-auth/', include('rest_framework.urls')),
]
