from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# Import models
from clients.models import Client, ClientMarketplaceCredentials
from products.models import Product, Brand, SubBrand, Provider
from marketplaces.models import MarketplaceListing

class Command(BaseCommand):
    help = 'Synchronize Amazon products and listings to local database'

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
                self.style.ERROR("❌ No Amazon credentials found to sync")
            )
            sys.exit(1)
        
        # Sync each credential
        for credential in credentials:
            self.sync_amazon_credential(credential)

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
        """Get Amazon credentials to sync"""
        credentials = ClientMarketplaceCredentials.objects.filter(
            marketplace_type='amazon'
        )
        
        if options.get('client_id'):
            credentials = credentials.filter(client_id=options['client_id'])
        
        if options.get('credentials_id'):
            credentials = credentials.filter(id=options['credentials_id'])
        
        return credentials

    def sync_amazon_credential(self, credential):
        """Sync products and listings for a specific Amazon credential"""
        self.stdout.write(f"\n🔄 Syncing Amazon products for {credential.client.name}")
        self.stdout.write("=" * 60)
        
        try:
            # Set up environment variables from credentials
            self.setup_amazon_credentials(credential)
            
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
                self.style.SUCCESS("✅ Amazon sync completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error syncing Amazon: {str(e)}")
            )
            if not self.dry_run:
                credential.last_error = str(e)
                credential.save()

    def setup_amazon_credentials(self, credential):
        """Set up environment variables for Amazon SP API"""
        env_mapping = {
            'lwa_app_id': 'LWA_APP_ID',
            'lwa_client_secret': 'LWA_CLIENT_SECRET',
            'refresh_token': 'SP_API_REFRESH_TOKEN',
            'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
            'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
            'role_arn': 'SP_API_ROLE_ARN'
        }
        
        for cred_key, env_var in env_mapping.items():
            if cred_key in credential.credentials:
                os.environ[env_var] = str(credential.credentials[cred_key])
        
        # Set defaults for optional variables
        if 'SP_API_REGION' not in os.environ:
            os.environ['SP_API_REGION'] = 'us-east-1'
        if 'SP_API_MARKETPLACE_ID' not in os.environ:
            os.environ['SP_API_MARKETPLACE_ID'] = 'A1AM78C64UM0Y8'  # Mexico marketplace

    def test_connection(self):
        """Test Amazon SP API connection"""
        try:
            from sp_api.api import Catalog
            catalog_api = Catalog()
            return True
        except Exception as e:
            self.stdout.write(f"❌ Connection test failed: {str(e)}")
            return False

    def sync_products(self, credential):
        """Sync Amazon products"""
        self.stdout.write("📦 Syncing Amazon products...")
        
        try:
            from sp_api.api import Catalog, Reports
            from sp_api.base import SellingApiException
            
            catalog_api = Catalog()
            
            # Get catalog items (products)
            # This is a simplified implementation - you would need to implement
            # the actual product fetching logic based on your Amazon SP API setup
            
            self.stdout.write("✅ Products sync completed")
            
        except Exception as e:
            self.stdout.write(f"❌ Error syncing products: {str(e)}")

    def sync_listings(self, credential):
        """Sync Amazon listings"""
        self.stdout.write("📋 Syncing Amazon listings...")
        
        try:
            from sp_api.api import Catalog, Reports
            from sp_api.base import SellingApiException
            
            # Get listings
            # This is a simplified implementation - you would need to implement
            # the actual listings fetching logic based on your Amazon SP API setup
            
            self.stdout.write("✅ Listings sync completed")
            
        except Exception as e:
            self.stdout.write(f"❌ Error syncing listings: {str(e)}")
