from rest_framework import serializers
from .models import ApiLog
from .schemas import ApiLogSchema, ApiLogCreateSchema, ApiLogUpdateSchema
from core.pydantic_serializer import PydanticModelSerializer


class ApiLogSerializer(PydanticModelSerializer):
    class Meta:
        model = ApiLog
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=ApiLogSchema,
            pydantic_create_schema=ApiLogCreateSchema,
            pydantic_update_schema=ApiLogUpdateSchema,
            **kwargs
        )
