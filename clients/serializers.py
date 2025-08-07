from rest_framework import serializers
from .models import Client, ClientMarketplaceCredentials
from core.schemas import ClientSchema, ClientMarketplaceCredentialsSchema
from core.pydantic_serializer import PydanticModelSerializer


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


class ClientMarketplaceCredentialsSerializer(PydanticModelSerializer):
    class Meta:
        model = ClientMarketplaceCredentials
        fields = '__all__'
        extra_kwargs = {
            'credentials': {'write_only': True}
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ClientMarketplaceCredentialsSchema,
            **kwargs
        )
