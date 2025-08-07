# Coveme API - Multi-Marketplace Product Management

## 🚀 Descripción

Coveme API es una plataforma completa para la gestión de productos en múltiples marketplaces (Amazon, Mercado Libre, Shopify, eBay, Walmart) con capacidades avanzadas de matching automático, sincronización de datos y análisis de mercado.

## 🏗️ Arquitectura

### Apps Django

- **`core`**: Modelos base, usuarios extendidos y funcionalidades comunes
- **`clients`**: Gestión de clientes y credenciales de marketplace
- **`products`**: Catálogo de productos, marcas, sub-marcas y proveedores
- **`marketplaces`**: Listados, coincidencias, historial de precios y trazabilidad
- **`orders`**: Gestión de órdenes y items de orden
- **`feedback`**: Reviews, preguntas y comentarios de clientes
- **`analytics`**: Logs de API y métricas de rendimiento

### Características Principales

- ✅ **Multi-tenant**: Soporte para múltiples clientes
- ✅ **Multi-marketplace**: Amazon, Mercado Libre, Shopify, eBay, Walmart
- ✅ **Matching inteligente**: Algoritmo de coincidencia automática de productos
- ✅ **Trazabilidad**: Historial de precios y análisis competitivo
- ✅ **APIs RESTful**: Endpoints completos con filtros y paginación
- ✅ **Admin Django**: Interfaz de administración completa
- ✅ **Autenticación**: Sistema de usuarios y permisos por roles

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8+
- pip
- virtualenv

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd coveme-api/api
```

2. **Crear y activar virtualenv**
```bash
python -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

5. **Aplicar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Crear datos de ejemplo (opcional)**
```bash
python create_sample_data.py
```

## 🚀 Ejecución

### Servidor de desarrollo
```bash
./run_server.sh
```

O manualmente:
```bash
source venv/bin/activate
export PYTHONPATH=/path/to/venv/lib/python3.13/site-packages
python manage.py runserver 0.0.0.0:8000
```

### URLs de acceso

- **Admin Django**: http://localhost:8000/admin/
- **API REST**: http://localhost:8000/api/v1/
- **Autenticación API**: http://localhost:8000/api-auth/

### Credenciales de ejemplo

- **Superusuario**: `admin` / `admin123`
- **Usuario demo**: `demo_user` / `demo123`

## 📊 Base de Datos

### Esquema Optimizado

El proyecto utiliza un esquema optimizado para multi-marketplace con las siguientes características:

- **Tabla única de coincidencias**: `product_matches` relaciona productos con listados de marketplace
- **Multi-tenant**: Todos los datos están aislados por cliente
- **Escalabilidad**: Diseño optimizado para crecimiento
- **Trazabilidad completa**: Historial de cambios y auditoría

### Tablas Principales

| Tabla | Propósito |
|-------|-----------|
| `clients` | Empresas que usan la plataforma |
| `users` | Usuarios con roles y permisos |
| `products` | Catálogo central de productos |
| `marketplace_listings` | Listados específicos por marketplace |
| `product_matches` | Coincidencias entre productos y listados |
| `orders` | Órdenes de todos los marketplaces |
| `customer_feedback` | Reviews y comentarios de clientes |

## 🔌 APIs

### Endpoints Principales

#### Clientes
- `GET /api/v1/clients/` - Listar clientes
- `POST /api/v1/clients/` - Crear cliente
- `GET /api/v1/clients/{id}/` - Obtener cliente
- `PUT /api/v1/clients/{id}/` - Actualizar cliente

#### Productos
- `GET /api/v1/products/` - Listar productos
- `POST /api/v1/products/` - Crear producto
- `GET /api/v1/products/{id}/` - Obtener producto
- `PUT /api/v1/products/{id}/` - Actualizar producto

#### Listados de Marketplace
- `GET /api/v1/marketplace-listings/` - Listar listados
- `POST /api/v1/marketplace-listings/` - Crear listado
- `GET /api/v1/marketplace-listings/{id}/` - Obtener listado

#### Coincidencias de Productos
- `GET /api/v1/product-matches/` - Listar coincidencias
- `POST /api/v1/product-matches/` - Crear coincidencia
- `GET /api/v1/product-matches/manual-reviews/` - Revisión manual
- `POST /api/v1/product-matches/start_sync/` - Iniciar sincronización

#### Órdenes
- `GET /api/v1/orders/` - Listar órdenes
- `GET /api/v1/orders/{id}/` - Obtener orden
- `GET /api/v1/order-items/` - Listar items de orden

#### Feedback de Clientes
- `GET /api/v1/customer-feedback/` - Listar feedback
- `POST /api/v1/customer-feedback/` - Crear feedback
- `PUT /api/v1/customer-feedback/{id}/` - Actualizar feedback

### Filtros Disponibles

Todos los endpoints soportan filtros por:
- `client` - Filtrar por cliente
- `marketplace_type` - Filtrar por tipo de marketplace
- `status` - Filtrar por estado
- `created_at` - Filtrar por fecha de creación

### Ejemplos de uso

```bash
# Obtener productos de un cliente específico
curl -X GET "http://localhost:8000/api/v1/products/?client=1"

# Obtener listados de Amazon
curl -X GET "http://localhost:8000/api/v1/marketplace-listings/?marketplace_type=amazon"

# Obtener coincidencias que necesitan revisión manual
curl -X GET "http://localhost:8000/api/v1/product-matches/manual-reviews/"
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Para PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=coveme_db
DB_USER=coveme_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Configuración de Marketplace

Cada marketplace requiere credenciales específicas:

#### Amazon SP-API
```json
{
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1",
    "marketplace_id": "ATVPDKIKX0DER",
    "seller_id": "A1AM78C64UM0Y8"
}
```

#### Mercado Libre
```json
{
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
}
```

#### Shopify
```json
{
    "shop_url": "your-shop.myshopify.com",
    "access_token": "your_access_token",
    "api_version": "2024-01"
}
```

## 📈 Funcionalidades Avanzadas

### Matching de Productos

El sistema incluye un algoritmo inteligente de matching que:

1. **Análisis de similitud**: Compara títulos, marcas, SKUs
2. **Score de confianza**: Calcula probabilidad de coincidencia
3. **Matching automático**: Para coincidencias ≥ 85%
4. **Revisión manual**: Para coincidencias 60-85%
5. **Creación de nuevos**: Para coincidencias < 60%

### Sincronización

- **Sincronización automática** de productos entre marketplaces
- **Actualización de precios** en tiempo real
- **Sincronización de inventario** automática
- **Webhooks** para actualizaciones en tiempo real

### Análisis de Mercado

- **Trazabilidad de competidores** con historial de precios
- **Análisis de tendencias** de ventas
- **Métricas de rendimiento** por marketplace
- **Reportes personalizados** por cliente

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Tests específicos
python manage.py test core
python manage.py test clients
python manage.py test products
```

## 📚 Documentación API

La documentación completa de la API está disponible en:
- **Swagger UI**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- 📧 Email: support@coveme.com
- 📖 Documentación: https://docs.coveme.com
- 🐛 Issues: https://github.com/coveme/api/issues

---

**Coveme API** - Gestión inteligente de productos multi-marketplace 🚀
