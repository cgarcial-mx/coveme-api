#!/usr/bin/env python3
import os
import requests
from pathlib import Path

print("🚀 Simple Mercado Libre API Test")

# Load environment variables
env_file = Path.cwd() / '.env.local'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
    print("✅ Environment variables loaded")

# Get credentials
client_id = os.environ.get('MERCADOLIBRE_APP_ID')
client_secret = os.environ.get('MERCADOLIBRE_SECRET_KEY')
meli_url = os.environ.get('MERCADOLIBRE_URL', 'https://api.mercadolibre.com')

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret[:10]}...")
print(f"API URL: {meli_url}")

# Test authentication
url = f"{meli_url}/oauth/token"
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

print(f"\n🔐 Testing authentication...")
response = requests.post(url, data=data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get('access_token')
    print(f"✅ Success! Access token: {access_token[:20]}...")
    
    # Test categories API
    print(f"\n📂 Testing categories API...")
    site_id = os.environ.get('MERCADOLIBRE_SITE', 'MLM')
    categories_url = f"{meli_url}/sites/{site_id}/categories"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    cat_response = requests.get(categories_url, headers=headers)
    print(f"Categories status: {cat_response.status_code}")
    
    if cat_response.status_code == 200:
        categories = cat_response.json()
        print(f"✅ Found {len(categories)} categories")
        for i, cat in enumerate(categories[:5]):
            print(f"   {i+1}. {cat.get('name', 'N/A')}")
    else:
        print(f"❌ Categories failed: {cat_response.text[:100]}")
        
else:
    print(f"❌ Authentication failed: {response.text}")

print("\n🎉 Test completed!") 