from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

class ClientContextMixin:
    """
    Mixin para extraer automáticamente el client_id del JWT del usuario autenticado
    """
    
    def get_client_from_request(self, request):
        """Extraer el client_id del JWT del usuario autenticado"""
        if not request.user.is_authenticated:
            raise PermissionDenied("Usuario no autenticado")
        
        # Obtener el client_id del JWT o del usuario
        client_id = None
        
        # Intentar obtener del JWT primero
        if hasattr(request, 'auth') and request.auth:
            try:
                client_id = request.auth.get('client_id')
            except (AttributeError, KeyError):
                pass
        
        # Si no está en el JWT, obtener del usuario
        if not client_id and hasattr(request.user, 'client'):
            client_id = request.user.client.id if request.user.client else None
        
        if not client_id:
            raise PermissionDenied("Usuario no tiene un cliente asociado")
        
        print("client_id", client_id)

        return client_id
    
    def validate_client_permission(self, request, client_id):
        """Validar que el usuario tenga permisos para el cliente especificado"""
        user_client_id = self.get_client_from_request(request)
        
        # Si el usuario es superuser o admin global, puede acceder a cualquier cliente
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        
        # Verificar que el usuario solo pueda acceder a su propio cliente
        if user_client_id != client_id:
            raise PermissionDenied("No tienes permisos para acceder a este cliente")
        
        return True
