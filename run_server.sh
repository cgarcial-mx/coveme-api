#!/bin/bash

# Activar virtualenv y ejecutar servidor Django
source venv/bin/activate
export PYTHONPATH=/home/carlos/Documentos/coveme/coveme-api/api/venv/lib/python3.13/site-packages

echo "🚀 Iniciando servidor Django..."
echo "📊 Admin: http://localhost:8000/admin/"
echo "🔗 API: http://localhost:8000/api/v1/"
echo "👤 Usuario admin: admin / admin123"
echo "👤 Usuario demo: demo_user / demo123"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver 0.0.0.0:8000
