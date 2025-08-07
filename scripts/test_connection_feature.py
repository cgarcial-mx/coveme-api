#!/usr/bin/env python3
"""
Script to test the connection feature for marketplace credentials
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from clients.models import Client, ClientMarketplaceCredentials
from clients.utils import test_marketplace_connection

def test_connection_feature():
    """Test the connection feature with sample data"""
    
    print("🧪 Testing Connection Feature")
    print("=" * 50)
    
    # Check if there are any credentials in the database
    credentials_count = ClientMarketplaceCredentials.objects.count()
    print(f"Found {credentials_count} marketplace credentials in database")
    
    if credentials_count == 0:
        print("❌ No credentials found. Please create some credentials first.")
        return
    
    # Test each credential
    for credential in ClientMarketplaceCredentials.objects.all():
        print(f"\n🔍 Testing {credential.client.name} - {credential.get_marketplace_type_display()}")
        print("-" * 40)
        
        try:
            success, message = test_marketplace_connection(credential)
            
            if success:
                print(f"✅ {message}")
                # Update the credential status
                credential.connection_status = 'connected'
                credential.last_error = None
            else:
                print(f"❌ {message}")
                # Update the credential status
                credential.connection_status = 'error'
                credential.last_error = message
            
            credential.save()
            
        except Exception as e:
            print(f"❌ Error testing connection: {str(e)}")
            credential.connection_status = 'error'
            credential.last_error = str(e)
            credential.save()
    
    print("\n" + "=" * 50)
    print("🎉 Connection feature test completed!")

def create_sample_credentials():
    """Create sample credentials for testing"""
    
    print("📝 Creating sample credentials for testing...")
    
    # Create a sample client if it doesn't exist
    client, created = Client.objects.get_or_create(
        name="Test Client",
        defaults={
            'tax_id': 'TEST123',
            'subscription_plan': 'basic',
            'status': 'active'
        }
    )
    
    if created:
        print(f"✅ Created test client: {client.name}")
    else:
        print(f"📋 Using existing client: {client.name}")
    
    # Sample credentials for different marketplaces
    sample_credentials = {
        'amazon': {
            'lwa_app_id': 'test_app_id',
            'lwa_client_secret': 'test_client_secret',
            'refresh_token': 'test_refresh_token',
            'aws_access_key_id': 'test_access_key',
            'aws_secret_access_key': 'test_secret_key',
            'role_arn': 'test_role_arn'
        },
        'mercadolibre': {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        },
        'shopify': {
            'shop_url': 'test-shop.myshopify.com',
            'access_token': 'test_access_token',
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret'
        }
    }
    
    for marketplace_type, credentials in sample_credentials.items():
        credential, created = ClientMarketplaceCredentials.objects.get_or_create(
            client=client,
            marketplace_type=marketplace_type,
            defaults={
                'credentials': credentials,
                'connection_status': 'disconnected'
            }
        )
        
        if created:
            print(f"✅ Created {marketplace_type} credentials")
        else:
            print(f"📋 Using existing {marketplace_type} credentials")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the connection feature')
    parser.add_argument('--create-samples', action='store_true', 
                       help='Create sample credentials for testing')
    
    args = parser.parse_args()
    
    if args.create_samples:
        create_sample_credentials()
    
    test_connection_feature()
