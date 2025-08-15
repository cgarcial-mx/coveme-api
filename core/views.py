from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import logout
from .serializers import LoginSerializer, UserSerializer, RefreshTokenSerializer, LogoutSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint that returns JWT tokens and user info"""
    print("🔍 Request data:", request.data)
    
    serializer = LoginSerializer(data=request.data)
    print(" Serializer created")
    
    is_valid = serializer.is_valid()
    print("🔍 Serializer is_valid:", is_valid)
    
    if not is_valid:
        print("❌ Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    print("✅ Serializer is valid!")
    user = serializer.validated_data['user']
    print(" User found:", user.username, user.email)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # Add custom claims to access token
    access_token['user_id'] = user.id
    access_token['username'] = user.username
    access_token['role'] = user.role
    access_token['client_id'] = user.client.id if user.client else None
    
    # Get user permissions for JWT
    user_permissions = user.get_jwt_permissions()
    access_token['permissions'] = user_permissions
    
    return Response({
        'access': str(access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'permissions': user_permissions
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint that blacklists the refresh token"""
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile and permissions"""
    user = request.user
    permissions = user.get_jwt_permissions()
    
    return Response({
        'user': UserSerializer(user).data,
        'permissions': permissions
    })

class CustomTokenRefreshView(TokenRefreshView):
    """Custom refresh token view that adds user info"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from the new access token
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(response.data['access'])
            user_id = access_token['user_id']
            
            try:
                user = User.objects.get(id=user_id)
                user_permissions = user.get_jwt_permissions()
                
                response.data['user'] = UserSerializer(user).data
                response.data['permissions'] = user_permissions
            except User.DoesNotExist:
                pass
        
        return response
