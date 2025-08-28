from rest_framework import serializers
from .models import Client, ClientMarketplaceCredentials
from core.schemas import ClientSchema, ClientMarketplaceCredentialsSchema
from core.pydantic_serializer import PydanticModelSerializer
from core.mixins import ClientContextMixin


class ClientSerializer(PydanticModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ClientSchema,
            **kwargs
        )


class ClientMarketplaceCredentialsSerializer(PydanticModelSerializer, ClientContextMixin):
    """Serializer para credenciales de marketplace con validación Pydantic"""
    
    class Meta:
        model = ClientMarketplaceCredentials
        fields = [
            'id', 'client', 'marketplace_type', 'name', 'marketplace_name', 
            'credentials', 'settings', 'webhook_url', 'connection_status', 
            'last_sync_at', 'last_error', 'created_by', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'connection_status', 'last_sync_at', 'last_error', 'created_by', 'created_at', 'updated_at']
        pydantic_schema=ClientMarketplaceCredentialsSchema,
        extra_kwargs = {
            'client': {'read_only': True}
        }
    
    def validate(self, data):
        """Validación personalizada"""
        # Verificar que no haya duplicados
        marketplace_type = data.get('marketplace_type')
        name = data.get('name')
        
        if marketplace_type and name and 'client_id' in data:
            existing_credential = ClientMarketplaceCredentials.objects.filter(
                client_id=data['client_id'],
                marketplace_type=marketplace_type,
                name=name
            ).exclude(pk=getattr(self.instance, 'pk', None)).first()
            
            if existing_credential:
                raise serializers.ValidationError(
                    f"Ya existen credenciales con el nombre '{name}' para {marketplace_type}"
                )
        
        return data
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ClientMarketplaceCredentialsSchema,
            **kwargs
        )
    
    def validate_credentials(self, value):
        """Validar credenciales según el tipo de marketplace"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Las credenciales deben ser un objeto JSON")
        
        # Obtener el tipo de marketplace del contexto
        marketplace_type = None
        if self.context.get('request') and self.context['request'].data:
            marketplace_type = self.context['request'].data.get('marketplace_type')
        
        if not marketplace_type:
            raise serializers.ValidationError("Debe especificar el tipo de marketplace")
        
        # Validar según el tipo de marketplace
        try:
            if marketplace_type == 'amazon':
                self._validate_aws_credentials(value)
            elif marketplace_type == 'mercadolibre':
                self._validate_mercadolibre_credentials(value)
            elif marketplace_type == 'shopify':
                self._validate_shopify_credentials(value)
            else:
                # Para otros marketplaces, solo validar que sea un JSON válido
                pass
        except Exception as e:
            raise serializers.ValidationError(f"Credenciales inválidas para {marketplace_type}: {str(e)}")
        
        return value
    
    def _validate_aws_credentials(self, credentials):
        """Validar credenciales de AWS"""
        required_fields = ['aws_access_key_id', 'aws_secret_access_key', 'aws_region', 'marketplace_id', 'seller_id']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
    
    def _validate_mercadolibre_credentials(self, credentials):
        """Validar credenciales de Mercado Libre"""
        required_fields = ['access_token', 'refresh_token', 'user_id', 'country_code', 'site_id']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
    
    def _validate_shopify_credentials(self, credentials):
        """Validar credenciales de Shopify"""
        required_fields = ['shop_url', 'access_token']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
        
        # Agregar automáticamente la versión de la API si no está presente
        if 'api_version' not in credentials:
            credentials['api_version'] = '2024-01'
    
    def validate(self, data):
        """Validación del modelo completo"""
        # El client_id se asigna automáticamente desde el JWT
        request = self.context.get('request')
        if request:
            client_id = self.get_client_from_request(request)
            data['client_id'] = client_id
        
        # Validar que el nombre sea único para este cliente y tipo de marketplace
        marketplace_type = data.get('marketplace_type')
        name = data.get('name')
        
        if marketplace_type and name and 'client_id' in data:
            existing_credential = ClientMarketplaceCredentials.objects.filter(
                client_id=data['client_id'],
                marketplace_type=marketplace_type,
                name=name
            ).first()
            
            if existing_credential:
                raise serializers.ValidationError({
                    'name': f"Ya existe una credencial con el nombre '{name}' para {marketplace_type}"
                })
        
        return data

class MarketplaceCredentialsCreateSerializer(serializers.ModelSerializer, ClientContextMixin):
    """Serializer específico para crear credenciales sin client_id"""
    
    class Meta:
        model = ClientMarketplaceCredentials
        fields = ['marketplace_type', 'name', 'marketplace_name', 'credentials', 'settings', 'webhook_url', 'is_active']
        extra_kwargs = {
            'client': {'read_only': True},  # Se asigna automáticamente
            'name': {'required': True}
        }
    
    def validate_credentials(self, value):
        """Validar credenciales según el tipo de marketplace"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Las credenciales deben ser un objeto JSON")
        
        # Obtener el tipo de marketplace del contexto
        marketplace_type = None
        if self.context.get('request') and self.context['request'].data:
            marketplace_type = self.context['request'].data.get('marketplace_type')
        
        if not marketplace_type:
            raise serializers.ValidationError("Debe especificar el tipo de marketplace")
        
        # Validar según el tipo de marketplace
        try:
            if marketplace_type == 'amazon':
                self._validate_aws_credentials(value)
            elif marketplace_type == 'mercadolibre':
                self._validate_mercadolibre_credentials(value)
            elif marketplace_type == 'shopify':
                self._validate_shopify_credentials(value)
            else:
                # Para otros marketplaces, solo validar que sea un JSON válido
                pass
        except Exception as e:
            raise serializers.ValidationError(f"Credenciales inválidas para {marketplace_type}: {str(e)}")
        
        return value
    
    def _validate_aws_credentials(self, credentials):
        """Validar credenciales de AWS"""
        required_fields = ['aws_access_key_id', 'aws_secret_access_key', 'aws_region', 'marketplace_id', 'seller_id']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
    
    def _validate_mercadolibre_credentials(self, credentials):
        """Validar credenciales de Mercado Libre"""
        required_fields = ['access_token', 'refresh_token', 'user_id', 'country_code', 'site_id']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
    
    def _validate_shopify_credentials(self, credentials):
        """Validar credenciales de Shopify"""
        required_fields = ['shop_url', 'access_token']
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                raise serializers.ValidationError(f"Campo requerido: {field}")
        
        # Agregar automáticamente la versión de la API si no está presente
        if 'api_version' not in credentials:
            credentials['api_version'] = '2024-01'
    
    def validate(self, data):
        """Validación del modelo completo"""
        # El client_id se asigna automáticamente desde el JWT
        request = self.context.get('request')
        if request:
            client_id = self.get_client_from_request(request)
            data['client_id'] = client_id
        
        # Validar que el nombre sea único para este cliente y tipo de marketplace
        marketplace_type = data.get('marketplace_type')
        name = data.get('name')
        
        if marketplace_type and name and 'client_id' in data:
            existing_credential = ClientMarketplaceCredentials.objects.filter(
                client_id=data['client_id'],
                marketplace_type=marketplace_type,
                name=name
            ).first()
            
            if existing_credential:
                raise serializers.ValidationError({
                    'name': f"Ya existe una credencial con el nombre '{name}' para {marketplace_type}"
                })
        
        return data

class MarketplaceCredentialsUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar credenciales"""
    
    class Meta:
        model = ClientMarketplaceCredentials
        fields = ['name', 'marketplace_name', 'credentials', 'settings', 'webhook_url', 'is_active']
    
    def validate(self, data):
        """Validación personalizada para actualización"""
        # Verificar que el nombre sea único si se está cambiando
        if 'name' in data and self.instance:
            existing_credential = ClientMarketplaceCredentials.objects.filter(
                client=self.instance.client,
                marketplace_type=self.instance.marketplace_type,
                name=data['name']
            ).exclude(pk=self.instance.pk).first()
            
            if existing_credential:
                raise serializers.ValidationError({
                    'name': f"Ya existe una credencial con el nombre '{data['name']}' para {self.instance.get_marketplace_type_display()}"
                })
        
        return data
