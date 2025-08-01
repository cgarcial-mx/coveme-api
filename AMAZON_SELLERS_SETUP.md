# 🛍️ Guía de Configuración: Conectar Clientes a Amazon Sellers

Esta guía te ayudará a configurar múltiples clientes/vendedores para usar la API de Amazon Selling Partner (SP-API).

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Configuración de Amazon Seller Central](#configuración-de-amazon-seller-central)
- [Configuración de AWS IAM](#configuración-de-aws-iam)
- [Configuración en el Sistema](#configuración-en-el-sistema)
- [Uso y Pruebas](#uso-y-pruebas)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos Previos

### Software Necesario
- Python 3.8+
- Django 5.2+
- `python-amazon-sp-api` package
- Acceso a Amazon Seller Central
- Acceso a AWS Console

### Cuentas Requeridas
- **Amazon Seller Central** - Para crear la aplicación SP-API
- **AWS Console** - Para configurar IAM roles y credenciales
- **Cuenta de Vendedor Amazon** - Para obtener permisos de marketplace

## 🏪 Configuración de Amazon Seller Central

### Paso 1: Crear Aplicación en Seller Central

1. **Accede a Amazon Seller Central**
   ```
   https://sellercentral.amazon.com/
   ```

2. **Navega a Apps & Services → Develop Apps**
   - En el menú lateral, busca "Apps & Services"
   - Selecciona "Develop Apps"

3. **Crea una Nueva Aplicación**
   - Haz clic en "Create new app"
   - Completa la información básica:
     - **App name**: `Nombre de tu aplicación`
     - **App description**: `Descripción de la aplicación`
     - **App logo**: (Opcional)

4. **Configura los Permisos (Scopes)**
   - Selecciona los siguientes scopes según tus necesidades:
     ```
     ✅ catalog:read          # Para listar productos
     ✅ orders:read           # Para leer órdenes
     ✅ reports:read          # Para generar reportes
     ✅ notifications:read    # Para notificaciones
     ✅ inventory:read        # Para inventario
     ```

5. **Guarda la Aplicación**
   - Haz clic en "Save and continue"

### Paso 2: Obtener Credenciales LWA

1. **Copia las Credenciales de la Aplicación**
   - **Client ID**: `amzn1.application-oa2-client.XXXXXXXXX`
   - **Client Secret**: `amzn1.oa2-cs.v1.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

2. **Genera el Refresh Token**
   - Haz clic en "Generate refresh token"
   - Selecciona el marketplace correspondiente
   - Copia el refresh token generado

### Paso 3: Configurar Marketplace

Identifica el **Marketplace ID** según la región:

| Región | Marketplace ID | Descripción |
|--------|----------------|-------------|
| México | `A1AM78C64UM0Y8` | Amazon México |
| Estados Unidos | `ATVPDKIKX0DER` | Amazon US |
| Canadá | `A2EUQ1WTGCTBG2` | Amazon Canada |
| Brasil | `A2Q3Y263D00KWC` | Amazon Brazil |
| Reino Unido | `A1F83G8C2ARO7P` | Amazon UK |
| Alemania | `A1PA6795UKMFR9` | Amazon Germany |
| Francia | `A13V1IB3VIYZZH` | Amazon France |
| Italia | `APJ6JRA9NG5V4` | Amazon Italy |
| España | `A1RKKUPIHCS9HS` | Amazon Spain |

## ☁️ Configuración de AWS IAM

### Paso 1: Crear Usuario IAM

1. **Accede a AWS Console**
   ```
   https://console.aws.amazon.com/
   ```

2. **Navega a IAM → Users**
   - Busca "IAM" en los servicios
   - Selecciona "Users" en el menú lateral

3. **Crea un Nuevo Usuario**
   - Haz clic en "Add user"
   - **User name**: `amazon-sp-api-user`
   - **Access type**: Programmatic access

4. **Asigna Permisos**
   - Selecciona "Attach existing policies directly"
   - Busca y selecciona: `AmazonSellingPartnerAPIRole`

5. **Crea el Usuario**
   - Haz clic en "Next" y luego "Create user"

6. **Guarda las Credenciales**
   - **Access Key ID**: `AKIAXXXXXXXXXXXXXXXX`
   - **Secret Access Key**: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - ⚠️ **IMPORTANTE**: Guarda estas credenciales de forma segura

### Paso 2: Crear Role ARN

1. **Navega a IAM → Roles**
   - Selecciona "Roles" en el menú lateral

2. **Crea un Nuevo Role**
   - Haz clic en "Create role"
   - **Trusted entity**: AWS service
   - **Service**: Lambda (o el servicio que uses)

3. **Asigna Permisos**
   - Adjunta la política: `AmazonSellingPartnerAPIRole`

4. **Completa la Creación**
   - **Role name**: `AmazonSPAPIRole`
   - **Description**: `Role for Amazon SP-API access`

5. **Copia el Role ARN**
   - **Role ARN**: `arn:aws:iam::XXXXXXXXXX:role/AmazonSPAPIRole`

## ⚙️ Configuración en el Sistema

### Opción 1: Usando Archivos .env (Desarrollo)

Crea un archivo `.env.local` para cada cliente:

```bash
# Cliente 1 - México
# .env.cliente_mexico
LWA_APP_ID=amzn1.application-oa2-client.XXXXXXXXX
LWA_CLIENT_SECRET=amzn1.oa2-cs.v1.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SP_API_REFRESH_TOKEN=Atzr|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SP_API_ROLE_ARN=arn:aws:iam::XXXXXXXXXX:role/AmazonSPAPIRole
SP_API_REGION=us-east-1
SP_API_MARKETPLACE_ID=A1AM78C64UM0Y8
```

### Opción 2: Usando Base de Datos (Producción)

1. **Ejecuta las migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Crea un vendedor en la base de datos**
   ```python
   from api.models import AmazonSeller
   
   AmazonSeller.objects.create(
       name="Cliente México",
       seller_id="cliente_mexico",
       lwa_app_id="amzn1.application-oa2-client.XXXXXXXXX",
       lwa_client_secret="amzn1.oa2-cs.v1.XXXXXXXXXXXXXXXX",
       sp_api_refresh_token="Atzr|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
       aws_access_key_id="AKIAXXXXXXXXXXXXXXXX",
       aws_secret_access_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
       sp_api_role_arn="arn:aws:iam::XXXXXXXXXX:role/AmazonSPAPIRole",
       sp_api_region="us-east-1",
       sp_api_marketplace_id="A1AM78C64UM0Y8",
       is_active=True
   )
   ```

## 🧪 Uso y Pruebas

### Comando de Prueba

```bash
# Activar entorno virtual
source venv/bin/activate

# Probar con credenciales de archivo .env
python manage.py test_amazon_api

# Probar con credenciales de un vendedor específico
python manage.py test_amazon_api --seller-id cliente_mexico

# Probar funcionalidades específicas
python manage.py test_amazon_api --listings --seller-id cliente_mexico
python manage.py test_amazon_api --orders --seller-id cliente_mexico
python manage.py test_amazon_api --permissions --seller-id cliente_mexico
```

### Verificar Configuración

El comando debería mostrar:
```
✅ All required environment variables are set
🔐 Testing Amazon SP API Authentication...
✅ SP API configuration created successfully
✅ API connection established successfully!
✅ Your Amazon SP API credentials are working correctly
```

## 🔍 Solución de Problemas

### Error: "Missing required environment variables"

**Causa**: Faltan variables de entorno requeridas.

**Solución**:
1. Verifica que todas las credenciales estén configuradas
2. Revisa el formato del archivo `.env`
3. Asegúrate de que no haya espacios extra en los valores

### Error: "Access to requested resource is denied"

**Causa**: Permisos insuficientes en la aplicación SP-API.

**Solución**:
1. Verifica que los scopes estén configurados correctamente
2. Regenera el refresh token después de agregar scopes
3. Confirma que el marketplace esté habilitado

### Error: "Invalid Input"

**Causa**: Parámetros incorrectos en las llamadas a la API.

**Solución**:
1. Verifica el formato de las fechas (ISO 8601)
2. Confirma que los marketplace IDs sean correctos
3. Revisa la documentación de la API para parámetros requeridos

### Error: "Unauthorized"

**Causa**: Credenciales AWS incorrectas o role ARN mal configurado.

**Solución**:
1. Verifica las credenciales AWS
2. Confirma que el role ARN tenga los permisos correctos
3. Verifica que el usuario IAM pueda asumir el role

## 📊 Checklist de Configuración

### Para Cada Cliente/Vendedor:

- [ ] **Amazon Seller Central**
  - [ ] Aplicación creada con scopes correctos
  - [ ] Client ID y Client Secret obtenidos
  - [ ] Refresh Token generado
  - [ ] Marketplace ID identificado

- [ ] **AWS IAM**
  - [ ] Usuario IAM creado
  - [ ] Access Key ID y Secret Access Key obtenidos
  - [ ] Role ARN creado con permisos correctos
  - [ ] Política AmazonSellingPartnerAPIRole asignada

- [ ] **Sistema Local**
  - [ ] Archivo `.env` configurado (desarrollo)
  - [ ] Registro en base de datos (producción)
  - [ ] Comando de prueba ejecutado exitosamente
  - [ ] Funcionalidades específicas verificadas

## 🔐 Seguridad

### Mejores Prácticas:

1. **Nunca commits credenciales** en el código fuente
2. **Usa variables de entorno** para credenciales
3. **Rota las credenciales** regularmente
4. **Monitorea el uso** de las APIs
5. **Usa roles con mínimos privilegios** en AWS
6. **Encripta credenciales** en la base de datos

### Variables Sensibles:

```bash
# NUNCA incluir en el código
LWA_APP_ID=amzn1.application-oa2-client.XXXXXXXXX
LWA_CLIENT_SECRET=amzn1.oa2-cs.v1.XXXXXXXXXXXXXXXX
SP_API_REFRESH_TOKEN=Atzr|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SP_API_ROLE_ARN=arn:aws:iam::XXXXXXXXXX:role/RoleName
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** del comando de prueba
2. **Verifica la documentación** oficial de Amazon SP-API
3. **Consulta el checklist** de configuración
4. **Revisa los permisos** en Seller Central y AWS

---

**Nota**: Esta guía asume que ya tienes Django configurado y el paquete `python-amazon-sp-api` instalado. Para instalación inicial, consulta la documentación del proyecto.
