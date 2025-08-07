# Sistema de Sincronización de Shopify

Este documento describe el sistema completo de sincronización de productos y listings de Shopify.

## 🎯 Objetivo

El sistema permite sincronizar automáticamente:
- **Productos** desde Shopify a la tabla `products.Product`
- **Listings** desde Shopify a la tabla `marketplaces.MarketplaceListing`

## 📋 Requisitos

### Variables de Entorno
Configura las siguientes variables en tu archivo `.env.local`:

```bash
# Shopify API Credentials
SHOPIFY_SHOP_URL=tu-tienda.myshopify.com
SHOPIFY_ACCESS_TOKEN=tu-access-token
SHOPIFY_API_VERSION=2024-01
```

### Dependencias
```bash
pip install Django djangorestframework django-filter requests
```

## 🚀 Uso

### 1. Probar Conexión

Antes de sincronizar, verifica que las credenciales funcionen:

```bash
python manage.py test_shopify_api --auth
```

### 2. Sincronización desde Línea de Comandos

#### Modo Dry-Run (Recomendado para pruebas)
```bash
python manage.py sync_shopify_products --dry-run --debug --limit 10
```

#### Sincronización Real
```bash
python manage.py sync_shopify_products --debug --limit 50
```

#### Sincronizar Credenciales Específicas
```bash
python manage.py sync_shopify_products --credentials-id 1 --limit 100
```

### 3. Sincronización via API REST

#### Probar Conexión
```bash
POST /api/v1/marketplace-credentials/{id}/test_connection/
```

#### Sincronizar Productos y Listings
```bash
POST /api/v1/marketplace-credentials/{id}/sync_products_and_listings/
Content-Type: application/json

{
    "dry_run": true,
    "limit": 10,
    "debug": true
}
```

## 📊 Estructura de Datos

### Productos Sincronizados (`products.Product`)
- **internal_sku**: Generado como `SHOPIFY_{product_id}`
- **title**: Título del producto en Shopify
- **description**: Descripción HTML del producto
- **brand**: Vendor de Shopify (creado automáticamente)
- **provider**: Mismo que brand
- **category**: Product type de Shopify
- **cost**: Precio del primer variant

### Listings Sincronizados (`marketplaces.MarketplaceListing`)
- **marketplace_id**: ID del producto en Shopify
- **external_sku**: Handle del producto
- **title**: Título del producto
- **price**: Precio del primer variant
- **inventory_quantity**: Suma de inventario de todos los variants
- **status**: Estado del producto en Shopify
- **thumbnail_url**: URL de la primera imagen
- **permalink**: URL del producto
- **metadata**: Información adicional (vendor, tags, etc.)

## 🔧 Comandos Disponibles

### `sync_shopify_products`

Sincroniza productos y listings de Shopify.

#### Opciones:
- `--client-id`: ID del cliente específico
- `--credentials-id`: ID de credenciales específicas
- `--dry-run`: Mostrar qué se sincronizaría sin hacer cambios
- `--force`: Forzar sincronización aunque las credenciales estén desconectadas
- `--limit`: Número máximo de productos a sincronizar (default: 100)
- `--debug`: Modo debug con salida detallada

### `test_shopify_api`

Prueba la conexión con la API de Shopify.

#### Opciones:
- `--auth`: Probar solo autenticación
- `--listings`: Probar consumo de productos
- `--orders`: Probar API de órdenes
- `--customers`: Probar API de clientes
- `--webhook`: Probar funcionalidad de webhooks
- `--full`: Prueba completa de todas las APIs
- `--debug`: Modo debug
- `--limit`: Número de productos a mostrar
- `--json`: Mostrar respuesta JSON completa

## 🌐 Endpoints de API

### Marketplace Credentials

#### Probar Conexión
```
POST /api/v1/marketplace-credentials/{id}/test_connection/
```

**Respuesta exitosa:**
```json
{
    "status": "success",
    "message": "Connection test completed",
    "output": "...",
    "connection_status": "connected"
}
```

#### Sincronizar Productos y Listings
```
POST /api/v1/marketplace-credentials/{id}/sync_products_and_listings/
```

**Body:**
```json
{
    "dry_run": true,
    "limit": 10,
    "debug": true
}
```

**Respuesta exitosa:**
```json
{
    "status": "success",
    "message": "Sync completed successfully",
    "output": "...",
    "sync_details": {
        "credential_id": 1,
        "client_name": "Mi Cliente",
        "marketplace_type": "shopify",
        "last_sync_at": "2024-01-01T12:00:00Z",
        "dry_run": true,
        "limit": 10,
        "debug": true
    }
}
```

## 🔄 Flujo de Sincronización

1. **Validación de Credenciales**
   - Verifica que existan shop_url y access_token
   - Prueba la conexión con la API de Shopify

2. **Sincronización de Productos**
   - Obtiene productos desde Shopify API
   - Crea/actualiza registros en `products.Product`
   - Crea marcas y proveedores automáticamente

3. **Sincronización de Listings**
   - Crea/actualiza registros en `marketplaces.MarketplaceListing`
   - Incluye información de precios, inventario e imágenes

4. **Actualización de Estado**
   - Actualiza `last_sync_at` en las credenciales
   - Registra errores si los hay

## 🛠️ Configuración Avanzada

### Personalizar Mapeo de Datos

Para personalizar cómo se mapean los datos de Shopify a tu base de datos, edita el archivo:
`api/management/commands/sync_shopify_products.py`

### Agregar Nuevos Marketplaces

Para agregar soporte para otros marketplaces:

1. Crear nuevo comando de sincronización
2. Agregar lógica en `clients/views.py`
3. Actualizar modelos según sea necesario

### Configurar Sincronización Automática

Para sincronización automática, puedes usar cron jobs:

```bash
# Sincronizar cada hora
0 * * * * cd /path/to/project && python manage.py sync_shopify_products --limit 100
```

## 🐛 Solución de Problemas

### Error: "Missing required credentials"
- Verifica que las variables de entorno estén configuradas
- Asegúrate de que el archivo `.env.local` existe

### Error: "Authentication failed"
- Verifica que el access_token sea válido
- Asegúrate de que la app tenga los permisos correctos

### Error: "Connection failed"
- Verifica que la shop_url sea correcta
- Asegúrate de que la tienda esté activa

### Productos no se sincronizan
- Verifica que haya productos en la tienda de Shopify
- Revisa los logs con `--debug` para más detalles

## 📈 Monitoreo

### Verificar Estado de Sincronización
```bash
# Ver productos sincronizados
python manage.py shell
>>> from products.models import Product
>>> Product.objects.filter(internal_sku__startswith='SHOPIFY_').count()

# Ver listings sincronizados
>>> from marketplaces.models import MarketplaceListing
>>> MarketplaceListing.objects.filter(marketplace_type='shopify').count()
```

### Logs de Sincronización
Los logs se guardan en:
- `last_sync_at`: Última sincronización exitosa
- `last_error`: Último error (si lo hay)
- `connection_status`: Estado de la conexión

## 🔐 Seguridad

- Las credenciales se almacenan encriptadas en la base de datos
- Los tokens de acceso deben tener permisos mínimos necesarios
- Se recomienda usar variables de entorno para las credenciales

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs con `--debug`
2. Verifica la configuración de credenciales
3. Prueba la conexión con `test_shopify_api --auth`
