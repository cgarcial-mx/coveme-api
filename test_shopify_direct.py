#!/usr/bin/env python3
"""
Simple test script to demonstrate Shopify API testing
This script shows how to use the test_shopify_api.py management command
"""

import os
import sys
from pathlib import Path

def main():
    print("🛍️ Shopify API Test Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if .env.local exists
    env_file = Path('.env.local')
    if not env_file.exists():
        print("⚠️ Warning: .env.local file not found.")
        print("💡 Please create a .env.local file with your Shopify credentials:")
        print("   SHOPIFY_SHOP_URL=your-store.myshopify.com")
        print("   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token")
        print("   SHOPIFY_API_VERSION=2024-01")
        print()
    
    print("📋 Available test commands:")
    print()
    print("🔐 Basic authentication test:")
    print("   python manage.py test_shopify_api")
    print()
    print("🔍 Full API test:")
    print("   python manage.py test_shopify_api --full")
    print()
    print("📦 Products/Listings test:")
print("   python manage.py test_shopify_api --listings")
print("   python manage.py test_shopify_api --listings --limit 50")
print("   python manage.py test_shopify_api --listings --json")
print("   python manage.py test_shopify_api --listings --json --limit 10")
    print()
    print("📋 Orders test:")
    print("   python manage.py test_shopify_api --orders")
    print()
    print("👥 Customers test:")
    print("   python manage.py test_shopify_api --customers")
    print()
    print("🔔 Webhooks test:")
    print("   python manage.py test_shopify_api --webhook")
    print()
    print("🔧 Debug mode (shows detailed API responses):")
    print("   python manage.py test_shopify_api --debug")
    print()
    print("📚 Shopify API Documentation:")
    print("   https://shopify.dev/docs/api")
    print()
    print("💡 Setup Instructions:")
    print("1. Create a Shopify Private App in your store admin")
    print("2. Get the access token from the app settings")
    print("3. Add your credentials to .env.local file")
    print("4. Run the test commands above")
    print()
    print("🎯 Example usage:")
print("   python manage.py test_shopify_api --full --debug")
print("   python manage.py test_shopify_api --listings --limit 30")
print("   python manage.py test_shopify_api --listings --debug --limit 10")
print("   python manage.py test_shopify_api --listings --json --limit 5")
print("   python manage.py test_shopify_api --full --json")

if __name__ == "__main__":
    main() 