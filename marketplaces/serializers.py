from rest_framework import serializers
from .models import (
    SaleChannel, MarketplaceListing, ProductMatch, ProductPriceHistory, 
    ProductTracing, ProductTracingHistory
)
from .schemas import (
    SaleChannelSchema, MarketplaceListingSchema, ProductMatchSchema,
    ProductPriceHistorySchema, ProductTracingSchema, ProductTracingHistorySchema,
    MarketplaceListingCreateSchema, MarketplaceListingUpdateSchema,
    ProductMatchCreateSchema, ProductMatchUpdateSchema,
    ProductTracingCreateSchema, ProductTracingUpdateSchema
)
from core.pydantic_serializer import PydanticModelSerializer


class SaleChannelSerializer(PydanticModelSerializer):
    class Meta:
        model = SaleChannel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=SaleChannelSchema,
            **kwargs
        )


class MarketplaceListingSerializer(PydanticModelSerializer):
    class Meta:
        model = MarketplaceListing
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=MarketplaceListingSchema,
            pydantic_create_schema=MarketplaceListingCreateSchema,
            pydantic_update_schema=MarketplaceListingUpdateSchema,
            **kwargs
        )


class ProductMatchSerializer(PydanticModelSerializer):
    class Meta:
        model = ProductMatch
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProductMatchSchema,
            pydantic_create_schema=ProductMatchCreateSchema,
            pydantic_update_schema=ProductMatchUpdateSchema,
            **kwargs
        )


class ProductPriceHistorySerializer(PydanticModelSerializer):
    class Meta:
        model = ProductPriceHistory
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProductPriceHistorySchema,
            **kwargs
        )


class ProductTracingSerializer(PydanticModelSerializer):
    class Meta:
        model = ProductTracing
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProductTracingSchema,
            pydantic_create_schema=ProductTracingCreateSchema,
            pydantic_update_schema=ProductTracingUpdateSchema,
            **kwargs
        )


class ProductTracingHistorySerializer(PydanticModelSerializer):
    class Meta:
        model = ProductTracingHistory
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProductTracingHistorySchema,
            **kwargs
        )
