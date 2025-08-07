from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import sys
import os
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

# Import models
from clients.models import Client, ClientMarketplaceCredentials
from products.models import Product, Brand, SubBrand, Provider
from marketplaces.models import MarketplaceListing

class Command(BaseCommand):
    help = 'Synchronize Shopify products and listings to local database'

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
                self.style.ERROR("❌ No Shopify credentials found to sync")
            )
            sys.exit(1)
        
        # Sync each credential
        for credential in credentials:
            self.sync_shopify_credential(credential)

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
        """Get Shopify credentials to sync"""
        credentials = ClientMarketplaceCredentials.objects.filter(
            marketplace_type='shopify'
        )
        
        if options.get('client_id'):
            credentials = credentials.filter(client_id=options['client_id'])
        
        if options.get('credentials_id'):
            credentials = credentials.filter(id=options['credentials_id'])
        
        if not self.force:
            credentials = credentials.filter(connection_status='connected')
        
        return credentials

    def sync_shopify_credential(self, credential):
        """Sync products and listings for a specific Shopify credential"""
        
        self.stdout.write(f"\n🔄 Syncing Shopify for client: {credential.client.name}")
        self.stdout.write("=" * 60)
        
        try:
            # Extract credentials
            shop_url = credential.credentials.get('shop_url')
            access_token = credential.credentials.get('access_token')
            api_version = credential.credentials.get('api_version', '2024-01')
            
            if not shop_url or not access_token:
                self.stdout.write(
                    self.style.ERROR("❌ Missing required credentials (shop_url or access_token)")
                )
                return
            
            # Set up API headers
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Build API URL
            if shop_url.startswith('http'):
                shop_url = shop_url.replace('https://', '').replace('http://', '')
            
            base_url = f"https://{shop_url}/admin/api/{api_version}"
            
            # Test connection first
            if not self.test_connection(base_url, headers):
                return
            
            # Sync products
            products_synced = self.sync_products(credential, base_url, headers)
            
            # Sync listings
            listings_synced = self.sync_listings(credential, base_url, headers)
            
            # Update credential status
            if not self.dry_run:
                credential.last_sync_at = timezone.now()
                credential.last_error = None
                credential.save()
            
            self.stdout.write(f"\n✅ Sync completed successfully!")
            self.stdout.write(f"   Products synced: {products_synced}")
            self.stdout.write(f"   Listings synced: {listings_synced}")
            
        except Exception as e:
            error_msg = f"❌ Sync failed: {str(e)}"
            self.stdout.write(self.style.ERROR(error_msg))
            
            if not self.dry_run:
                credential.last_error = error_msg
                credential.save()

    def test_connection(self, base_url, headers):
        """Test Shopify API connection"""
        try:
            response = requests.get(f"{base_url}/shop.json", headers=headers)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_info = shop_data.get('shop', {})
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Connected to Shopify store: {shop_info.get('name', 'N/A')}")
                )
                return True
                
            elif response.status_code == 401:
                self.stdout.write(
                    self.style.ERROR("❌ Authentication failed: Invalid access token")
                )
                return False
                
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Connection failed: {response.status_code}")
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Connection test failed: {e}")
            )
            return False

    def sync_products(self, credential, base_url, headers):
        """Sync Shopify products to local Product model"""
        
        self.stdout.write("\n📦 Syncing Shopify products...")
        
        try:
            # Get products from Shopify
            products_url = f"{base_url}/products.json"
            params = {'limit': self.limit}
            
            response = requests.get(products_url, headers=headers, params=params)
            
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to fetch products: {response.status_code}")
                )
                return 0
            
            products_data = response.json()
            shopify_products = products_data.get('products', [])
            
            self.stdout.write(f"   Found {len(shopify_products)} products in Shopify")
            
            products_synced = 0
            
            for shopify_product in shopify_products:
                try:
                    # Create or update product
                    product = self.create_or_update_product(credential.client, shopify_product)
                    
                    if product:
                        products_synced += 1
                        
                        if self.debug_mode:
                            self.stdout.write(f"   ✅ Synced product: {product.title}")
                    
                except Exception as e:
                    if self.debug_mode:
                        self.stdout.write(f"   ❌ Failed to sync product {shopify_product.get('id')}: {e}")
            
            self.stdout.write(f"   Successfully synced {products_synced} products")
            return products_synced
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Products sync failed: {e}")
            )
            return 0

    def create_or_update_product(self, client, shopify_product):
        """Create or update a Product from Shopify data"""
        
        # Generate internal SKU from Shopify product ID
        internal_sku = f"SHOPIFY_{shopify_product.get('id')}"
        
        # Get or create brand
        brand = None
        vendor = shopify_product.get('vendor')
        if vendor:
            brand, created = Brand.objects.get_or_create(
                client=client,
                name=vendor
            )
        
        # Get or create provider (same as brand for now)
        provider = None
        if vendor:
            provider, created = Provider.objects.get_or_create(
                client=client,
                name=vendor
            )
        
        # Prepare product data
        product_data = {
            'client': client,
            'internal_sku': internal_sku,
            'title': shopify_product.get('title', ''),
            'description': shopify_product.get('body_html', ''),
            'brand': brand,
            'provider': provider,
            'category': shopify_product.get('product_type', ''),
            'barcode': shopify_product.get('variants', [{}])[0].get('barcode', ''),
        }
        
        # Get price from first variant
        variants = shopify_product.get('variants', [])
        if variants:
            price = variants[0].get('price')
            if price:
                try:
                    product_data['cost'] = float(price)
                except (ValueError, TypeError):
                    pass
        
        if self.dry_run:
            self.stdout.write(f"   Would create/update product: {product_data['title']}")
            return None
        
        # Create or update product
        product, created = Product.objects.update_or_create(
            client=client,
            internal_sku=internal_sku,
            defaults=product_data
        )
        
        return product

    def sync_listings(self, credential, base_url, headers):
        """Sync Shopify products as marketplace listings"""
        
        self.stdout.write("\n🛍️ Syncing Shopify listings...")
        
        try:
            # Get products from Shopify
            products_url = f"{base_url}/products.json"
            params = {'limit': self.limit}
            
            response = requests.get(products_url, headers=headers, params=params)
            
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to fetch products for listings: {response.status_code}")
                )
                return 0
            
            products_data = response.json()
            shopify_products = products_data.get('products', [])
            
            listings_synced = 0
            
            for shopify_product in shopify_products:
                try:
                    # Create or update listing
                    listing = self.create_or_update_listing(credential.client, shopify_product)
                    
                    if listing:
                        listings_synced += 1
                        
                        if self.debug_mode:
                            self.stdout.write(f"   ✅ Synced listing: {listing.title}")
                    
                except Exception as e:
                    if self.debug_mode:
                        self.stdout.write(f"   ❌ Failed to sync listing {shopify_product.get('id')}: {e}")
            
            self.stdout.write(f"   Successfully synced {listings_synced} listings")
            return listings_synced
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Listings sync failed: {e}")
            )
            return 0

    def create_or_update_listing(self, client, shopify_product):
        """Create or update a MarketplaceListing from Shopify product"""
        
        marketplace_id = str(shopify_product.get('id'))
        
        # Get price from first variant
        price = None
        inventory_quantity = 0
        variants = shopify_product.get('variants', [])
        if variants:
            price = variants[0].get('price')
            inventory_quantity = sum(int(v.get('inventory_quantity', 0)) for v in variants)
        
        # Get images
        images = shopify_product.get('images', [])
        thumbnail_url = images[0].get('src') if images else None
        
        # Prepare listing data
        listing_data = {
            'client': client,
            'marketplace_type': 'shopify',
            'marketplace_id': marketplace_id,
            'external_sku': shopify_product.get('handle', ''),
            'title': shopify_product.get('title', ''),
            'price': float(price) if price else None,
            'currency': 'USD',  # Default, could be extracted from shop settings
            'inventory_quantity': inventory_quantity,
            'status': shopify_product.get('status', ''),
            'thumbnail_url': thumbnail_url,
            'permalink': f"https://{shopify_product.get('handle', '')}",
            'metadata': {
                'shopify_product_id': shopify_product.get('id'),
                'vendor': shopify_product.get('vendor'),
                'product_type': shopify_product.get('product_type'),
                'tags': shopify_product.get('tags'),
                'variants_count': len(variants),
                'images_count': len(images),
            }
        }
        
        if self.dry_run:
            self.stdout.write(f"   Would create/update listing: {listing_data['title']}")
            return None
        
        # Create or update listing
        listing, created = MarketplaceListing.objects.update_or_create(
            client=client,
            marketplace_type='shopify',
            marketplace_id=marketplace_id,
            defaults=listing_data
        )
        
        return listing
