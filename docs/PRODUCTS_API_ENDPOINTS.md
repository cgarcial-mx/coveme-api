# API de Productos - Endpoints y Tipos

## Base URL
```
https://api.coveme.com/api/v1/
```

## 🔐 Autenticación
Todos los endpoints requieren autenticación JWT:
```
Authorization: Bearer <access_token>
```

---

## 📦 Endpoints de Productos

### 1. Productos Maestros

#### `GET /products/`
**Descripción:** Listar todos los productos del cliente autenticado
**Filtros disponibles:**
- `brand` - ID de la marca
- `provider` - ID del proveedor  
- `category` - Categoría del producto

**Respuesta:**
```json
{
  "count": 150,
  "next": "https://api.coveme.com/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "internal_sku": "PROD-001",
      "title": "Laptop Gaming Pro",
      "description": "Laptop de alto rendimiento para gaming",
      "brand_id": 5,
      "brand_name": "TechCorp",
      "subbrand_id": 12,
      "subbrand_name": "Gaming Series",
      "provider_id": 3,
      "provider_name": "TechSupplier",
      "category": "Electronics",
      "weight": "2.5",
      "dimensions": {"length": "35", "width": "25", "height": "2"},
      "barcode": "1234567890123",
      "cost": "1200.00",
      "cost_with_discount": "1100.00",
      "is_iva_included": false,
      "is_supermarket": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `POST /products/`
**Descripción:** Crear un nuevo producto
**Body:**
```json
{
  "internal_sku": "PROD-002",
  "title": "Mouse Gaming RGB",
  "description": "Mouse gaming con iluminación RGB",
  "brand_id": 5,
  "subbrand_id": 12,
  "provider_id": 3,
  "category": "Accessories",
  "weight": "0.150",
  "dimensions": {"length": "12", "width": "6", "height": "4"},
  "barcode": "9876543210987",
  "cost": "45.00",
  "cost_with_discount": "40.00",
  "is_iva_included": false,
  "is_supermarket": false
}
```

#### `GET /products/{id}/`
**Descripción:** Obtener detalles de un producto específico

#### `PUT /products/{id}/`
**Descripción:** Actualizar completamente un producto

#### `PATCH /products/{id}/`
**Descripción:** Actualizar parcialmente un producto

#### `DELETE /products/{id}/`
**Descripción:** Eliminar un producto

---

### 2. Marcas (Brands)

#### `GET /brands/`
**Descripción:** Listar todas las marcas del cliente
**Filtros:** Ninguno (se filtra automáticamente por cliente)

#### `POST /brands/`
**Descripción:** Crear una nueva marca
**Body:**
```json
{
  "name": "TechCorp"
}
```

---

### 3. Sub-marcas (SubBrands)

#### `GET /subbrands/`
**Descripción:** Listar todas las sub-marcas del cliente
**Filtros:**
- `brand` - ID de la marca padre

#### `POST /subbrands/`
**Descripción:** Crear una nueva sub-marca
**Body:**
```json
{
  "brand_id": 5,
  "name": "Gaming Series"
}
```

---

### 4. Proveedores (Providers)

#### `GET /providers/`
**Descripción:** Listar todos los proveedores del cliente
**Filtros:** Ninguno (se filtra automáticamente por cliente)

#### `POST /providers/`
**Descripción:** Crear un nuevo proveedor
**Body:**
```json
{
  "name": "TechSupplier",
  "email": "contact@techsupplier.com",
  "contact_info": {
    "phone": "+1-555-0123",
    "address": "123 Tech Street"
  }
}
```

---

## 🏪 Endpoints de Marketplace

### 5. Listados de Marketplace

#### `GET /marketplace-listings/`
**Descripción:** Listar todos los listados del cliente en marketplaces
**Filtros disponibles:**
- `marketplace_type` - Tipo de marketplace (amazon, mercadolibre, shopify, ebay, walmart)
- `product` - ID del producto maestro
- `status` - Estado del listado

**Respuesta:**
```json
{
  "id": 1,
  "marketplace_type": "amazon",
  "marketplace_id": "B08N5WRWNW",
  "external_sku": "AMZ-001",
  "title": "Laptop Gaming Pro - TechCorp",
  "price": "1499.99",
  "currency": "USD",
  "inventory_quantity": 25,
  "status": "active",
  "is_fulfillment": true,
  "listing_fee": "39.99",
  "shipment_fee": "15.00",
  "listing_type": "FBA",
  "official_store_name": "TechCorp Store",
  "thumbnail_url": "https://example.com/image.jpg",
  "permalink": "https://amazon.com/dp/B08N5WRWNW"
}
```

---

### 6. Coincidencias de Productos

#### `GET /product-matches/`
**Descripción:** Listar coincidencias entre productos y listados
**Filtros:**
- `product` - ID del producto
- `marketplace_listing` - ID del listado
- `match_type` - Tipo de coincidencia (auto, manual, rejected)
- `status` - Estado de la coincidencia

---

### 7. Historial de Precios

#### `GET /price-history/`
**Descripción:** Historial de cambios de precios
**Filtros:**
- `product` - ID del producto
- `marketplace_listing` - ID del listado

---

### 8. Trazabilidad de Competidores

#### `GET /product-tracing/`
**Descripción:** Seguimiento de productos competidores
**Filtros:**
- `product` - ID del producto
- `marketplace_type` - Tipo de marketplace

---

## 📊 Tipos de Datos

### Producto (Product)
```typescript
interface Product {
  id: number;
  internal_sku: string;           // SKU interno único
  title: string;                  // Título del producto
  description?: string;           // Descripción opcional
  brand_id?: number;              // ID de la marca
  subbrand_id?: number;           // ID de la sub-marca
  provider_id?: number;           // ID del proveedor
  category?: string;              // Categoría del producto
  weight?: Decimal;               // Peso en kg
  dimensions: {                   // Dimensiones (LxWxH)
    length: string;
    width: string;
    height: string;
  };
  barcode?: string;               // Código de barras
  cost?: Decimal;                 // Costo base
  cost_with_discount?: Decimal;   // Costo con descuento
  is_iva_included: boolean;       // IVA incluido
  is_supermarket: boolean;        // Es producto de supermercado
  created_by_id?: number;         // Usuario que lo creó
  created_at: string;             // Fecha de creación ISO
  updated_at: string;             // Fecha de última actualización ISO
}
```

### Listado de Marketplace (MarketplaceListing)
```typescript
interface MarketplaceListing {
  id: number;
  marketplace_type: 'amazon' | 'mercadolibre' | 'shopify' | 'ebay' | 'walmart';
  marketplace_id: string;         // ID único en el marketplace
  external_sku?: string;          // SKU externo
  title?: string;                 // Título en el marketplace
  price?: Decimal;                // Precio de venta
  currency: string;               // Moneda (USD, EUR, ARS, etc.)
  inventory_quantity?: number;    // Cantidad en inventario
  status?: string;                // Estado del listado
  is_fulfillment: boolean;        // Es fulfillment
  listing_fee?: Decimal;          // Comisión del marketplace
  shipment_fee?: Decimal;         // Costo de envío
  listing_type?: string;          // Tipo de listado
  official_store_name?: string;   // Nombre de la tienda oficial
  thumbnail_url?: string;         // URL de la imagen
  permalink?: string;             // URL del producto
  metadata: object;               // Metadatos adicionales
}
```

### Coincidencia de Producto (ProductMatch)
```typescript
interface ProductMatch {
  id: number;
  product_id: number;             // ID del producto maestro
  marketplace_listing_id: number; // ID del listado
  confidence_score: Decimal;      // Puntuación de confianza (0-1)
  match_type: 'auto' | 'manual' | 'rejected';
  match_criteria: object;         // Criterios de coincidencia
  reviewed_by_id?: number;        // Usuario que revisó
  reviewed_at?: string;           // Fecha de revisión
  status: 'active' | 'inactive' | 'rejected';
}
```

---

## 🔍 Filtros y Búsqueda

### Filtros por Defecto
- **Cliente:** Automático basado en JWT (no configurable)
- **Paginación:** 20 resultados por página
- **Ordenamiento:** Por fecha de creación (más reciente primero)

### Filtros Personalizables
```bash
# Filtros de productos
GET /products/?brand=5&category=Electronics&provider=3

# Filtros de marketplace
GET /marketplace-listings/?marketplace_type=amazon&status=active

# Filtros de coincidencias
GET /product-matches/?match_type=auto&status=active
```

---

## 📝 Notas Importantes

1. **Multi-tenancy:** Todos los endpoints filtran automáticamente por el cliente del usuario autenticado
2. **Validación:** Los datos se validan usando esquemas Pydantic
3. **Auditoría:** Todos los modelos incluyen timestamps de creación y actualización
4. **Relaciones:** Los productos pueden estar asociados a marcas, sub-marcas y proveedores
5. **Marketplaces:** Soporte para Amazon, Mercado Libre, Shopify, eBay y Walmart
6. **Trazabilidad:** Sistema completo de seguimiento de precios y competencia

---

## 🚀 Ejemplos de Uso

### Crear un Producto Completo
```bash
curl -X POST https://api.coveme.com/api/v1/products/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "internal_sku": "LAPTOP-001",
    "title": "Laptop Gaming Pro Max",
    "description": "Laptop gaming de última generación",
    "brand_id": 1,
    "category": "Electronics",
    "weight": "2.8",
    "dimensions": {"length": "36", "width": "26", "height": "2.5"},
    "cost": "1500.00",
    "is_iva_included": false
  }'
```

### Listar Productos con Filtros
```bash
curl -X GET "https://api.coveme.com/api/v1/products/?category=Electronics&brand=1" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Obtener Historial de Precios
```bash
curl -X GET "https://api.coveme.com/api/v1/price-history/?product=1" \
  -H "Authorization: Bearer <your_jwt_token>"
```

---

## 📚 Referencias Adicionales

- [Documentación de Autenticación JWT](./AUTHENTICATION.md)
- [Configuración de Marketplaces](./MARKETPLACE_SETUP.md)
- [Sistema de Sincronización](./SYNC_SYSTEM.md)
- [Guía de Permisos](./PERMISSIONS.md)
