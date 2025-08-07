from rest_framework import serializers
from .models import Order, OrderItem
from .schemas import (
    OrderSchema, OrderItemSchema, OrderWithItemsSchema,
    OrderCreateSchema, OrderUpdateSchema,
    OrderItemCreateSchema, OrderItemUpdateSchema
)
from core.pydantic_serializer import PydanticModelSerializer


class OrderItemSerializer(PydanticModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=OrderItemSchema,
            pydantic_create_schema=OrderItemCreateSchema,
            pydantic_update_schema=OrderItemUpdateSchema,
            **kwargs
        )


class OrderSerializer(PydanticModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=OrderWithItemsSchema,
            pydantic_create_schema=OrderCreateSchema,
            pydantic_update_schema=OrderUpdateSchema,
            **kwargs
        )
