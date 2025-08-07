#!/usr/bin/env python3
"""
Test script to demonstrate Pydantic integration in the Coveme API project
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from products.schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema
from orders.schemas import OrderCreateSchema, OrderSchema
from marketplaces.schemas import MarketplaceListingCreateSchema
from core.pydantic_utils import validate_pydantic_data, handle_pydantic_validation_error
from pydantic import ValidationError


def test_product_schemas():
    """Test product Pydantic schemas"""
    print("=== Testing Product Schemas ===")
    
    # Test valid product creation data
    valid_product_data = {
        "client_id": 1,
        "internal_sku": "PROD-001",
        "title": "Test Product",
        "description": "A test product for validation",
        "category": "Electronics",
        "weight": Decimal("1.5"),
        "cost": Decimal("10.99"),
        "is_iva_included": True,
        "is_supermarket": False
    }
    
    try:
        product_schema = ProductCreateSchema(**valid_product_data)
        print(f"✅ Valid product data: {product_schema.model_dump()}")
    except ValidationError as e:
        print(f"❌ Validation error: {handle_pydantic_validation_error(e)}")
    
    # Test invalid product data
    invalid_product_data = {
        "client_id": "not_an_integer",  # Should be int
        "internal_sku": "",  # Should not be empty
        "title": "A" * 600,  # Too long
        "cost": "invalid_decimal"  # Should be Decimal
    }
    
    try:
        product_schema = ProductCreateSchema(**invalid_product_data)
        print(f"✅ Invalid product data (should have failed): {product_schema.model_dump()}")
    except ValidationError as e:
        print(f"✅ Validation error caught: {handle_pydantic_validation_error(e)}")


def test_order_schemas():
    """Test order Pydantic schemas"""
    print("\n=== Testing Order Schemas ===")
    
    # Test valid order creation data
    valid_order_data = {
        "client_id": 1,
        "marketplace_type": "amazon",
        "marketplace_order_id": "AMZ-123456",
        "order_status": "pending",
        "order_total": Decimal("99.99"),
        "currency": "USD",
        "purchase_date": datetime.now(),
        "customer_info": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "shipping_address": {
            "street": "123 Main St",
            "city": "New York",
            "zip": "10001"
        }
    }
    
    try:
        order_schema = OrderCreateSchema(**valid_order_data)
        print(f"✅ Valid order data: {order_schema.model_dump()}")
    except ValidationError as e:
        print(f"❌ Validation error: {handle_pydantic_validation_error(e)}")


def test_marketplace_schemas():
    """Test marketplace Pydantic schemas"""
    print("\n=== Testing Marketplace Schemas ===")
    
    # Test valid marketplace listing data
    valid_listing_data = {
        "client_id": 1,
        "marketplace_type": "mercadolibre",
        "marketplace_id": "ML123456",
        "external_sku": "EXT-SKU-001",
        "title": "Product in Marketplace",
        "price": Decimal("15.99"),
        "currency": "USD",
        "inventory_quantity": 100,
        "status": "active",
        "is_fulfillment": False,
        "metadata": {
            "category": "Electronics",
            "brand": "Test Brand"
        }
    }
    
    try:
        listing_schema = MarketplaceListingCreateSchema(**valid_listing_data)
        print(f"✅ Valid marketplace listing data: {listing_schema.model_dump()}")
    except ValidationError as e:
        print(f"❌ Validation error: {handle_pydantic_validation_error(e)}")


def test_schema_validation():
    """Test schema validation utilities"""
    print("\n=== Testing Schema Validation Utilities ===")
    
    # Test validation function
    test_data = {
        "client_id": 1,
        "internal_sku": "TEST-001",
        "title": "Test Product"
    }
    
    try:
        validated = validate_pydantic_data(test_data, ProductCreateSchema)
        print(f"✅ Data validation successful: {validated.model_dump()}")
    except ValidationError as e:
        print(f"❌ Data validation failed: {handle_pydantic_validation_error(e)}")


def test_error_handling():
    """Test error handling utilities"""
    print("\n=== Testing Error Handling ===")
    
    # Test with invalid data
    invalid_data = {
        "client_id": "invalid",
        "internal_sku": "",
        "title": None
    }
    
    try:
        ProductCreateSchema(**invalid_data)
    except ValidationError as e:
        error_response = handle_pydantic_validation_error(e)
        print(f"✅ Error handling test: {error_response}")


def main():
    """Main test function"""
    print("🚀 Testing Pydantic Integration in Coveme API")
    print("=" * 50)
    
    try:
        test_product_schemas()
        test_order_schemas()
        test_marketplace_schemas()
        test_schema_validation()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ All Pydantic integration tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
