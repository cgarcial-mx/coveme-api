from rest_framework import serializers
from .models import Brand, SubBrand, Provider, Product
from .schemas import (
    BrandSchema, SubBrandSchema, ProviderSchema, ProductSchema,
    ProductCreateSchema, ProductUpdateSchema
)
from core.pydantic_serializer import PydanticModelSerializer


class BrandSerializer(PydanticModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=BrandSchema,
            **kwargs
        )


class SubBrandSerializer(PydanticModelSerializer):
    class Meta:
        model = SubBrand
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=SubBrandSchema,
            **kwargs
        )


class ProviderSerializer(PydanticModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProviderSchema,
            **kwargs
        )


class ProductSerializer(PydanticModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ProductSchema,
            pydantic_create_schema=ProductCreateSchema,
            pydantic_update_schema=ProductUpdateSchema,
            **kwargs
        )
