# Listings CRUD API Documentation

## Overview

The Listings API provides comprehensive CRUD operations for managing marketplace listings across different e-commerce platforms including Amazon, Mercado Libre, Shopify, eBay, and Walmart.

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

All listings endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

The JWT token must contain the `client_id` claim for the user's associated client.

## Models & Types

### MarketplaceListing Model

```python
class MarketplaceListing(TimestampedModel):
    """Listado específico en un marketplace"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
    marketplace_type = models.CharField(max_length=50, choices=[
        ('amazon', 'Amazon'),
        ('mercadolibre', 'Mercado Libre'),
        ('shopify', 'Shopify'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
    ])
    marketplace_id = models.CharField(max_length=100)
    external_sku = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    inventory_quantity = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    is_fulfillment = models.BooleanField(default=False)
    listing_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipment_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_type = models.CharField(max_length=50, null=True, blank=True)
    official_store_name = models.CharField(max_length=200, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    permalink = models.URLField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
```

### Pydantic Schemas

#### MarketplaceListingSchema (Read)
```python
class MarketplaceListingSchema(TimestampedSchema):
    id: Optional[int] = None
    client_id: int
    product_id: Optional[int] = None
    marketplace_type: str
    marketplace_id: str
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = Field(default="USD")
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: bool = False
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### MarketplaceListingCreateSchema (Create)
```python
class MarketplaceListingCreateSchema(BaseModel):
    client_id: int
    product_id: Optional[int] = None
    marketplace_type: str
    marketplace_id: str
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = Field(default="USD")
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: bool = False
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### MarketplaceListingUpdateSchema (Update)
```python
class MarketplaceListingUpdateSchema(BaseModel):
    product_id: Optional[int] = None
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: Optional[bool] = None
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

## API Endpoints

### Base Endpoint
```
/marketplace-listings/
```

### Client Context Mixin

The listings endpoint automatically implements client isolation through the `ClientContextMixin`. This means:

- **Automatic Client Filtering**: All listings are automatically filtered by the authenticated user's client
- **JWT Integration**: The client ID is extracted from the JWT token or user profile
- **Permission Validation**: Users can only access listings from their associated client
- **Security**: Prevents cross-client data access

**Implementation Pattern:**
```python
class MarketplaceListingViewSet(ClientContextMixin, viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.all()
    serializer_class = MarketplaceListingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marketplace_type', 'status']  # 'client' removed - auto-filtered
    
    def get_queryset(self):
        """Automatically filter listings by authenticated user's client"""
        client_id = self.get_client_from_request(self.request)
        return MarketplaceListing.objects.filter(client_id=client_id)
```

**Benefits:**
- ✅ **Automatic Security**: No need to manually specify `client_id` in requests
- ✅ **Data Isolation**: Users only see their own client's listings
- ✅ **Simplified API**: Cleaner request/response payloads
- ✅ **JWT Integration**: Seamless authentication and authorization

### CRUD Operations

#### 1. Create Listing
**POST** `/marketplace-listings/`

**Request Body:**
```json
{
    "product_id": 123,
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "external_sku": "AMZ-SKU-001",
    "title": "Wireless Bluetooth Headphones",
    "price": "29.99",
    "currency": "USD",
    "inventory_quantity": 100,
    "status": "active",
    "is_fulfillment": false,
    "listing_fee": "2.99",
    "shipment_fee": "4.99",
    "listing_type": "FBA",
    "official_store_name": "TechStore",
    "thumbnail_url": "https://example.com/image.jpg",
    "permalink": "https://amazon.com/product/B08N5WRWNW",
    "metadata": {
        "category": "Electronics",
        "brand": "TechBrand",
        "features": ["Bluetooth 5.0", "Noise Cancelling"]
    }
}
```

> **Note**: `client_id` is automatically extracted from the authenticated user's JWT token and does not need to be specified in the request body.

**Response (201 Created):**
```json
{
    "id": 1,
    "client_id": 1,
    "product_id": 123,
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "external_sku": "AMZ-SKU-001",
    "title": "Wireless Bluetooth Headphones",
    "price": "29.99",
    "currency": "USD",
    "inventory_quantity": 100,
    "status": "active",
    "is_fulfillment": false,
    "listing_fee": "2.99",
    "shipment_fee": "4.99",
    "listing_type": "FBA",
    "official_store_name": "TechStore",
    "thumbnail_url": "https://example.com/image.jpg",
    "permalink": "https://amazon.com/product/B08N5WRWNW",
    "metadata": {
        "category": "Electronics",
        "brand": "TechBrand",
        "features": ["Bluetooth 5.0", "Noise Cancelling"]
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

> **Note**: `client_id` is automatically populated in responses but should not be sent in requests.

#### 2. Read Listings

##### Get All Listings
**GET** `/marketplace-listings/`

**Query Parameters:**
- `client`: Filter by client ID
- `marketplace_type`: Filter by marketplace type (amazon, mercadolibre, shopify, ebay, walmart)
- `status`: Filter by status

**Example:**
```bash
GET /marketplace-listings/?marketplace_type=amazon&status=active
```

**Response (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "client_id": 1,
            "product_id": 123,
            "marketplace_type": "amazon",
            "marketplace_id": "B08N5WRWNW",
            "title": "Wireless Bluetooth Headphones",
            "price": "29.99",
            "currency": "USD",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "client_id": 1,
            "product_id": 124,
            "marketplace_type": "amazon",
            "marketplace_id": "B08N5WRWNW",
            "title": "USB-C Cable",
            "price": "9.99",
            "currency": "USD",
            "status": "active",
            "created_at": "2024-01-15T11:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z"
        }
    ]
}
```

##### Get Single Listing
**GET** `/marketplace-listings/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "client_id": 1,
    "product_id": 123,
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "external_sku": "AMZ-SKU-001",
    "title": "Wireless Bluetooth Headphones",
    "price": "29.99",
    "currency": "USD",
    "inventory_quantity": 100,
    "status": "active",
    "is_fulfillment": false,
    "listing_fee": "2.99",
    "shipment_fee": "4.99",
    "listing_type": "FBA",
    "official_store_name": "TechStore",
    "thumbnail_url": "https://example.com/image.jpg",
    "permalink": "https://amazon.com/product/B08N5WRWNW",
    "metadata": {
        "category": "Electronics",
        "brand": "TechBrand",
        "features": ["Bluetooth 5.0", "Noise Cancelling"]
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 3. Update Listing
**PUT** `/marketplace-listings/{id}/`

**Request Body:**
```json
{
    "price": "24.99",
    "inventory_quantity": 75,
    "status": "active",
    "metadata": {
        "category": "Electronics",
        "brand": "TechBrand",
        "features": ["Bluetooth 5.0", "Noise Cancelling"],
        "promotion": "20% off"
    }
}
```

> **Note**: Only the fields you want to update need to be included. `client_id` cannot be modified.

**Response (200 OK):**
```json
{
    "id": 1,
    "client_id": 1,
    "product_id": 123,
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "external_sku": "AMZ-SKU-001",
    "title": "Wireless Bluetooth Headphones",
    "price": "24.99",
    "currency": "USD",
    "inventory_quantity": 75,
    "status": "active",
    "is_fulfillment": false,
    "listing_fee": "2.99",
    "shipment_fee": "4.99",
    "listing_type": "FBA",
    "official_store_name": "TechStore",
    "thumbnail_url": "https://example.com/image.jpg",
    "permalink": "https://amazon.com/product/B08N5WRWNW",
    "metadata": {
        "category": "Electronics",
        "brand": "TechBrand",
        "features": ["Bluetooth 5.0", "Noise Cancelling"],
        "promotion": "20% off"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
}
```

**PATCH** `/marketplace-listings/{id}/`

**Request Body:**
```json
{
    "price": "24.99"
}
```

#### 4. Delete Listing
**DELETE** `/marketplace-listings/{id}/`

**Response (204 No Content)**

## Field Types & Validation

### Required Fields
- `marketplace_type`: String - Must be one of: amazon, mercadolibre, shopify, ebay, walmart
- `marketplace_id`: String - Unique identifier in the marketplace (max 100 chars)

### Auto-populated Fields
- `client_id`: Integer - Automatically extracted from authenticated user's JWT token

### Optional Fields
- `product_id`: Integer - References an existing product
- `external_sku`: String - External SKU from marketplace (max 100 chars)
- `title`: String - Product title (max 500 chars)
- `price`: Decimal - Product price (max 10 digits, 2 decimal places)
- `currency`: String - Currency code (default: USD, max 3 chars)
- `inventory_quantity`: Integer - Available inventory
- `status`: String - Listing status (max 50 chars)
- `is_fulfillment`: Boolean - Whether fulfillment is handled by marketplace (default: false)
- `listing_fee`: Decimal - Fee charged by marketplace (max 10 digits, 2 decimal places)
- `shipment_fee`: Decimal - Shipping fee (max 10 digits, 2 decimal places)
- `listing_type`: String - Type of listing (max 50 chars)
- `official_store_name`: String - Official store name (max 200 chars)
- `thumbnail_url`: URL - Product thumbnail image URL (max 500 chars)
- `permalink`: URL - Direct link to product (max 500 chars)
- `metadata`: JSON - Additional data in key-value format

### Validation Rules
- `marketplace_type` must be one of the predefined choices
- `price`, `listing_fee`, `shipment_fee` must be positive decimal numbers
- `inventory_quantity` must be a non-negative integer
- URLs must be valid URL format
- `metadata` must be valid JSON

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation failed",
    "details": {
        "marketplace_type": ["Invalid marketplace type. Must be one of: amazon, mercadolibre, shopify, ebay, walmart"],
        "price": ["Price must be a positive number"]
    }
}
```

### 404 Not Found
```json
{
    "error": "Listing not found",
    "detail": "No marketplace listing found with id 999"
}
```

### 409 Conflict
```json
{
    "error": "Duplicate listing",
    "detail": "A listing with this marketplace_id already exists for this client and marketplace_type"
}
```

## Filtering & Search

### Available Filters
- `client`: Filter by client ID
- `marketplace_type`: Filter by marketplace type
- `status`: Filter by listing status
- `is_fulfillment`: Filter by fulfillment type
- `price_min`: Filter by minimum price
- `price_max`: Filter by maximum price

### Example Queries
```bash
# Get all Amazon listings for a specific client
GET /marketplace-listings/?client=1&marketplace_type=amazon

# Get all active listings with price range
GET /marketplace-listings/?status=active&price_min=10&price_max=100

# Get all fulfillment listings
GET /marketplace-listings/?is_fulfillment=true
```

## Bulk Operations

### Bulk Create
**POST** `/marketplace-listings/bulk_create/`

**Request Body:**
```json
{
    "listings": [
        {
            "marketplace_type": "amazon",
            "marketplace_id": "B08N5WRWNW",
            "title": "Product 1",
            "price": "29.99"
        },
        {
            "marketplace_type": "amazon",
            "marketplace_id": "B08N5WRWNW",
            "title": "Product 2",
            "price": "19.99"
        }
    ]
}
```

> **Note**: `client_id` is automatically applied to all listings in bulk operations.

### Bulk Update
**PUT** `/marketplace-listings/bulk_update/`

**Request Body:**
```json
{
    "ids": [1, 2, 3],
    "updates": {
        "status": "inactive",
        "metadata": {"bulk_updated": true}
    }
}
```

## Related Models

### ProductMatch
Links products to marketplace listings with confidence scores and match criteria.

### ProductPriceHistory
Tracks price changes over time for analysis and reporting.

### ProductTracing
Monitors competitor products and pricing across marketplaces.

## Usage Examples

### Python Requests
```python
import requests

# Create a new listing
url = "http://localhost:8000/api/v1/marketplace-listings/"
data = {
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "title": "Wireless Headphones",
    "price": "29.99"
}

response = requests.post(url, json=data)
listing = response.json()

# Update listing price
update_url = f"http://localhost:8000/api/v1/marketplace-listings/{listing['id']}/"
update_data = {"price": "24.99"}
response = requests.patch(update_url, json=update_data)

# Get all Amazon listings
listings_url = "http://localhost:8000/api/v1/marketplace-listings/?marketplace_type=amazon"
response = requests.get(listings_url)
listings = response.json()
```

### cURL Examples
```bash
# Create listing
curl -X POST "http://localhost:8000/api/v1/marketplace-listings/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "marketplace_type": "amazon",
    "marketplace_id": "B08N5WRWNW",
    "title": "Wireless Headphones",
    "price": "29.99"
  }'

# Get listings
curl -X GET "http://localhost:8000/api/v1/marketplace-listings/?marketplace_type=amazon"

# Update listing
curl -X PATCH "http://localhost:8000/api/v1/marketplace-listings/1/" \
  -H "Content-Type: application/json" \
  -d '{"price": "24.99"}'

# Delete listing
curl -X DELETE "http://localhost:8000/api/v1/marketplace-listings/1/"
```

## Best Practices

1. **Validation**: Always validate data before sending to the API
2. **Error Handling**: Implement proper error handling for API responses
3. **Rate Limiting**: Respect API rate limits and implement retry logic
4. **Data Consistency**: Ensure data consistency across related models
5. **Monitoring**: Monitor API usage and performance metrics
6. **Security**: Use proper authentication and authorization
7. **Documentation**: Keep API documentation updated with any changes

## Support

For technical support or questions about the Listings API, please contact the development team or refer to the main API documentation.
