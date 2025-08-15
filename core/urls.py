from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login_view, name='auth_login'),
    path('auth/logout/', views.logout_view, name='auth_logout'),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view(), name='auth_refresh'),
    path('auth/profile/', views.user_profile, name='auth_profile'),
    
    # Standard JWT endpoints (optional)
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
