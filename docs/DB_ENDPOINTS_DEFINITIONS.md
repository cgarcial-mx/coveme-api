# Database and API Endpoints Definitions

## 📋 Overview

This document defines the complete database schema, API endpoints, and system architecture for the Coveme multi-marketplace product management platform. The system allows clients to manage products across Amazon, Mercado Libre, and Shopify marketplaces with intelligent product matching and customer feedback management.

## 🏗️ System Architecture

### Core Components
- **Clients**: Companies using the platform
- **Users**: Employees of clients with different permission levels
- **Marketplaces**: Amazon SP-API, Mercado Libre, Shopify
- **Products**: Central product catalog with marketplace listings
- **Orders**: Order management across all marketplaces
- **Customer Feedback**: Reviews, questions, and comments

## 🗄️ Database Schema

### 1. Core Tables

#### Clients Table
```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    tax_id VARCHAR(50) UNIQUE,
    subscription_plan VARCHAR(50) NOT NULL, -- 'basic', 'premium', 'enterprise'
    api_quota INTEGER NOT NULL, -- Límite de llamadas por mes
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'admin', 'manager', 'operator', 'viewer'
    permissions JSONB, -- Permisos específicos
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Client Marketplace Credentials Table
```sql
CREATE TABLE client_marketplace_credentials (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    marketplace_type VARCHAR(50) NOT NULL, -- 'amazon', 'mercadolibre', 'shopify'
    marketplace_name VARCHAR(100),
    
    -- Credenciales específicas por marketplace
    credentials JSONB NOT NULL, -- Credenciales encriptadas
    settings JSONB, -- Configuraciones específicas
    webhook_url VARCHAR(500), -- URL para webhooks si aplica
    
    -- Estado de conexión
    connection_status VARCHAR(50) DEFAULT 'disconnected', -- 'connected', 'disconnected', 'error'
    last_sync_at TIMESTAMP,
    last_error TEXT,
    
    -- Metadatos
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, marketplace_type)
);
```

### 2. Product Management Tables

#### Products Table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    internal_sku VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    model VARCHAR(100),
    category VARCHAR(100),
    weight DECIMAL(10,3),
    dimensions JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, internal_sku)
);
```

#### Marketplace Listings Table
```sql
CREATE TABLE marketplace_listings (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    product_id INTEGER REFERENCES products(id),
    marketplace_type VARCHAR(50) NOT NULL,
    marketplace_id VARCHAR(100) NOT NULL,
    external_sku VARCHAR(100),
    title VARCHAR(500),
    price DECIMAL(10,2),
    currency VARCHAR(3),
    inventory_quantity INTEGER,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, marketplace_type, marketplace_id)
);
```

#### Product Matches Table
```sql
CREATE TABLE product_matches (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    product_id INTEGER REFERENCES products(id),
    matched_marketplace_type VARCHAR(50),
    matched_marketplace_id VARCHAR(100),
    confidence_score DECIMAL(3,2),
    match_type VARCHAR(50), -- 'auto', 'manual', 'rejected'
    match_criteria JSONB,
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Order Management Tables

#### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    marketplace_type VARCHAR(50) NOT NULL,
    marketplace_order_id VARCHAR(100) NOT NULL,
    order_status VARCHAR(50),
    order_total DECIMAL(10,2),
    currency VARCHAR(3),
    purchase_date TIMESTAMP,
    last_update_date TIMESTAMP,
    customer_info JSONB,
    shipping_address JSONB,
    billing_address JSONB,
    payment_info JSONB,
    fulfillment_status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, marketplace_type, marketplace_order_id)
);
```

#### Order Items Table
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    marketplace_item_id VARCHAR(100),
    product_id INTEGER REFERENCES products(id),
    title VARCHAR(500),
    sku VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Customer Feedback Tables

#### Customer Feedback Table
```sql
CREATE TABLE customer_feedback (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    marketplace_type VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL, -- 'review', 'question', 'comment'
    marketplace_feedback_id VARCHAR(100),
    product_id INTEGER REFERENCES products(id),
    marketplace_product_id VARCHAR(100),
    customer_name VARCHAR(200),
    customer_email VARCHAR(255),
    rating INTEGER,
    title VARCHAR(500),
    content TEXT,
    feedback_date TIMESTAMP,
    status VARCHAR(50), -- 'pending', 'approved', 'rejected', 'answered'
    answer_text TEXT,
    answer_date TIMESTAMP,
    verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. System Tables

#### API Logs Table
```sql
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    user_id INTEGER REFERENCES users(id),
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    response_time INTEGER, -- en milisegundos
    quota_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔐 Authentication & Authorization

### Permission System
```python
PERMISSIONS_BY_ROLE = {
    'admin': {
        'products': ['create', 'read', 'update', 'delete'],
        'marketplaces': ['create', 'read', 'update', 'delete'],
        'users': ['create', 'read', 'update', 'delete'],
        'sync': ['start', 'review', 'confirm'],
        'orders': ['read', 'sync'],
        'feedback': ['read', 'sync', 'respond'],
        'reports': ['view', 'export'],
        'settings': ['read', 'update']
    },
    'manager': {
        'products': ['create', 'read', 'update'],
        'marketplaces': ['read', 'update'],
        'users': ['read'],
        'sync': ['start', 'review', 'confirm'],
        'orders': ['read', 'sync'],
        'feedback': ['read', 'sync', 'respond'],
        'reports': ['view'],
        'settings': ['read']
    },
    'operator': {
        'products': ['read', 'update'],
        'marketplaces': ['read'],
        'users': ['read'],
        'sync': ['review', 'confirm'],
        'orders': ['read'],
        'feedback': ['read', 'respond'],
        'reports': ['view'],
        'settings': ['read']
    },
    'viewer': {
        'products': ['read'],
        'marketplaces': ['read'],
        'users': ['read'],
        'sync': ['read'],
        'orders': ['read'],
        'feedback': ['read'],
        'reports': ['view'],
        'settings': ['read']
    }
}
```

### Subscription Plans
```python
SUBSCRIPTION_PLANS = {
    'basic': {
        'monthly_quota': 10000,
        'concurrent_requests': 10,
        'features': ['products', 'marketplaces', 'basic_sync'],
        'price': 99.00
    },
    'premium': {
        'monthly_quota': 50000,
        'concurrent_requests': 25,
        'features': ['products', 'marketplaces', 'advanced_sync', 'orders', 'feedback', 'reports'],
        'price': 299.00
    },
    'enterprise': {
        'monthly_quota': 200000,
        'concurrent_requests': 100,
        'features': ['products', 'marketplaces', 'advanced_sync', 'orders', 'feedback', 'reports', 'custom_integrations'],
        'price': 999.00
    }
}
```

## 🌐 API Endpoints

### Base URL
```
https://api.coveme.com/v1
```

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@company.com",
    "password": "password123"
}

Response:
{
    "access_token": "jwt_token_here",
    "user": {
        "id": 123,
        "email": "user@company.com",
        "role": "manager",
        "client_id": 456
    }
}
```

### Client Management Endpoints

#### Get Client Users
```http
GET /clients/{client_id}/users
Authorization: Bearer <token>

Response:
{
    "users": [
        {
            "id": 123,
            "email": "user@company.com",
            "username": "user123",
            "role": "manager",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### Create Client User
```http
POST /clients/{client_id}/users
Authorization: Bearer <token>
Content-Type: application/json

{
    "email": "newuser@company.com",
    "username": "newuser",
    "password": "password123",
    "role": "operator"
}

Response:
{
    "user": {
        "id": 124,
        "email": "newuser@company.com",
        "username": "newuser",
        "role": "operator",
        "status": "active"
    }
}
```

### Marketplace Credentials Endpoints

#### Get Marketplace Credentials
```http
GET /clients/{client_id}/marketplace-credentials
Authorization: Bearer <token>

Response:
{
    "credentials": [
        {
            "id": 456,
            "marketplace_type": "amazon",
            "marketplace_name": "Amazon US",
            "connection_status": "connected",
            "last_sync_at": "2024-01-20T14:45:00Z",
            "last_error": null,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T14:45:00Z"
        }
    ]
}
```

#### Add Marketplace Credentials
```http
POST /clients/{client_id}/marketplace-credentials
Authorization: Bearer <token>
Content-Type: application/json

{
    "marketplace_type": "amazon",
    "marketplace_name": "Amazon US",
    "credentials": {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "marketplace_id": "ATVPDKIKX0DER",
        "seller_id": "A1AM78C64UM0Y8"
    },
    "settings": {
        "auto_refresh": true
    }
}

Response:
{
    "credential_id": 456,
    "status": "created",
    "connection_test": {
        "status": "success",
        "message": "Conexión exitosa con Amazon SP-API"
    }
}
```

#### Test Marketplace Connection
```http
POST /clients/{client_id}/marketplace-credentials/{credential_id}/test
Authorization: Bearer <token>

Response:
{
    "credential_id": 456,
    "connection_test": {
        "status": "success",
        "message": "Conexión exitosa con Amazon SP-API"
    }
}
```

### Product Management Endpoints

#### Get Products
```http
GET /clients/{client_id}/products?marketplace_type=amazon&limit=20
Authorization: Bearer <token>

Response:
{
    "products": [
        {
            "id": 789,
            "internal_sku": "PROD-001",
            "title": "iPhone 13 Pro Max 256GB Sierra Blue",
            "brand": "Apple",
            "model": "iPhone 13 Pro Max",
            "category": "Electronics",
            "marketplace_listings": [
                {
                    "marketplace_type": "amazon",
                    "marketplace_id": "B08N5WRWNW",
                    "price": 1299.00,
                    "currency": "USD",
                    "status": "active"
                }
            ]
        }
    ]
}
```

#### Create Product
```http
POST /clients/{client_id}/products
Authorization: Bearer <token>
Content-Type: application/json

{
    "internal_sku": "PROD-002",
    "title": "Samsung Galaxy S21",
    "description": "Latest Samsung smartphone",
    "brand": "Samsung",
    "model": "Galaxy S21",
    "category": "Electronics",
    "weight": 0.5,
    "dimensions": {
        "length": 15.0,
        "width": 7.0,
        "height": 0.8
    }
}

Response:
{
    "product": {
        "id": 790,
        "internal_sku": "PROD-002",
        "title": "Samsung Galaxy S21",
        "brand": "Samsung",
        "created_at": "2024-01-20T15:30:00Z"
    }
}
```

### Product Synchronization Endpoints

#### Start Product Sync
```http
POST /clients/{client_id}/sync/start
Authorization: Bearer <token>
Content-Type: application/json

{
    "marketplace_types": ["amazon", "mercadolibre", "shopify"]
}

Response:
{
    "sync_id": "sync_123456",
    "status": "started",
    "marketplaces": ["amazon", "mercadolibre", "shopify"],
    "estimated_duration": "5 minutes"
}
```

#### Get Sync Status
```http
GET /clients/{client_id}/sync/{sync_id}/status
Authorization: Bearer <token>

Response:
{
    "sync_id": "sync_123456",
    "status": "completed",
    "progress": {
        "total_products": 150,
        "processed_products": 150,
        "matches_found": 120,
        "manual_reviews": 20,
        "new_products": 10
    },
    "duration": "4 minutes 30 seconds"
}
```

#### Get Manual Reviews
```http
GET /clients/{client_id}/sync/manual-reviews
Authorization: Bearer <token>

Response:
{
    "reviews": [
        {
            "id": 1,
            "listing": {
                "marketplace_type": "amazon",
                "marketplace_id": "B08N5WRWNW",
                "title": "Echo Dot (4th Gen)",
                "brand": "Amazon"
            },
            "suggested_matches": [
                {
                    "product_id": 789,
                    "title": "Echo Dot (4th Gen)",
                    "confidence": 0.85,
                    "match_criteria": {
                        "title_similarity": 0.9,
                        "brand_match": true
                    }
                }
            ],
            "marketplace": "amazon"
        }
    ]
}
```

#### Confirm Match
```http
POST /clients/{client_id}/sync/confirm-match
Authorization: Bearer <token>
Content-Type: application/json

{
    "match_id": 1,
    "product_id": 789
}

Response:
{
    "status": "confirmed",
    "match_id": 1
}
```

#### Create New Product from Review
```http
POST /clients/{client_id}/sync/create-new
Authorization: Bearer <token>
Content-Type: application/json

{
    "listing_data": {
        "marketplace_type": "amazon",
        "marketplace_id": "B08N5WRWNW",
        "title": "Echo Dot (4th Gen)",
        "brand": "Amazon"
    },
    "marketplace_type": "amazon"
}

Response:
{
    "product": {
        "id": 791,
        "internal_sku": "PROD-003",
        "title": "Echo Dot (4th Gen)",
        "brand": "Amazon"
    }
}
```

### Order Management Endpoints

#### Get Orders
```http
GET /clients/{client_id}/orders?marketplace_type=amazon&status=pending&limit=20
Authorization: Bearer <token>

Response:
{
    "orders": [
        {
            "id": 123,
            "marketplace_type": "amazon",
            "marketplace_order_id": "114-1234567-1234567",
            "order_status": "pending",
            "order_total": {
                "amount": 1299.00,
                "currency": "USD"
            },
            "purchase_date": "2024-01-20T10:30:00Z",
            "customer_info": {
                "customer_name": "John Doe",
                "customer_email": "john@example.com"
            },
            "shipping_address": {
                "city": "New York",
                "state": "NY",
                "country": "US"
            }
        }
    ]
}
```

#### Sync Orders
```http
POST /clients/{client_id}/orders/sync
Authorization: Bearer <token>
Content-Type: application/json

{
    "marketplace_types": ["amazon", "mercadolibre", "shopify"],
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z"
}

Response:
{
    "sync_id": "order_sync_123456",
    "orders_synced": 45,
    "marketplaces": ["amazon", "mercadolibre", "shopify"]
}
```

### Customer Feedback Endpoints

#### Get Customer Feedback
```http
GET /clients/{client_id}/feedback?feedback_type=review&marketplace_type=amazon&status=pending
Authorization: Bearer <token>

Response:
{
    "feedback": [
        {
            "id": 456,
            "marketplace_type": "amazon",
            "feedback_type": "review",
            "marketplace_feedback_id": "review_123",
            "product_id": 789,
            "customer_name": "Jane Smith",
            "rating": 5,
            "title": "Great product!",
            "content": "Excellent quality and fast delivery",
            "feedback_date": "2024-01-20T12:00:00Z",
            "status": "pending",
            "verified_purchase": true
        }
    ]
}
```

#### Sync Customer Feedback
```http
POST /clients/{client_id}/feedback/sync
Authorization: Bearer <token>
Content-Type: application/json

{
    "marketplace_types": ["amazon", "mercadolibre"],
    "feedback_types": ["review", "question"]
}

Response:
{
    "sync_id": "feedback_sync_123456",
    "feedback_synced": 23,
    "marketplaces": ["amazon", "mercadolibre"]
}
```

#### Respond to Feedback
```http
POST /clients/{client_id}/feedback/{feedback_id}/respond
Authorization: Bearer <token>
Content-Type: application/json

{
    "response_text": "Gracias por tu comentario. Estamos trabajando para mejorar nuestro servicio."
}

Response:
{
    "feedback_id": 456,
    "status": "responded",
    "response": {
        "status": "success",
        "message": "Respuesta enviada correctamente"
    }
}
```

### Reports Endpoints

#### Get Sync Summary Report
```http
GET /clients/{client_id}/reports/sync-summary
Authorization: Bearer <token>

Response:
{
    "summary": {
        "total_products": 150,
        "total_orders": 45,
        "total_feedback": 23,
        "last_sync": "2024-01-20T14:45:00Z",
        "marketplace_stats": {
            "amazon": {
                "products": 50,
                "orders": 15,
                "reviews": 8
            },
            "mercadolibre": {
                "products": 60,
                "orders": 20,
                "questions": 10
            },
            "shopify": {
                "products": 40,
                "orders": 10,
                "comments": 5
            }
        }
    }
}
```

#### Get Product Matches Report
```http
GET /clients/{client_id}/reports/product-matches
Authorization: Bearer <token>

Response:
{
    "matches": [
        {
            "product_id": 789,
            "marketplace_type": "amazon",
            "confidence_score": 0.95,
            "match_type": "auto",
            "match_criteria": {
                "title_similarity": 0.98,
                "brand_match": true,
                "sku_match": true
            }
        }
    ]
}
```

## 🔧 Marketplace Credentials Schema

### Amazon SP-API Credentials
```json
{
    "required_fields": [
        "access_key_id",
        "secret_access_key",
        "region",
        "marketplace_id",
        "seller_id"
    ],
    "optional_fields": [
        "role_arn",
        "refresh_token"
    ]
}
```

### Mercado Libre Credentials
```json
{
    "required_fields": [
        "access_token",
        "refresh_token",
        "client_id",
        "client_secret"
    ],
    "optional_fields": [
        "site_id"
    ]
}
```

### Shopify Credentials
```json
{
    "required_fields": [
        "shop_url",
        "access_token",
        "api_version"
    ],
    "optional_fields": [
        "webhook_secret",
        "private_app_password"
    ]
}
```

## 📊 Data Normalization

### Product Matching Algorithm
```python
class ProductMatcher:
    def __init__(self):
        self.confidence_thresholds = {
            'exact': 0.95,
            'high': 0.85,
            'medium': 0.70,
            'low': 0.50
        }
    
    def calculate_match_score(self, listing, product):
        score = 0.0
        weights = {
            'sku_match': 0.4,
            'title_similarity': 0.25,
            'brand_match': 0.15,
            'model_match': 0.1,
            'dimension_match': 0.05,
            'category_match': 0.05
        }
        
        # SKU/Barcode matching (más confiable)
        if self.match_sku(listing, product):
            score += weights['sku_match']
        
        # Title similarity
        title_sim = self.calculate_title_similarity(listing.title, product.title)
        score += title_sim * weights['title_similarity']
        
        # Brand matching
        if self.match_brand(listing.brand, product.brand):
            score += weights['brand_match']
        
        # Model matching
        if self.match_model(listing.model, product.model):
            score += weights['model_match']
        
        # Dimension matching
        if self.match_dimensions(listing.dimensions, product.dimensions):
            score += weights['dimension_match']
        
        # Category matching
        if self.match_category(listing.category, product.category):
            score += weights['category_match']
        
        return min(score, 1.0)
```

## 🔄 Sync Process Flow

### 1. Determine Base Marketplace
- Analyze all configured marketplaces
- Select marketplace with most products as base
- Create products from base marketplace

### 2. Process Other Marketplaces
- For each marketplace listing:
  - Find matches with base products
  - Auto-match if confidence ≥ 0.85
  - Manual review if 0.60 ≤ confidence < 0.85
  - Create new product if confidence < 0.60

### 3. Manual Review Process
- Present suggested matches to user
- Allow user to confirm match or create new product
- Track all decisions for audit trail

## 📈 Monitoring and Analytics

### API Usage Tracking
- Track all API calls by client
- Monitor quota usage
- Alert when approaching limits

### Sync Performance Metrics
- Sync duration
- Success/failure rates
- Match accuracy rates
- Manual review rates

### Business Intelligence
- Products per marketplace
- Order volume trends
- Customer feedback sentiment
- Revenue by marketplace

## 🔒 Security Considerations

### Data Encryption
- Encrypt sensitive credentials
- Use environment variables for secrets
- Implement proper key rotation

### Access Control
- JWT-based authentication
- Role-based permissions
- API key management
- Rate limiting per client

### Audit Trail
- Log all API calls
- Track user actions
- Monitor for suspicious activity
- Maintain compliance logs

## 🚀 Deployment Considerations

### Azure API Management
- Configure API gateway
- Set up rate limiting
- Implement monitoring
- Configure developer portal

### Database Optimization
- Index frequently queried fields
- Partition large tables
- Implement caching strategy
- Regular maintenance schedules

### Scalability
- Horizontal scaling for API servers
- Database read replicas
- CDN for static content
- Load balancing across regions

## 📝 API Documentation

### OpenAPI/Swagger Specification
- Complete endpoint documentation
- Request/response examples
- Error code definitions
- Authentication flows

### SDK Libraries
- Python SDK
- JavaScript/Node.js SDK
- PHP SDK
- .NET SDK

### Integration Guides
- Step-by-step setup instructions
- Best practices
- Troubleshooting guides
- Code examples

This comprehensive system provides a complete solution for multi-marketplace product management with intelligent matching, order synchronization, and customer feedback management across Amazon, Mercado Libre, and Shopify platforms. 

