# API de Credenciales de Marketplace

## Descripción

Esta API permite gestionar las credenciales de marketplace de los clientes. **El client_id se extrae automáticamente del JWT del usuario autenticado**, por lo que no es necesario enviarlo en el body de la request.

## Endpoints

### Base URL
```
/api/v1/marketplace-credentials/
```

## Operaciones CRUD

### 1. Crear Credenciales (POST)

**Endpoint:** `POST /api/v1/marketplace-credentials/`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Body:**
```json
{
    "marketplace_type": "shopify",
    "marketplace_name": "Mi Tienda Online",
    "credentials": {
        "shop_url": "https://mi-tienda.myshopify.com",
        "access_token": "shpca_1234567890abcdef1234567890abcdef",
        "api_version": "2024-01"
    },
    "webhook_url": "https://api.midominio.com/webhooks/shopify"
}
```

**Tipos de Marketplace Soportados:**

#### AWS (Amazon)
```json
{
    "marketplace_type": "amazon",
    "marketplace_name": "Mi Tienda Amazon",
    "credentials": {
        "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "aws_region": "us-east-1",
        "marketplace_id": "ATVPDKIKX0DER",
        "seller_id": "A1B2C3D4E5F6G7",
        "role_arn": "arn:aws:iam::123456789012:role/AmazonMarketplaceRole"
    }
}
```

#### Mercado Libre
```json
{
    "marketplace_type": "mercadolibre",
    "marketplace_name": "Mi Tienda ML",
    "credentials": {
        "access_token": "APP_USR-1234567890abcdef-123456-abcdef",
        "refresh_token": "TG-1234567890abcdef-123456",
        "user_id": "123456789",
        "country_code": "AR",
        "site_id": "MLA"
    }
}
```

#### Shopify
```json
{
    "marketplace_type": "shopify",
    "marketplace_name": "Mi Tienda Shopify",
    "credentials": {
        "shop_url": "https://mi-tienda.myshopify.com",
        "access_token": "shpca_1234567890abcdef1234567890abcdef",
        "api_version": "2024-01",
        "webhook_secret": "webhook_secret_123"
    }
}
```

### 2. Obtener Credenciales (GET)

**Listar todas:**
```
GET /api/v1/marketplace-credentials/
```

**Filtros disponibles:**
- `?client=1` - Filtrar por cliente
- `?marketplace_type=shopify` - Filtrar por tipo de marketplace
- `?connection_status=connected` - Filtrar por estado de conexión

**Obtener una específica:**
```
GET /api/v1/marketplace-credentials/{id}/
```

### 3. Actualizar Credenciales (PUT/PATCH)

**Endpoint:** `PUT /api/v1/marketplace-credentials/{id}/` o `PATCH /api/v1/marketplace-credentials/{id}/`

**Body (ejemplo para Shopify):**
```json
{
    "credentials": {
        "shop_url": "https://nueva-tienda.myshopify.com",
        "access_token": "nuevo_token_123",
        "api_version": "2024-01"
    },
    "webhook_url": "https://nuevo-dominio.com/webhooks/shopify"
}
```

### 4. Eliminar Credenciales (DELETE)

**Endpoint:** `DELETE /api/v1/marketplace-credentials/{id}/`

## Acciones Especiales

### Validar Credenciales
**Endpoint:** `POST /api/v1/marketplace-credentials/{id}/validate_credentials/`

Valida que las credenciales tengan el formato correcto según el tipo de marketplace.

### Obtener Schema de Credenciales
**Endpoint:** `GET /api/v1/marketplace-credentials/{id}/get_credential_schema/`

Retorna información sobre los campos requeridos y opcionales para el tipo de marketplace.

### Probar Conexión
**Endpoint:** `POST /api/v1/marketplace-credentials/{id}/test_connection/`

Prueba la conexión real con el marketplace usando las credenciales.

### Sincronizar Productos
**Endpoint:** `POST /api/v1/marketplace-credentials/{id}/sync_products_and_listings/`

Sincroniza productos y listings desde el marketplace.

## Validaciones

### AWS
- `aws_access_key_id`: Requerido, formato válido de AWS
- `aws_secret_access_key`: Requerido
- `aws_region`: Requerido, región válida de AWS
- `marketplace_id`: Requerido, ID válido de marketplace
- `seller_id`: Requerido, ID de vendedor

### Mercado Libre
- `access_token`: Requerido, token de acceso válido
- `refresh_token`: Requerido, token de refresco
- `user_id`: Requerido, ID de usuario
- `country_code`: Requerido, código de país válido
- `site_id`: Requerido, ID de sitio válido

### Shopify
- `shop_url`: Requerido, URL válida de Shopify
- `access_token`: Requerido, token de acceso válido
- `api_version`: Opcional, versión de API (default: 2024-01)

## Respuestas de Error

### Error de Validación
```json
{
    "error": "validation_failed",
    "message": "Credenciales inválidas para shopify: shop_url field required"
}
```

### Error de Duplicado
```json
{
    "error": "duplicate_credentials",
    "message": "Ya existen credenciales para el cliente Mi Cliente en shopify"
}
```

### Error de Tipo de Marketplace
```json
{
    "error": "invalid_marketplace_type",
    "message": "Tipo de marketplace inválido. Tipos válidos: amazon, mercadolibre, shopify, ebay, walmart",
    "received_type": "invalid_type"
}
```

## Códigos de Estado HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Credenciales creadas exitosamente
- `400 Bad Request` - Error de validación o datos inválidos
- `404 Not Found` - Credenciales no encontradas
- `500 Internal Server Error` - Error interno del servidor

## Notas Importantes

1. **Tipo de Marketplace**: Es obligatorio especificar el `marketplace_type` al crear credenciales
2. **Validación**: Las credenciales se validan automáticamente según el tipo de marketplace
3. **Duplicados**: No se permiten credenciales duplicadas para el mismo cliente y marketplace
4. **Seguridad**: Las credenciales se almacenan encriptadas en la base de datos
5. **Actualizaciones**: Al actualizar credenciales, se mantiene el tipo de marketplace original

## Resumen

He creado un sistema completo de API CRUD para credenciales de marketplace que incluye:

### 🔐 **Validaciones Específicas por Marketplace**
- **AWS**: Valida campos como `aws_access_key_id`, `aws_secret_access_key`, `aws_region`, etc.
- **Mercado Libre**: Valida `access_token`, `refresh_token`, `user_id`, `country_code`, `site_id`
- **Shopify**: Valida `shop_url`, `access_token`, `api_version`

### 🚀 **Funcionalidades del ViewSet**
- **CRUD completo** con validaciones específicas
- **Validación de credenciales** según el tipo de marketplace
- **Prevención de duplicados** por cliente y marketplace
- **Acciones especiales** como validar, probar conexión y sincronizar

### 📝 **Serializers Inteligentes**
- **Validación condicional** según el tipo de marketplace
- **Schemas específicos** para cada marketplace
- **Manejo de errores** detallado y descriptivo

### 🔍 **Endpoints Adicionales**
- `POST /{id}/validate_credentials/` - Validar formato de credenciales
- `GET /{id}/get_credential_schema/` - Obtener schema de validación
- `POST /{id}/test_connection/` - Probar conexión real
- `POST /{id}/sync_products_and_listings/` - Sincronizar productos

### 💡 **Características Clave**
1. **Validación automática** según el tipo de marketplace especificado
2. **Prevención de errores** con validaciones robustas
3. **Mensajes de error claros** para debugging
4. **Documentación completa** con ejemplos de uso
5. **Manejo de transacciones** para operaciones atómicas

El sistema está listo para usar y maneja automáticamente las diferencias entre marketplaces, validando que las credenciales tengan el formato correcto según el tipo especificado.
