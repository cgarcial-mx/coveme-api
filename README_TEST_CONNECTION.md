# Test Connection Feature

## 🎯 Overview

Se ha agregado un botón de "Test Connection" en el admin de Django para las credenciales de marketplace de clientes. Esta funcionalidad permite probar la conectividad y autenticación de las credenciales de API directamente desde el panel de administración.

## ✨ Features

- **Botón de Test Connection**: Disponible en la vista de lista y detalle del admin
- **Actualización de Estado en Tiempo Real**: El estado de conexión se actualiza automáticamente después de la prueba
- **Manejo de Errores**: Mensajes de error detallados se muestran y almacenan
- **Feedback Visual**: Indicadores de estado con códigos de color (verde para conectado, naranja para desconectado, rojo para error)
- **Soporte para Múltiples Marketplaces**: Amazon, Mercado Libre y Shopify

## 🚀 Cómo Usar

### 1. Acceder al Admin

Navega al admin de Django y ve a:
```
Admin > Clients > Client marketplace credentials
```

### 2. Probar una Conexión

1. Encuentra la credencial que quieres probar en la lista
2. Haz clic en el botón "Test Connection" en la columna "Test Connection"
3. El sistema intentará autenticarse con la API del marketplace
4. Serás redirigido de vuelta a la vista de detalle con un mensaje de éxito o error

### 3. Ver Resultados

- **Éxito**: El estado de conexión se actualizará a "Connected" (verde)
- **Error**: El estado de conexión se actualizará a "Error" (rojo) con información detallada del error

## 🔧 Marketplaces Soportados

### Amazon
- Prueba la autenticación de Amazon SP API
- Requiere credenciales: `lwa_app_id`, `lwa_client_secret`, `refresh_token`, `aws_access_key_id`, `aws_secret_access_key`, `role_arn`

### Mercado Libre
- Prueba la autenticación de Mercado Libre API
- Requiere credenciales: `access_token`, `refresh_token`, `client_id`, `client_secret`

### Shopify
- Prueba la autenticación de Shopify API
- Requiere credenciales: `shop_url`, `access_token`, `api_key`, `api_secret`

## 📁 Archivos Modificados/Creados

1. **`clients/utils.py`**: Contiene la lógica de prueba de conexión
2. **`clients/admin.py`**: Modificado para agregar el botón de test connection y funcionalidad
3. **`clients/static/clients/admin.css`**: CSS personalizado para el estilo del admin
4. **`scripts/test_connection_feature.py`**: Script de prueba para verificar la funcionalidad
5. **`docs/TEST_CONNECTION_FEATURE.md`**: Documentación técnica detallada

## 🧪 Testing

Para probar la funcionalidad:

```bash
# Crear credenciales de muestra y probar
python scripts/test_connection_feature.py --create-samples

# Solo probar con credenciales existentes
python scripts/test_connection_feature.py
```

## 🔒 Consideraciones de Seguridad

- Las credenciales se almacenan en la base de datos como JSON (considerar encriptación para producción)
- Las pruebas de conexión usan las mismas credenciales que las llamadas reales a la API
- No se exponen credenciales en los mensajes de error
- Todas las operaciones de prueba se registran para auditoría

## 🎨 Personalización del Admin

El admin incluye:
- Enrutamiento de URL personalizado para la acción de test connection
- Visualización de estado con códigos de color
- Botón de test connection estilizado
- Fieldsets organizados para mejor presentación de datos

## 🔮 Mejoras Futuras

Mejoras potenciales:
- Prueba en lote de múltiples credenciales
- Pruebas automáticas programadas
- Notificaciones por email para fallos de conexión
- Información más detallada de respuestas de API
- Soporte para marketplaces adicionales (eBay, Walmart, etc.)

## 📝 Notas de Desarrollo

- La funcionalidad utiliza los comandos de management existentes (`test_amazon_api`, `test_meli_api`, `test_shopify_api`)
- Los mensajes de éxito se detectan mediante indicadores específicos en la salida de los comandos
- El estado de conexión se actualiza automáticamente después de cada prueba
- Los errores se almacenan en el campo `last_error` del modelo
