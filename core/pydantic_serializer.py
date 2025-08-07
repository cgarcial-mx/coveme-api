from rest_framework import serializers
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError
from .pydantic_utils import django_to_pydantic, pydantic_to_django, handle_pydantic_validation_error
import logging

logger = logging.getLogger(__name__)


class PydanticModelSerializer(serializers.ModelSerializer):
    """
    A Django REST Framework serializer that integrates with Pydantic schemas
    """
    
    def __init__(self, *args, **kwargs):
        self.pydantic_schema = kwargs.pop('pydantic_schema', None)
        self.pydantic_create_schema = kwargs.pop('pydantic_create_schema', None)
        self.pydantic_update_schema = kwargs.pop('pydantic_update_schema', None)
        super().__init__(*args, **kwargs)
    
    def validate(self, attrs):
        """
        Validate data using Pydantic schema
        """
        if self.instance is None and self.pydantic_create_schema:
            # Creating new instance
            schema_class = self.pydantic_create_schema
        elif self.instance is not None and self.pydantic_update_schema:
            # Updating existing instance
            schema_class = self.pydantic_update_schema
        elif self.pydantic_schema:
            # Use default schema
            schema_class = self.pydantic_schema
        else:
            # Fall back to Django validation
            return super().validate(attrs)
        
        try:
            # Validate with Pydantic
            pydantic_obj = schema_class(**attrs)
            return pydantic_obj.model_dump()
        except ValidationError as e:
            error_detail = handle_pydantic_validation_error(e)
            raise serializers.ValidationError(error_detail['details'])
    
    def to_representation(self, instance):
        """
        Convert Django model to Pydantic schema for serialization
        """
        if self.pydantic_schema:
            try:
                pydantic_obj = django_to_pydantic(instance, self.pydantic_schema)
                return pydantic_obj.model_dump()
            except Exception as e:
                logger.error(f"Error converting Django model to Pydantic: {e}")
                # Fall back to default serialization
                return super().to_representation(instance)
        else:
            return super().to_representation(instance)
    
    def create(self, validated_data):
        """
        Create Django model instance using Pydantic validation
        """
        if self.pydantic_create_schema:
            try:
                pydantic_obj = self.pydantic_create_schema(**validated_data)
                instance = pydantic_to_django(pydantic_obj, self.Meta.model)
                instance.save()
                return instance
            except Exception as e:
                logger.error(f"Error creating Django model with Pydantic: {e}")
                # Fall back to default creation
                return super().create(validated_data)
        else:
            return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update Django model instance using Pydantic validation
        """
        if self.pydantic_update_schema:
            try:
                # Merge existing data with updates
                existing_data = {}
                for field in instance._meta.fields:
                    value = getattr(instance, field.name)
                    if hasattr(value, 'id'):  # Foreign key
                        existing_data[f"{field.name}_id"] = value.id
                    else:
                        existing_data[field.name] = value
                
                # Update with new data
                existing_data.update(validated_data)
                
                pydantic_obj = self.pydantic_update_schema(**existing_data)
                updated_instance = pydantic_to_django(pydantic_obj, self.Meta.model, instance)
                updated_instance.save()
                return updated_instance
            except Exception as e:
                logger.error(f"Error updating Django model with Pydantic: {e}")
                # Fall back to default update
                return super().update(instance, validated_data)
        else:
            return super().update(instance, validated_data)


class PydanticListSerializer(serializers.ListSerializer):
    """
    List serializer that works with Pydantic schemas
    """
    
    def __init__(self, *args, **kwargs):
        self.pydantic_schema = kwargs.pop('pydantic_schema', None)
        super().__init__(*args, **kwargs)
    
    def to_representation(self, data):
        """
        Convert list of Django models to Pydantic schemas
        """
        if self.pydantic_schema:
            try:
                pydantic_objects = []
                for item in data:
                    pydantic_obj = django_to_pydantic(item, self.pydantic_schema)
                    pydantic_objects.append(pydantic_obj.model_dump())
                return pydantic_objects
            except Exception as e:
                logger.error(f"Error converting Django models to Pydantic: {e}")
                # Fall back to default serialization
                return super().to_representation(data)
        else:
            return super().to_representation(data)


def create_pydantic_serializer(
    model_class,
    pydantic_schema: Type[BaseModel],
    pydantic_create_schema: Optional[Type[BaseModel]] = None,
    pydantic_update_schema: Optional[Type[BaseModel]] = None,
    fields: Optional[List[str]] = None,
    read_only_fields: Optional[List[str]] = None,
    extra_kwargs: Optional[Dict[str, Any]] = None
) -> Type[PydanticModelSerializer]:
    """
    Factory function to create a PydanticModelSerializer
    """
    
    class Meta:
        model = model_class
        if fields:
            fields = fields
        if read_only_fields:
            read_only_fields = read_only_fields
        if extra_kwargs:
            extra_kwargs = extra_kwargs
    
    serializer_class = type(
        f'{model_class.__name__}PydanticSerializer',
        (PydanticModelSerializer,),
        {
            'Meta': Meta,
            'pydantic_schema': pydantic_schema,
            'pydantic_create_schema': pydantic_create_schema,
            'pydantic_update_schema': pydantic_update_schema,
        }
    )
    
    return serializer_class
