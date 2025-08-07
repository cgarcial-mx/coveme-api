from rest_framework import serializers
from .models import CustomerFeedback
from .schemas import (
    CustomerFeedbackSchema, CustomerFeedbackCreateSchema, CustomerFeedbackUpdateSchema
)
from core.pydantic_serializer import PydanticModelSerializer


class CustomerFeedbackSerializer(PydanticModelSerializer):
    class Meta:
        model = CustomerFeedback
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            pydantic_schema=CustomerFeedbackSchema,
            pydantic_create_schema=CustomerFeedbackCreateSchema,
            pydantic_update_schema=CustomerFeedbackUpdateSchema,
            **kwargs
        )
