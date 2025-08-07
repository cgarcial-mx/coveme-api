#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de sincronización de Shopify

Este script muestra cómo:
1. Probar la conexión con Shopify
2. Sincronizar productos y listings
3. Usar la API REST para sincronización
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Agregar el directorio del proyecto al path
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

def test_shopify_connection():
    """Probar la conexión con Shopify usando el comando de test"""
    print("🔐 Probando conexión con Shopify...")
    print("=" * 50)
    
    try:
        # Capturar la salida del comando
        output = StringIO()
        call_command('test_shopify_api', '--auth', stdout=output)
        output.seek(0)
        result = output.read()
        
        print(result)
        
        if '✅ Shopify API connection established successfully' in result:
            print("✅ Conexión exitosa!")
            return True
        else:
            print("❌ Conexión fallida!")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar conexión: {e}")
        return False

def sync_shopify_products_dry_run():
    """Ejecutar sincronización en modo dry-run para ver qué se sincronizaría"""
    print("\n🔄 Ejecutando sincronización en modo dry-run...")
    print("=" * 50)
    
    try:
        output = StringIO()
        call_command('sync_shopify_products', '--dry-run', '--debug', '--limit', '10', stdout=output)
        output.seek(0)
        result = output.read()
        
        print(result)
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")

def sync_shopify_products_real():
    """Ejecutar sincronización real"""
    print("\n🔄 Ejecutando sincronización real...")
    print("=" * 50)
    
    try:
        output = StringIO()
        call_command('sync_shopify_products', '--debug', '--limit', '20', stdout=output)
        output.seek(0)
        result = output.read()
        
        print(result)
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")

def test_api_endpoints():
    """Probar los endpoints de la API REST"""
    print("\n🌐 Probando endpoints de la API REST...")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Listar credenciales de marketplace
    try:
        response = requests.get(f"{base_url}/marketplace-credentials/")
        if response.status_code == 200:
            credentials = response.json()
            print(f"✅ Credenciales encontradas: {len(credentials.get('results', []))}")
            
            # Buscar credenciales de Shopify
            shopify_creds = [c for c in credentials.get('results', []) if c.get('marketplace_type') == 'shopify']
            
            if shopify_creds:
                cred_id = shopify_creds[0]['id']
                print(f"   Shopify credential ID: {cred_id}")
                
                # Probar endpoint de sincronización
                sync_url = f"{base_url}/marketplace-credentials/{cred_id}/sync_products_and_listings/"
                sync_data = {
                    'dry_run': True,
                    'limit': 5,
                    'debug': True
                }
                
                print(f"   Probando endpoint: {sync_url}")
                sync_response = requests.post(sync_url, json=sync_data)
                
                if sync_response.status_code == 200:
                    print("✅ Endpoint de sincronización funciona correctamente")
                    result = sync_response.json()
                    print(f"   Resultado: {result.get('status')}")
                else:
                    print(f"❌ Error en endpoint: {sync_response.status_code}")
                    print(f"   Respuesta: {sync_response.text}")
            else:
                print("⚠️ No se encontraron credenciales de Shopify")
                
        else:
            print(f"❌ Error al obtener credenciales: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al probar API: {e}")

def show_usage_examples():
    """Mostrar ejemplos de uso"""
    print("\n📚 Ejemplos de uso:")
    print("=" * 50)
    
    print("\n1. Probar conexión con Shopify:")
    print("   python manage.py test_shopify_api --auth")
    
    print("\n2. Sincronizar productos (dry-run):")
    print("   python manage.py sync_shopify_products --dry-run --debug --limit 10")
    
    print("\n3. Sincronizar productos (real):")
    print("   python manage.py sync_shopify_products --debug --limit 50")
    
    print("\n4. Sincronizar credenciales específicas:")
    print("   python manage.py sync_shopify_products --credentials-id 1 --limit 100")
    
    print("\n5. Usar API REST para sincronización:")
    print("   POST /api/v1/marketplace-credentials/{id}/sync_products_and_listings/")
    print("   Body: {'dry_run': True, 'limit': 10, 'debug': True}")
    
    print("\n6. Probar conexión via API REST:")
    print("   POST /api/v1/marketplace-credentials/{id}/test_connection/")

def main():
    """Función principal"""
    print("🚀 Sistema de Sincronización de Shopify")
    print("=" * 50)
    
    # Verificar que las variables de entorno estén configuradas
    required_vars = ['SHOPIFY_SHOP_URL', 'SHOPIFY_ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("⚠️ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Asegúrate de que tu archivo .env.local contenga estas variables")
        return
    
    print("✅ Variables de entorno configuradas correctamente")
    
    # Ejecutar pruebas
    test_shopify_connection()
    sync_shopify_products_dry_run()
    test_api_endpoints()
    show_usage_examples()
    
    print("\n🎉 Ejemplo completado!")
    print("\n💡 Para usar el sistema:")
    print("   1. Configura las credenciales de Shopify en .env.local")
    print("   2. Ejecuta los comandos de sincronización")
    print("   3. Usa la API REST para integración con frontend")

if __name__ == "__main__":
    main()
