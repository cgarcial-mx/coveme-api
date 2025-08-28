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

**Optimizaciones implementadas:**
- **Select Related:** Los productos se obtienen con `select_related('brand', 'subbrand', 'provider')` para optimizar las consultas de base de datos
- **Propiedades del modelo:** Los campos `brand_name`, `subbrand_name` y `provider_name` se calculan automáticamente usando propiedades del modelo
- **Serialización Pydantic:** Conversión optimizada de Django a Pydantic con manejo robusto de campos relacionados

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

## 🔧 Mejoras Técnicas Implementadas

### Resolución del Issue: brand_name null en GET /products/

**Problema identificado:**
- Los campos `brand_name`, `subbrand_name` y `provider_name` retornaban `null` en las respuestas de la API
- Las consultas de base de datos no optimizaban las relaciones con marcas, sub-marcas y proveedores

**Soluciones implementadas:**

#### 1. Optimización de Consultas (ProductViewSet)
```python
def get_queryset(self):
    """Filtrar productos por el cliente del usuario autenticado"""
    client_id = self.get_client_from_request(self.request)
    return Product.objects.filter(client_id=client_id).select_related(
        'brand', 'subbrand', 'provider'
    )
```

#### 2. Propiedades del Modelo Product
```python
@property
def brand_name(self):
    """Get brand name or None"""
    return self.brand.name if self.brand else None

@property
def subbrand_name(self):
    """Get subbrand name or None"""
    return self.subbrand.name if self.subbrand else None

@property
def provider_name(self):
    """Get provider name or None"""
    return self.provider.name if self.provider else None
```

#### 3. Mejora en la Conversión Django a Pydantic
```python
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
```

**Beneficios de las mejoras:**
- ✅ **Rendimiento:** Reducción de consultas N+1 mediante `select_related`
- ✅ **Confiabilidad:** Los campos `*_name` siempre están disponibles cuando existe la relación
- ✅ **Mantenibilidad:** Propiedades del modelo centralizan la lógica de nombres relacionados
- ✅ **Robustez:** Manejo de errores mejorado en la conversión Pydantic

**Después de la corrección:**
```json
{
  "id": 1,
  "title": "Laptop Gaming Pro",
  "brand_id": 5,
  "brand_name": "TechCorp",  // ✅ Nombre de marca correcto
  "subbrand_id": 12,
  "subbrand_name": "Gaming Series",  // ✅ Nombre de sub-marca correcto
  "provider_id": 3,
  "provider_name": "TechSupplier"  // ✅ Nombre de proveedor correcto
}
```

**Comandos para verificar:**
```bash
# Verificar que los campos *_name no sean null
curl -X GET "https://api.coveme.com/api/v1/products/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  | jq '.results[] | select(.brand_name != null) | {id, title, brand_name}'

# Verificar optimización de consultas (en logs de Django)
# Debería mostrar consultas con JOIN en lugar de consultas separadas
```

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

## 💡 Mejores Prácticas y Recomendaciones

### Para el Uso de la API

1. **Filtrado Eficiente:**
   - Use los filtros disponibles (`brand`, `provider`, `category`) para reducir el número de resultados
   - Los filtros se aplican a nivel de base de datos para mejor rendimiento

2. **Manejo de Campos Relacionados:**
   - Siempre verifique que `brand_id`, `subbrand_id`, `provider_id` existan antes de crear productos
   - Los campos `*_name` se calculan automáticamente, no es necesario enviarlos en POST/PUT

3. **Optimización de Consultas:**
   - La API ya incluye `select_related` para optimizar las consultas
   - No es necesario hacer múltiples llamadas para obtener información de marcas/proveedores

### Para el Desarrollo

1. **Mantenimiento de Propiedades del Modelo:**
   - Si se agregan nuevos campos relacionados, actualizar las propiedades correspondientes
   - Las propiedades deben manejar casos donde la relación sea `None`

2. **Extensión de la API:**
   - Para nuevos campos relacionados, seguir el patrón establecido
   - Agregar las propiedades al modelo y actualizar `django_to_pydantic`

3. **Testing:**
   - Verificar que los campos `*_name` no sean `null` en las respuestas
   - Probar con productos que tengan y no tengan relaciones establecidas

---

## 📚 Referencias Adicionales

- [Documentación de Autenticación JWT](./AUTHENTICATION.md)
- [Configuración de Marketplaces](./MARKETPLACE_SETUP.md)
- [Sistema de Sincronización](./SYNC_SYSTEM.md)
- [Guía de Permisos](./PERMISSIONS.md)
