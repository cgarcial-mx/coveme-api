#!/bin/bash

# Script para generar refresh token de Amazon
echo "🔄 Amazon SP API Refresh Token Generator"
echo "========================================"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "�� Activating virtual environment..."
    source venv/bin/activate
fi

# Verificar que existe el archivo .env.local
if [ ! -f ".env.local" ]; then
    echo "❌ Error: No se encontró el archivo .env.local"
    echo "�� Asegúrate de tener configurado:"
    echo "   - LWA_APP_ID"
    echo "   - LWA_CLIENT_SECRET"
    exit 1
fi

echo "✅ Archivo .env.local encontrado"
echo "�� Ejecutando comando de generación..."

# Ejecutar el comando de Django
python manage.py generate_amazon_refresh_token

echo ""
echo "�� Proceso completado!"
echo "📁 El refresh token se guardó en: amazon_refresh_token.json"
