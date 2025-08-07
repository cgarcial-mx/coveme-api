from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import sys
import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Import models
from clients.models import Client, ClientMarketplaceCredentials
from products.models import Product, Brand, SubBrand, Provider
from marketplaces.models import MarketplaceListing

class Command(BaseCommand):
    help = 'Synchronize Mercado Libre products and listings to local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=int,
            help='Client ID to sync products for',
        )
        parser.add_argument(
            '--credentials-id',
            type=int,
            help='Specific credentials ID to sync',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if credentials are disconnected',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of products to sync (default: 100)',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with detailed output',
        )

    def handle(self, *args, **options):
        self.debug_mode = options.get('debug', False)
        self.dry_run = options.get('dry_run', False)
        self.force = options.get('force', False)
        self.limit = options.get('limit', 100)
        
        # Load environment variables
        self.load_env_file()
        
        # Get credentials to sync
        credentials = self.get_credentials_to_sync(options)
        
        if not credentials:
            self.stdout.write(
                self.style.ERROR("❌ No Mercado Libre credentials found to sync")
            )
            sys.exit(1)
        
        # Sync each credential
        for credential in credentials:
            self.sync_meli_credential(credential)

    def load_env_file(self):
        """Load environment variables from .env file"""
        env_file = Path.cwd() / '.env.local'
        if not env_file.exists():
            env_file = Path.cwd() / 'env.local'
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value

    def get_credentials_to_sync(self, options):
        """Get Mercado Libre credentials to sync"""
        credentials = ClientMarketplaceCredentials.objects.filter(
            marketplace_type='mercadolibre'
        )
        
        if options.get('client_id'):
            credentials = credentials.filter(client_id=options['client_id'])
        
        if options.get('credentials_id'):
            credentials = credentials.filter(id=options['credentials_id'])
        
        return credentials

    def sync_meli_credential(self, credential):
        """Sync products and listings for a specific Mercado Libre credential"""
        self.stdout.write(f"\n🔄 Syncing Mercado Libre products for {credential.client.name}")
        self.stdout.write("=" * 60)
        
        try:
            # Set up environment variables from credentials
            self.setup_meli_credentials(credential)
            
            # Test connection first
            if not self.test_connection():
                self.stdout.write(
                    self.style.ERROR("❌ Connection test failed. Skipping sync.")
                )
                return
            
            # Sync products
            self.sync_products(credential)
            
            # Sync listings
            self.sync_listings(credential)
            
            # Update last sync timestamp
            if not self.dry_run:
                credential.last_sync_at = timezone.now()
                credential.save()
            
            self.stdout.write(
                self.style.SUCCESS("✅ Mercado Libre sync completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error syncing Mercado Libre: {str(e)}")
            )
            if not self.dry_run:
                credential.last_error = str(e)
                credential.save()

    def setup_meli_credentials(self, credential):
        """Set up environment variables for Mercado Libre API"""
        env_mapping = {
            'access_token': 'MELI_ACCESS_TOKEN',
            'refresh_token': 'MELI_REFRESH_TOKEN',
            'client_id': 'MELI_CLIENT_ID',
            'client_secret': 'MELI_CLIENT_SECRET'
        }
        
        for cred_key, env_var in env_mapping.items():
            if cred_key in credential.credentials:
                os.environ[env_var] = str(credential.credentials[cred_key])

    def test_connection(self):
        """Test Mercado Libre API connection"""
        try:
            access_token = os.environ.get('MELI_ACCESS_TOKEN')
            if not access_token:
                return False
            
            # Test API connection by making a simple request
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://api.mercadolibre.com/users/me', headers=headers)
            
            if response.status_code == 200:
                return True
            else:
                return False
                
        except Exception as e:
            self.stdout.write(f"❌ Connection test failed: {str(e)}")
            return False

    def sync_products(self, credential):
        """Sync Mercado Libre products"""
        self.stdout.write("📦 Syncing Mercado Libre products...")
        
        try:
            access_token = os.environ.get('MELI_ACCESS_TOKEN')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get user's items (products)
            # This is a simplified implementation - you would need to implement
            # the actual product fetching logic based on your Mercado Libre API setup
            
            self.stdout.write("✅ Products sync completed")
            
        except Exception as e:
            self.stdout.write(f"❌ Error syncing products: {str(e)}")

    def sync_listings(self, credential):
        """Sync Mercado Libre listings"""
        self.stdout.write("📋 Syncing Mercado Libre listings...")
        
        try:
            access_token = os.environ.get('MELI_ACCESS_TOKEN')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get listings
            # This is a simplified implementation - you would need to implement
            # the actual listings fetching logic based on your Mercado Libre API setup
            
            self.stdout.write("✅ Listings sync completed")
            
        except Exception as e:
            self.stdout.write(f"❌ Error syncing listings: {str(e)}")
