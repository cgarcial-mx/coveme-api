# Pydantic Integration in Coveme API

This document describes the Pydantic integration in the Coveme API project, which provides robust data validation, serialization, and type safety.

## Overview

Pydantic has been integrated throughout the project to provide:

- **Data Validation**: Automatic validation of incoming and outgoing data
- **Type Safety**: Strong typing for all data structures
- **Serialization**: Consistent data serialization/deserialization
- **Error Handling**: Detailed validation error messages
- **Documentation**: Auto-generated API documentation

## Architecture

### Core Components

1. **Base Schemas** (`core/schemas.py`)
   - `TimestampedSchema`: Base schema with timestamps
   - `UserSchema`: User data schema
   - `ClientSchema`: Client data schema
   - `ClientMarketplaceCredentialsSchema`: Marketplace credentials schema

2. **Utility Functions** (`core/pydantic_utils.py`)
   - `django_to_pydantic()`: Convert Django models to Pydantic schemas
   - `pydantic_to_django()`: Convert Pydantic schemas to Django models
   - `validate_pydantic_data()`: Validate data against schemas
   - `handle_pydantic_validation_error()`: Format validation errors

3. **Custom Serializers** (`core/pydantic_serializer.py`)
   - `PydanticModelSerializer`: DRF serializer with Pydantic integration
   - `PydanticListSerializer`: List serializer with Pydantic support

4. **Middleware** (`core/pydantic_middleware.py`)
   - `PydanticValidationMiddleware`: Handle validation errors
   - `PydanticRequestMiddleware`: Validate incoming requests

5. **Settings** (`core/pydantic_settings.py`)
   - Configuration for Pydantic behavior

## App-Specific Schemas

### Products (`products/schemas.py`)

```python
from products.schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema

# Create a new product
product_data = {
    "client_id": 1,
    "internal_sku": "PROD-001",
    "title": "Test Product",
    "description": "A test product",
    "cost": Decimal("10.99")
}

# Validate with Pydantic
product_schema = ProductCreateSchema(**product_data)
```

### Orders (`orders/schemas.py`)

```python
from orders.schemas import OrderCreateSchema, OrderWithItemsSchema

# Create an order with items
order_data = {
    "client_id": 1,
    "marketplace_type": "amazon",
    "marketplace_order_id": "AMZ-123456",
    "order_total": Decimal("99.99"),
    "items": [
        {
            "client_id": 1,
            "order_id": 1,
            "quantity": Decimal("2"),
            "unit_price": Decimal("49.99")
        }
    ]
}

order_schema = OrderWithItemsSchema(**order_data)
```

### Marketplaces (`marketplaces/schemas.py`)

```python
from marketplaces.schemas import MarketplaceListingCreateSchema

# Create a marketplace listing
listing_data = {
    "client_id": 1,
    "marketplace_type": "mercadolibre",
    "marketplace_id": "ML123456",
    "title": "Product in Marketplace",
    "price": Decimal("15.99"),
    "inventory_quantity": 100
}

listing_schema = MarketplaceListingCreateSchema(**listing_data)
```

## Usage Examples

### 1. Using Pydantic Schemas in Views

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from products.schemas import ProductCreateSchema
from core.pydantic_utils import pydantic_to_django
from products.models import Product

@api_view(['POST'])
def create_product(request):
    try:
        # Validate incoming data
        product_schema = ProductCreateSchema(**request.data)
        
        # Convert to Django model and save
        product = pydantic_to_django(product_schema, Product)
        product.save()
        
        return Response({'message': 'Product created successfully'})
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
```

### 2. Using Custom Serializers

```python
from products.serializers import ProductSerializer
from products.models import Product

# The serializer automatically uses Pydantic validation
serializer = ProductSerializer(data=request.data)
if serializer.is_valid():
    product = serializer.save()
    return Response(serializer.data)
else:
    return Response(serializer.errors, status=400)
```

### 3. Converting Django Models to Pydantic

```python
from core.pydantic_utils import django_to_pydantic
from products.models import Product
from products.schemas import ProductSchema

# Get Django model instance
product = Product.objects.get(id=1)

# Convert to Pydantic schema
product_schema = django_to_pydantic(product, ProductSchema)
product_dict = product_schema.model_dump()
```

### 4. Bulk Operations

```python
from core.pydantic_utils import bulk_django_to_pydantic
from products.models import Product
from products.schemas import ProductSchema

# Get multiple products
products = Product.objects.filter(client_id=1)

# Convert all to Pydantic schemas
product_schemas = bulk_django_to_pydantic(products, ProductSchema)
```

## Error Handling

### Validation Errors

Pydantic validation errors are automatically converted to user-friendly responses:

```python
from pydantic import ValidationError
from core.pydantic_utils import handle_pydantic_validation_error

try:
    schema = ProductCreateSchema(**invalid_data)
except ValidationError as e:
    error_response = handle_pydantic_validation_error(e)
    # Returns: {'error': 'Validation failed', 'details': {...}}
```

### Middleware Error Handling

The `PydanticValidationMiddleware` automatically catches validation errors and returns proper HTTP responses:

```json
{
    "error": "Validation failed",
    "message": "The provided data does not meet the required schema",
    "details": [
        {
            "field": "client_id",
            "message": "value is not a valid integer",
            "type": "type_error.integer"
        }
    ],
    "status_code": 400
}
```

## Configuration

### Pydantic Settings

Configure Pydantic behavior in `core/pydantic_settings.py`:

```python
# Validation settings
STRICT_VALIDATION: bool = True
ALLOW_EXTRA_FIELDS: bool = False

# Serialization settings
SERIALIZE_EXCLUDE_NONE: bool = True
SERIALIZE_EXCLUDE_UNSET: bool = True

# Error handling
SHOW_ERROR_DETAILS: bool = True
LOG_VALIDATION_ERRORS: bool = True
```

### Django Settings

Add middleware to `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware
    'core.pydantic_middleware.PydanticValidationMiddleware',
    'core.pydantic_middleware.PydanticRequestMiddleware',
]
```

## Testing

Run the Pydantic integration tests:

```bash
python test_pydantic_integration.py
```

This will test:
- Schema validation
- Data conversion
- Error handling
- All app-specific schemas

## Benefits

1. **Type Safety**: Catch errors at development time
2. **Data Validation**: Ensure data integrity
3. **Documentation**: Auto-generated API docs
4. **Performance**: Fast validation and serialization
5. **Consistency**: Uniform data handling across the API
6. **Error Messages**: Clear, detailed validation errors

## Migration Guide

### From Django Serializers

1. **Replace ModelSerializer with PydanticModelSerializer**:
   ```python
   # Before
   class ProductSerializer(serializers.ModelSerializer):
       class Meta:
           model = Product
           fields = '__all__'
   
   # After
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
   ```

2. **Add Pydantic schemas** for each model
3. **Update views** to use Pydantic validation
4. **Test thoroughly** to ensure compatibility

## Best Practices

1. **Use specific schemas** for create/update operations
2. **Validate data early** in the request pipeline
3. **Handle errors gracefully** with proper HTTP status codes
4. **Document schemas** with clear field descriptions
5. **Test validation** with edge cases
6. **Use type hints** consistently throughout the codebase

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all schema files are properly imported
2. **Validation Errors**: Check field types and constraints
3. **Serialization Issues**: Verify model relationships are handled correctly
4. **Performance**: Use bulk operations for large datasets

### Debug Mode

Enable debug logging for Pydantic operations:

```python
import logging
logging.getLogger('core.pydantic_utils').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **OpenAPI Integration**: Auto-generate OpenAPI specs from Pydantic schemas
2. **GraphQL Support**: Add GraphQL schema generation
3. **Caching**: Implement schema caching for performance
4. **Async Support**: Add async validation capabilities
5. **Custom Validators**: Add domain-specific validation rules
