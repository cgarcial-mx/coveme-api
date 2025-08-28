from typing import TypeVar, Type, Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError
from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
M = TypeVar('M', bound=models.Model)


def pydantic_to_dict(pydantic_obj: BaseModel) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary, handling nested objects and relationships
    """
    if pydantic_obj is None:
        return {}
    
    data = pydantic_obj.model_dump()
    
    # Remove None values for optional fields
    cleaned_data = {}
    for key, value in data.items():
        if value is not None:
            cleaned_data[key] = value
    
    return cleaned_data


def dict_to_pydantic(data: Dict[str, Any], pydantic_class: Type[T]) -> T:
    """
    Convert a dictionary to a Pydantic model
    """
    try:
        return pydantic_class(**data)
    except ValidationError as e:
        logger.error(f"Validation error converting dict to {pydantic_class.__name__}: {e}")
        raise


def django_to_pydantic(django_obj: models.Model, pydantic_class: Type[T]) -> T:
    """
    Convert a Django model instance to a Pydantic model
    """
    if django_obj is None:
        raise ValueError("Django object cannot be None")
    
    # Convert Django model to dict
    data = {}
    for field in django_obj._meta.fields:
        value = getattr(django_obj, field.name)
        if hasattr(value, 'id'):  # Foreign key
            data[f"{field.name}_id"] = value.id
        else:
            data[field.name] = value
    
    # Handle related fields - check for common patterns
    related_fields = ['brand', 'subbrand', 'provider', 'client', 'created_by']
    for field_name in related_fields:
        if hasattr(django_obj, field_name):
            related_obj = getattr(django_obj, field_name)
            if related_obj is not None:
                # Add the related object ID if not already present
                if f"{field_name}_id" not in data:
                    data[f"{field_name}_id"] = related_obj.id
                
                # Add the related object name if it exists
                if hasattr(related_obj, 'name'):
                    data[f"{field_name}_name"] = related_obj.name
    
    # Check for properties that might contain related names
    property_fields = ['brand_name', 'subbrand_name', 'provider_name']
    for prop_name in property_fields:
        if hasattr(django_obj, prop_name):
            try:
                prop_value = getattr(django_obj, prop_name)
                if prop_value is not None:
                    data[prop_name] = prop_value
            except Exception:
                # Skip if property access fails
                pass
    
    return dict_to_pydantic(data, pydantic_class)


def pydantic_to_django(pydantic_obj: BaseModel, django_model: Type[M], instance: Optional[M] = None) -> M:
    """
    Convert a Pydantic model to a Django model instance
    """
    if pydantic_obj is None:
        raise ValueError("Pydantic object cannot be None")
    
    data = pydantic_to_dict(pydantic_obj)
    
    # Remove fields that don't exist in Django model
    django_fields = {field.name for field in django_model._meta.fields}
    cleaned_data = {k: v for k, v in data.items() if k in django_fields}
    
    if instance is None:
        # Create new instance
        instance = django_model(**cleaned_data)
    else:
        # Update existing instance
        for key, value in cleaned_data.items():
            setattr(instance, key, value)
    
    return instance


def validate_pydantic_data(data: Dict[str, Any], pydantic_class: Type[T]) -> T:
    """
    Validate data against a Pydantic schema
    """
    try:
        return pydantic_class(**data)
    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e}")
        raise


def bulk_django_to_pydantic(django_objects: List[models.Model], pydantic_class: Type[T]) -> List[T]:
    """
    Convert a list of Django model instances to Pydantic models
    """
    return [django_to_pydantic(obj, pydantic_class) for obj in django_objects]


def handle_pydantic_validation_error(error: ValidationError) -> Dict[str, Any]:
    """
    Convert Pydantic validation errors to a user-friendly format
    """
    error_messages = {}
    for error_detail in error.errors():
        field = error_detail['loc'][0] if error_detail['loc'] else 'unknown'
        message = error_detail['msg']
        error_messages[field] = message
    
    return {
        'error': 'Validation failed',
        'details': error_messages
    }


def safe_pydantic_conversion(data: Dict[str, Any], pydantic_class: Type[T]) -> Optional[T]:
    """
    Safely convert data to Pydantic model, returning None if validation fails
    """
    try:
        return pydantic_class(**data)
    except ValidationError:
        return None
