from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Test Shopify API using requests library'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full API test instead of just authentication',
        )
        parser.add_argument(
            '--listings',
            action='store_true',
            help='Test products consumption from Shopify API',
        )
        parser.add_argument(
            '--orders',
            action='store_true',
            help='Test orders API',
        )
        parser.add_argument(
            '--auth',
            action='store_true',
            help='Test authentication and token validation',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with detailed API responses',
        )
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Test webhook functionality',
        )
        parser.add_argument(
            '--customers',
            action='store_true',
            help='Test customers API',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of products to display (default: 20)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output complete JSON response for products',
        )

    def handle(self, *args, **options):
        # Load environment variables from .env file
        self.load_env_file()
        
        # Set up environment variables for Shopify API
        if not self.setup_shopify_credentials():
            sys.exit(1)
        
        try:
            # Store debug mode, limit, and json output for use in other methods
            self.debug_mode = options.get('debug', False)
            self.product_limit = options.get('limit', 20)
            self.json_output = options.get('json', False)
            
            if options['listings']:
                self.test_products_consumption()
            elif options['orders']:
                self.test_orders_api()
            elif options['auth']:
                self.test_authentication()
            elif options['webhook']:
                self.test_webhook_functionality()
            elif options['customers']:
                self.test_customers_api()
            elif options['full']:
                self.test_full_api()
            else:
                self.test_authentication()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Test failed with error: {e}')
            )
            sys.exit(1)

    def load_env_file(self):
        """Load environment variables from .env file"""
        # Try .env.local first, then fall back to env.local for backward compatibility
        # Look in the current working directory (where manage.py is located)
        env_file = Path.cwd() / '.env.local'
        if not env_file.exists():
            env_file = Path.cwd() / 'env.local'
        
        if env_file.exists():
            loaded_vars = []
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value
                        loaded_vars.append(key)
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠️ No .env file found at: {env_file}")
            )

    def setup_shopify_credentials(self):
        """Set up environment variables for Shopify API authentication"""
        # Check if required environment variables are set
        required_vars = [
            'SHOPIFY_SHOP_URL',
            'SHOPIFY_ACCESS_TOKEN',
            'SHOPIFY_API_VERSION'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in os.environ:
                missing_vars.append(var)
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            )
            self.stdout.write("💡 Make sure your .env.local file contains all required variables:")
            self.stdout.write("   - SHOPIFY_SHOP_URL (e.g., your-store.myshopify.com)")
            self.stdout.write("   - SHOPIFY_ACCESS_TOKEN (your private app access token)")
            self.stdout.write("   - SHOPIFY_API_VERSION (e.g., 2024-01)")
            self.stdout.write("")
            self.stdout.write("📚 Shopify API Documentation:")
            self.stdout.write("   https://shopify.dev/docs/api")
            return False
        
        # Set default values for optional variables if not present
        if 'SHOPIFY_API_VERSION' not in os.environ:
            os.environ['SHOPIFY_API_VERSION'] = '2024-01'
        
        self.stdout.write(
            self.style.SUCCESS("✅ All required environment variables are set")
        )
        return True

    def get_shopify_headers(self):
        """Get headers for Shopify API requests"""
        return {
            'X-Shopify-Access-Token': os.environ['SHOPIFY_ACCESS_TOKEN'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_shopify_api_url(self, endpoint):
        """Build Shopify API URL with proper versioning"""
        shop_url = os.environ['SHOPIFY_SHOP_URL']
        api_version = os.environ['SHOPIFY_API_VERSION']
        
        # Ensure shop URL doesn't have protocol
        if shop_url.startswith('http'):
            shop_url = shop_url.replace('https://', '').replace('http://', '')
        
        return f"https://{shop_url}/admin/api/{api_version}/{endpoint}"

    def test_authentication(self):
        """Test only the authentication with Shopify API"""
        
        self.stdout.write("🔐 Testing Shopify API Authentication...")
        self.stdout.write("=" * 50)
        
        try:
            self.stdout.write("📋 Setting up Shopify API configuration...")
            
            # Test API connection by making a simple API call
            headers = self.get_shopify_headers()
            test_url = self.get_shopify_api_url('shop.json')
            
            if self.debug_mode:
                self.stdout.write(f"🔍 Debug: Testing URL: {test_url}")
                self.stdout.write(f"🔍 Debug: Headers: {headers}")
            
            response = requests.get(test_url, headers=headers)
            
            if self.debug_mode:
                self.stdout.write(f"🔍 Debug: Response status: {response.status_code}")
                self.stdout.write(f"🔍 Debug: Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_info = shop_data.get('shop', {})
                
                self.stdout.write(
                    self.style.SUCCESS("✅ Shopify API connection established successfully!")
                )
                self.stdout.write(f"   Shop Name: {shop_info.get('name', 'N/A')}")
                self.stdout.write(f"   Shop Domain: {shop_info.get('domain', 'N/A')}")
                self.stdout.write(f"   Shop Email: {shop_info.get('email', 'N/A')}")
                self.stdout.write(f"   Shop Country: {shop_info.get('country_name', 'N/A')}")
                self.stdout.write(f"   Shop Currency: {shop_info.get('currency', 'N/A')}")
                self.stdout.write(f"   API Version: {os.environ['SHOPIFY_API_VERSION']}")
                
            elif response.status_code == 401:
                self.stdout.write(
                    self.style.ERROR("❌ Authentication failed: Invalid access token")
                )
                self.stdout.write("💡 Check your SHOPIFY_ACCESS_TOKEN in .env.local")
                
            elif response.status_code == 403:
                self.stdout.write(
                    self.style.ERROR("❌ Authentication failed: Insufficient permissions")
                )
                self.stdout.write("💡 Check your app's permissions in Shopify admin")
                
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ API connection failed: {response.status_code}")
                )
                if self.debug_mode:
                    self.stdout.write(f"🔍 Debug: Response: {response.text}")
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Authentication test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Authentication failed: {e}")
            )
            self.stdout.write("=" * 50)
            self.stdout.write("🔍 Common issues:")
            self.stdout.write("   - Check if the shop URL is correct (your-store.myshopify.com)")
            self.stdout.write("   - Verify the access token is valid")
            self.stdout.write("   - Ensure the API version is supported")
            self.stdout.write("   - Check if the app has proper permissions")

    def test_full_api(self):
        """Test multiple Shopify API endpoints"""
        
        self.stdout.write("🔍 Testing Shopify API (Full Test)...")
        self.stdout.write("=" * 50)
        
        try:
            headers = self.get_shopify_headers()
            
            self.stdout.write("📋 Setting up API configuration...")
            self.stdout.write(
                self.style.SUCCESS("✅ API configuration created successfully")
            )
            
            # Test 1: Shop Info API
            self.stdout.write("\n🏪 Testing Shop Info API...")
            try:
                shop_url = self.get_shopify_api_url('shop.json')
                response = requests.get(shop_url, headers=headers)
                
                if response.status_code == 200:
                    shop_data = response.json()
                    shop_info = shop_data.get('shop', {})
                    self.stdout.write(
                        self.style.SUCCESS("✅ Shop Info API working correctly")
                    )
                    self.stdout.write(f"   Shop: {shop_info.get('name', 'N/A')}")
                    self.stdout.write(f"   Domain: {shop_info.get('domain', 'N/A')}")
                    self.stdout.write(f"   Plan: {shop_info.get('plan_name', 'N/A')}")
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Shop Info API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Shop Info API test failed: {e}")
                )
            
            # Test 2: Products API
            self.stdout.write("\n📦 Testing Products API...")
            try:
                products_url = self.get_shopify_api_url('products.json')
                response = requests.get(products_url, headers=headers, params={'limit': 10})
                
                if response.status_code == 200:
                    products_data = response.json()
                    products = products_data.get('products', [])
                    self.stdout.write(
                        self.style.SUCCESS("✅ Products API working correctly")
                    )
                    self.stdout.write(f"   Products available: {len(products)}")
                    
                    # If JSON output is requested, show complete JSON
                    if self.json_output:
                        self.output_complete_json(products_data, "Products")
                        return
                    
                    # Show detailed information for first few products
                    for i, product in enumerate(products[:5]):
                        self.stdout.write(f"\n   {i+1}. {product.get('title', 'N/A')}")
                        self.stdout.write(f"      ID: {product.get('id', 'N/A')}")
                        self.stdout.write(f"      Status: {product.get('status', 'N/A')}")
                        self.stdout.write(f"      Vendor: {product.get('vendor', 'N/A')}")
                        self.stdout.write(f"      Product Type: {product.get('product_type', 'N/A')}")
                        
                        # Show variants summary
                        variants = product.get('variants', [])
                        if variants:
                            self.stdout.write(f"      Variants: {len(variants)}")
                            prices = [float(v.get('price', 0)) for v in variants if v.get('price')]
                            if prices:
                                min_price = min(prices)
                                max_price = max(prices)
                                if min_price == max_price:
                                    self.stdout.write(f"      Price: ${min_price:.2f}")
                                else:
                                    self.stdout.write(f"      Price Range: ${min_price:.2f} - ${max_price:.2f}")
                        
                        # Show images summary
                        images = product.get('images', [])
                        if images:
                            self.stdout.write(f"      Images: {len(images)}")
                        
                        # Show tags
                        tags = product.get('tags', '')
                        if tags:
                            self.stdout.write(f"      Tags: {tags}")
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Products API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Products API test failed: {e}")
                )
            
            # Test 3: Orders API
            self.stdout.write("\n📋 Testing Orders API...")
            try:
                orders_url = self.get_shopify_api_url('orders.json')
                response = requests.get(orders_url, headers=headers, params={'limit': 5})
                
                if response.status_code == 200:
                    orders_data = response.json()
                    orders = orders_data.get('orders', [])
                    self.stdout.write(
                        self.style.SUCCESS("✅ Orders API working correctly")
                    )
                    self.stdout.write(f"   Orders available: {len(orders)}")
                    
                    # Show first few orders
                    for i, order in enumerate(orders[:3]):
                        self.stdout.write(f"   {i+1}. Order #{order.get('order_number', 'N/A')} - {order.get('financial_status', 'N/A')}")
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Orders API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API test failed: {e}")
                )
            
            # Test 4: Customers API
            self.stdout.write("\n👥 Testing Customers API...")
            try:
                customers_url = self.get_shopify_api_url('customers.json')
                response = requests.get(customers_url, headers=headers, params={'limit': 5})
                
                if response.status_code == 200:
                    customers_data = response.json()
                    customers = customers_data.get('customers', [])
                    self.stdout.write(
                        self.style.SUCCESS("✅ Customers API working correctly")
                    )
                    self.stdout.write(f"   Customers available: {len(customers)}")
                    
                    # Show first few customers
                    for i, customer in enumerate(customers[:3]):
                        self.stdout.write(f"   {i+1}. {customer.get('first_name', 'N/A')} {customer.get('last_name', 'N/A')} (ID: {customer.get('id', 'N/A')})")
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Customers API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Customers API test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Shopify API full test completed!")
            )
            self.stdout.write("✅ All API endpoints are working correctly")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_products_consumption(self):
        """Test consumption of products from Shopify API"""
        
        self.stdout.write("🛍️ Testing Shopify API Products Consumption...")
        self.stdout.write("=" * 60)
        
        try:
            headers = self.get_shopify_headers()
            
            self.stdout.write("📋 Setting up API configuration...")
            self.stdout.write(
                self.style.SUCCESS("✅ API configuration created successfully")
            )
            
            # Test 1: Get all products with detailed information
            self.stdout.write("\n📦 Testing Products API...")
            try:
                products_url = self.get_shopify_api_url('products.json')
                response = requests.get(products_url, headers=headers, params={'limit': self.product_limit})
                
                if response.status_code == 200:
                    products_data = response.json()
                    products = products_data.get('products', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(products)} products")
                    )
                    
                    # If JSON output is requested, show complete JSON
                    if self.json_output:
                        self.output_complete_json(products_data, "Products")
                        return
                    
                    # Display detailed information for up to the specified limit
                    for i, product in enumerate(products[:self.product_limit]):
                        self.stdout.write(f"\n{'='*60}")
                        self.stdout.write(f"📦 Product {i+1}: {product.get('title', 'N/A')}")
                        self.stdout.write(f"{'='*60}")
                        
                        # Basic Information
                        self.stdout.write(f"🆔 ID: {product.get('id', 'N/A')}")
                        self.stdout.write(f"📝 Title: {product.get('title', 'N/A')}")
                        self.stdout.write(f"🔗 Handle: {product.get('handle', 'N/A')}")
                        self.stdout.write(f"📊 Status: {product.get('status', 'N/A')}")
                        self.stdout.write(f"🏢 Vendor: {product.get('vendor', 'N/A')}")
                        self.stdout.write(f"🏷️ Product Type: {product.get('product_type', 'N/A')}")
                        self.stdout.write(f"📅 Created: {product.get('created_at', 'N/A')}")
                        self.stdout.write(f"🔄 Updated: {product.get('updated_at', 'N/A')}")
                        self.stdout.write(f"📋 Published: {product.get('published_at', 'N/A')}")
                        
                        # SEO Information
                        seo_title = product.get('seo', {}).get('title', 'N/A')
                        seo_description = product.get('seo', {}).get('description', 'N/A')
                        self.stdout.write(f"🔍 SEO Title: {seo_title}")
                        self.stdout.write(f"📄 SEO Description: {seo_description[:100]}{'...' if len(seo_description) > 100 else ''}")
                        
                        # Template Information
                        self.stdout.write(f"📄 Template Suffix: {product.get('template_suffix', 'N/A')}")
                        self.stdout.write(f"🌐 Published Scope: {product.get('published_scope', 'N/A')}")
                        
                        # Tags and Categories
                        tags = product.get('tags', '')
                        if tags:
                            self.stdout.write(f"🏷️ Tags: {tags}")
                        
                        # Description
                        body_html = product.get('body_html', '')
                        if body_html:
                            # Clean HTML tags for display
                            import re
                            clean_description = re.sub('<[^<]+?>', '', body_html)
                            self.stdout.write(f"📝 Description: {clean_description[:200]}{'...' if len(clean_description) > 200 else ''}")
                        
                        # Variants Information
                        variants = product.get('variants', [])
                        if variants:
                            self.stdout.write(f"\n🔄 Variants ({len(variants)}):")
                            for j, variant in enumerate(variants):
                                self.stdout.write(f"   {j+1}. {variant.get('title', 'N/A')}")
                                self.stdout.write(f"      ID: {variant.get('id', 'N/A')}")
                                self.stdout.write(f"      SKU: {variant.get('sku', 'N/A')}")
                                self.stdout.write(f"      Price: ${variant.get('price', 'N/A')}")
                                self.stdout.write(f"      Compare Price: ${variant.get('compare_at_price', 'N/A')}")
                                self.stdout.write(f"      Inventory: {variant.get('inventory_quantity', 'N/A')}")
                                self.stdout.write(f"      Weight: {variant.get('weight', 'N/A')} {variant.get('weight_unit', 'N/A')}")
                                self.stdout.write(f"      Barcode: {variant.get('barcode', 'N/A')}")
                                self.stdout.write(f"      Requires Shipping: {variant.get('requires_shipping', 'N/A')}")
                                self.stdout.write(f"      Taxable: {variant.get('taxable', 'N/A')}")
                                self.stdout.write(f"      Fulfillment Service: {variant.get('fulfillment_service', 'N/A')}")
                        
                        # Images Information
                        images = product.get('images', [])
                        if images:
                            self.stdout.write(f"\n🖼️ Images ({len(images)}):")
                            for k, image in enumerate(images[:5]):  # Show first 5 images
                                self.stdout.write(f"   {k+1}. {image.get('src', 'N/A')}")
                                self.stdout.write(f"      ID: {image.get('id', 'N/A')}")
                                self.stdout.write(f"      Position: {image.get('position', 'N/A')}")
                                self.stdout.write(f"      Width: {image.get('width', 'N/A')}px")
                                self.stdout.write(f"      Height: {image.get('height', 'N/A')}px")
                                self.stdout.write(f"      Alt: {image.get('alt', 'N/A')}")
                        
                        # Options Information
                        options = product.get('options', [])
                        if options:
                            self.stdout.write(f"\n⚙️ Options ({len(options)}):")
                            for l, option in enumerate(options):
                                self.stdout.write(f"   {l+1}. {option.get('name', 'N/A')}")
                                self.stdout.write(f"      Position: {option.get('position', 'N/A')}")
                                self.stdout.write(f"      Values: {', '.join(option.get('values', []))}")
                        
                        # Collections Information
                        collections = product.get('collections', [])
                        if collections:
                            self.stdout.write(f"\n📚 Collections ({len(collections)}):")
                            for m, collection in enumerate(collections):
                                self.stdout.write(f"   {m+1}. {collection.get('title', 'N/A')} (ID: {collection.get('id', 'N/A')})")
                        
                        # Inventory Information
                        total_inventory = sum(variant.get('inventory_quantity', 0) for variant in variants)
                        self.stdout.write(f"\n📦 Total Inventory: {total_inventory}")
                        
                        # Price Range
                        if variants:
                            prices = [float(variant.get('price', 0)) for variant in variants if variant.get('price')]
                            if prices:
                                min_price = min(prices)
                                max_price = max(prices)
                                if min_price == max_price:
                                    self.stdout.write(f"💰 Price: ${min_price:.2f}")
                                else:
                                    self.stdout.write(f"💰 Price Range: ${min_price:.2f} - ${max_price:.2f}")
                        
                        # Gift Card Information
                        gift_card = product.get('gift_card', False)
                        if gift_card:
                            self.stdout.write(f"🎁 Gift Card: Yes")
                        
                        # Google Shopping Information
                        google_product_category = product.get('google_product_category', '')
                        if google_product_category:
                            self.stdout.write(f"🛒 Google Product Category: {google_product_category}")
                        
                        # Metafields (if available)
                        metafields = product.get('metafields', [])
                        if metafields:
                            self.stdout.write(f"\n🔧 Metafields ({len(metafields)}):")
                            for n, metafield in enumerate(metafields[:3]):  # Show first 3 metafields
                                self.stdout.write(f"   {n+1}. {metafield.get('key', 'N/A')}: {metafield.get('value', 'N/A')}")
                        
                        self.stdout.write(f"\n{'='*60}")
                    
                    if len(products) > self.product_limit:
                        self.stdout.write(f"\n📊 ... and {len(products) - self.product_limit} more products")
                    
                    self.stdout.write(f"\n📊 Total products retrieved: {len(products)}")
                    
                    # Summary Statistics
                    self.stdout.write(f"\n📈 Product Summary:")
                    self.stdout.write(f"   - Active Products: {len([p for p in products if p.get('status') == 'active'])}")
                    self.stdout.write(f"   - Draft Products: {len([p for p in products if p.get('status') == 'draft'])}")
                    self.stdout.write(f"   - Archived Products: {len([p for p in products if p.get('status') == 'archived'])}")
                    
                    # Vendor Statistics
                    vendors = {}
                    for product in products:
                        vendor = product.get('vendor', 'Unknown')
                        vendors[vendor] = vendors.get(vendor, 0) + 1
                    
                    if vendors:
                        self.stdout.write(f"   - Vendors: {len(vendors)}")
                        top_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:3]
                        for vendor, count in top_vendors:
                            self.stdout.write(f"     * {vendor}: {count} products")
                    
                    # Product Type Statistics
                    product_types = {}
                    for product in products:
                        product_type = product.get('product_type', 'Unknown')
                        product_types[product_type] = product_types.get(product_type, 0) + 1
                    
                    if product_types:
                        self.stdout.write(f"   - Product Types: {len(product_types)}")
                        top_types = sorted(product_types.items(), key=lambda x: x[1], reverse=True)[:3]
                        for ptype, count in top_types:
                            self.stdout.write(f"     * {ptype}: {count} products")
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Products API error: {response.status_code}")
                    )
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Products test failed: {e}")
                )
            
            # Test 2: Get product details
            self.stdout.write("\n🔍 Testing Product Details API...")
            try:
                if 'products' in locals() and products:
                    test_product_id = products[0].get('id')
                    
                    product_url = self.get_shopify_api_url(f'products/{test_product_id}.json')
                    response = requests.get(product_url, headers=headers)
                    
                    if response.status_code == 200:
                        product_data = response.json()
                        product = product_data.get('product', {})
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for product: {test_product_id}")
                        )
                        self.stdout.write(f"   Title: {product.get('title', 'N/A')}")
                        self.stdout.write(f"   Description: {product.get('body_html', 'N/A')[:100]}...")
                        self.stdout.write(f"   Vendor: {product.get('vendor', 'N/A')}")
                        self.stdout.write(f"   Product Type: {product.get('product_type', 'N/A')}")
                        self.stdout.write(f"   Tags: {product.get('tags', 'N/A')}")
                        
                        # Show variants
                        variants = product.get('variants', [])
                        if variants:
                            self.stdout.write(f"   Variants: {len(variants)}")
                            for variant in variants:
                                self.stdout.write(f"     - {variant.get('title', 'N/A')} - ${variant.get('price', 'N/A')} - Inventory: {variant.get('inventory_quantity', 'N/A')}")
                        
                        # Show images
                        images = product.get('images', [])
                        if images:
                            self.stdout.write(f"   Images: {len(images)} available")
                            for i, image in enumerate(images[:3]):
                                self.stdout.write(f"     {i+1}. {image.get('src', 'N/A')}")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Product details failed: {response.status_code}")
                        )
                        self.stdout.write(f"   Response: {response.text}")
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No products available for details test")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Product details test failed: {e}")
                )
            
            # Test 3: Get product variants
            self.stdout.write("\n🔄 Testing Product Variants API...")
            try:
                if 'products' in locals() and products:
                    test_product_id = products[0].get('id')
                    
                    variants_url = self.get_shopify_api_url(f'products/{test_product_id}/variants.json')
                    response = requests.get(variants_url, headers=headers)
                    
                    if response.status_code == 200:
                        variants_data = response.json()
                        variants = variants_data.get('variants', [])
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved {len(variants)} variants for product: {test_product_id}")
                        )
                        
                        for i, variant in enumerate(variants):
                            self.stdout.write(f"\n🔄 Variant {i+1}:")
                            self.stdout.write(f"   ID: {variant.get('id', 'N/A')}")
                            self.stdout.write(f"   Title: {variant.get('title', 'N/A')}")
                            self.stdout.write(f"   SKU: {variant.get('sku', 'N/A')}")
                            self.stdout.write(f"   Price: ${variant.get('price', 'N/A')}")
                            self.stdout.write(f"   Inventory: {variant.get('inventory_quantity', 'N/A')}")
                            self.stdout.write(f"   Weight: {variant.get('weight', 'N/A')} {variant.get('weight_unit', 'N/A')}")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Product variants failed: {response.status_code}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No products available for variants test")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Product variants test failed: {e}")
                )
            
            # Test 4: Get product images
            self.stdout.write("\n🖼️ Testing Product Images API...")
            try:
                if 'products' in locals() and products:
                    test_product_id = products[0].get('id')
                    
                    images_url = self.get_shopify_api_url(f'products/{test_product_id}/images.json')
                    response = requests.get(images_url, headers=headers)
                    
                    if response.status_code == 200:
                        images_data = response.json()
                        images = images_data.get('images', [])
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved {len(images)} images for product: {test_product_id}")
                        )
                        
                        for i, image in enumerate(images):
                            self.stdout.write(f"\n🖼️ Image {i+1}:")
                            self.stdout.write(f"   ID: {image.get('id', 'N/A')}")
                            self.stdout.write(f"   Position: {image.get('position', 'N/A')}")
                            self.stdout.write(f"   Src: {image.get('src', 'N/A')}")
                            self.stdout.write(f"   Width: {image.get('width', 'N/A')}")
                            self.stdout.write(f"   Height: {image.get('height', 'N/A')}")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Product images failed: {response.status_code}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No products available for images test")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Product images test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS("🎉 Shopify API Products test completed!")
            )
            self.stdout.write("✅ Products consumption functionality is working")
            self.stdout.write("\n💡 Next steps:")
            self.stdout.write("   - Implement pagination for large product catalogs")
            self.stdout.write("   - Add filtering by collection or tags")
            self.stdout.write("   - Store products in your database")
            self.stdout.write("   - Set up regular sync schedules")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Products test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 60)

    def test_orders_api(self):
        """Test Orders API functionality"""
        
        self.stdout.write("📦 Testing Shopify API Orders...")
        self.stdout.write("=" * 50)
        
        try:
            headers = self.get_shopify_headers()
            
            self.stdout.write("📋 Setting up Orders API...")
            self.stdout.write(
                self.style.SUCCESS("✅ Orders API initialized successfully")
            )
            
            # Get recent orders
            self.stdout.write("\n🔄 Fetching recent orders...")
            
            try:
                orders_url = self.get_shopify_api_url('orders.json')
                response = requests.get(orders_url, headers=headers, params={'limit': 10, 'status': 'any'})
                
                if response.status_code == 200:
                    orders_data = response.json()
                    orders = orders_data.get('orders', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(orders)} orders")
                    )
                    
                    # Display first few orders as example
                    for i, order in enumerate(orders[:3]):  # Show first 3 orders
                        self.stdout.write(f"\n📦 Order {i+1}:")
                        self.stdout.write(f"   Order ID: {order.get('id', 'N/A')}")
                        self.stdout.write(f"   Order Number: #{order.get('order_number', 'N/A')}")
                        self.stdout.write(f"   Financial Status: {order.get('financial_status', 'N/A')}")
                        self.stdout.write(f"   Fulfillment Status: {order.get('fulfillment_status', 'N/A')}")
                        self.stdout.write(f"   Total Price: ${order.get('total_price', 'N/A')}")
                        self.stdout.write(f"   Currency: {order.get('currency', 'N/A')}")
                        self.stdout.write(f"   Created At: {order.get('created_at', 'N/A')}")
                        
                        # Show customer info
                        customer = order.get('customer', {})
                        if customer:
                            self.stdout.write(f"   Customer: {customer.get('first_name', 'N/A')} {customer.get('last_name', 'N/A')}")
                            self.stdout.write(f"   Customer Email: {customer.get('email', 'N/A')}")
                        
                        # Show line items
                        line_items = order.get('line_items', [])
                        if line_items:
                            self.stdout.write(f"   Items: {len(line_items)}")
                            for j, item in enumerate(line_items[:2]):  # Show first 2 items
                                self.stdout.write(f"     {j+1}. {item.get('title', 'N/A')} x{item.get('quantity', 'N/A')} - ${item.get('price', 'N/A')}")
                    
                    if len(orders) > 3:
                        self.stdout.write(f"\n... and {len(orders) - 3} more orders")
                    
                    self.stdout.write(f"\n📊 Total orders retrieved: {len(orders)}")
                    
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No orders found or API error")
                    )
                    self.stdout.write(f"   Status: {response.status_code}")
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error fetching orders: {e}")
                )
            
            # Test order details
            self.stdout.write("\n🔍 Testing Order Details API...")
            try:
                if 'orders' in locals() and orders:
                    test_order_id = orders[0].get('id')
                    
                    order_url = self.get_shopify_api_url(f'orders/{test_order_id}.json')
                    response = requests.get(order_url, headers=headers)
                    
                    if response.status_code == 200:
                        order_data = response.json()
                        order = order_data.get('order', {})
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for order: {test_order_id}")
                        )
                        self.stdout.write(f"   Order Number: #{order.get('order_number', 'N/A')}")
                        self.stdout.write(f"   Financial Status: {order.get('financial_status', 'N/A')}")
                        self.stdout.write(f"   Fulfillment Status: {order.get('fulfillment_status', 'N/A')}")
                        self.stdout.write(f"   Total Price: ${order.get('total_price', 'N/A')}")
                        self.stdout.write(f"   Subtotal: ${order.get('subtotal_price', 'N/A')}")
                        self.stdout.write(f"   Tax: ${order.get('total_tax', 'N/A')}")
                        self.stdout.write(f"   Shipping: ${order.get('total_shipping_price_set', {}).get('shop_money', {}).get('amount', 'N/A')}")
                        
                        # Show shipping address
                        shipping_address = order.get('shipping_address', {})
                        if shipping_address:
                            self.stdout.write(f"   Shipping Address: {shipping_address.get('address1', 'N/A')}, {shipping_address.get('city', 'N/A')}")
                        
                        # Show line items
                        line_items = order.get('line_items', [])
                        if line_items:
                            self.stdout.write(f"   Items: {len(line_items)}")
                            for item in line_items:
                                self.stdout.write(f"     - {item.get('title', 'N/A')} x{item.get('quantity', 'N/A')} - ${item.get('price', 'N/A')}")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Order details failed: {response.status_code}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ Skipping order details test - no orders available")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Order details test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Shopify API Orders test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Orders test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_customers_api(self):
        """Test Customers API functionality"""
        
        self.stdout.write("👥 Testing Shopify API Customers...")
        self.stdout.write("=" * 50)
        
        try:
            headers = self.get_shopify_headers()
            
            self.stdout.write("📋 Setting up Customers API...")
            self.stdout.write(
                self.style.SUCCESS("✅ Customers API initialized successfully")
            )
            
            # Get customers
            self.stdout.write("\n🔄 Fetching customers...")
            
            try:
                customers_url = self.get_shopify_api_url('customers.json')
                response = requests.get(customers_url, headers=headers, params={'limit': 10})
                
                if response.status_code == 200:
                    customers_data = response.json()
                    customers = customers_data.get('customers', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(customers)} customers")
                    )
                    
                    # Display first few customers as example
                    for i, customer in enumerate(customers[:3]):  # Show first 3 customers
                        self.stdout.write(f"\n👥 Customer {i+1}:")
                        self.stdout.write(f"   ID: {customer.get('id', 'N/A')}")
                        self.stdout.write(f"   Name: {customer.get('first_name', 'N/A')} {customer.get('last_name', 'N/A')}")
                        self.stdout.write(f"   Email: {customer.get('email', 'N/A')}")
                        self.stdout.write(f"   Phone: {customer.get('phone', 'N/A')}")
                        self.stdout.write(f"   Orders Count: {customer.get('orders_count', 'N/A')}")
                        self.stdout.write(f"   Total Spent: ${customer.get('total_spent', 'N/A')}")
                        self.stdout.write(f"   Created At: {customer.get('created_at', 'N/A')}")
                        
                        # Show default address
                        default_address = customer.get('default_address', {})
                        if default_address:
                            self.stdout.write(f"   Address: {default_address.get('address1', 'N/A')}, {default_address.get('city', 'N/A')}")
                    
                    if len(customers) > 3:
                        self.stdout.write(f"\n... and {len(customers) - 3} more customers")
                    
                    self.stdout.write(f"\n📊 Total customers retrieved: {len(customers)}")
                    
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No customers found or API error")
                    )
                    self.stdout.write(f"   Status: {response.status_code}")
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error fetching customers: {e}")
                )
            
            # Test customer details
            self.stdout.write("\n🔍 Testing Customer Details API...")
            try:
                if 'customers' in locals() and customers:
                    test_customer_id = customers[0].get('id')
                    
                    customer_url = self.get_shopify_api_url(f'customers/{test_customer_id}.json')
                    response = requests.get(customer_url, headers=headers)
                    
                    if response.status_code == 200:
                        customer_data = response.json()
                        customer = customer_data.get('customer', {})
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for customer: {test_customer_id}")
                        )
                        self.stdout.write(f"   Name: {customer.get('first_name', 'N/A')} {customer.get('last_name', 'N/A')}")
                        self.stdout.write(f"   Email: {customer.get('email', 'N/A')}")
                        self.stdout.write(f"   Phone: {customer.get('phone', 'N/A')}")
                        self.stdout.write(f"   Orders Count: {customer.get('orders_count', 'N/A')}")
                        self.stdout.write(f"   Total Spent: ${customer.get('total_spent', 'N/A')}")
                        self.stdout.write(f"   Verified Email: {customer.get('verified_email', 'N/A')}")
                        self.stdout.write(f"   Tax Exempt: {customer.get('tax_exempt', 'N/A')}")
                        
                        # Show addresses
                        addresses = customer.get('addresses', [])
                        if addresses:
                            self.stdout.write(f"   Addresses: {len(addresses)}")
                            for i, address in enumerate(addresses[:2]):
                                self.stdout.write(f"     {i+1}. {address.get('address1', 'N/A')}, {address.get('city', 'N/A')}")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Customer details failed: {response.status_code}")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ Skipping customer details test - no customers available")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Customer details test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Shopify API Customers test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Customers test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_webhook_functionality(self):
        """Test webhook functionality"""
        
        self.stdout.write("🔔 Testing Shopify API Webhooks...")
        self.stdout.write("=" * 50)
        
        try:
            headers = self.get_shopify_headers()
            
            self.stdout.write("📋 Setting up Webhooks API...")
            self.stdout.write(
                self.style.SUCCESS("✅ Webhooks API initialized successfully")
            )
            
            # Get existing webhooks
            self.stdout.write("\n🔄 Fetching existing webhooks...")
            
            try:
                webhooks_url = self.get_shopify_api_url('webhooks.json')
                response = requests.get(webhooks_url, headers=headers)
                
                if response.status_code == 200:
                    webhooks_data = response.json()
                    webhooks = webhooks_data.get('webhooks', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(webhooks)} webhooks")
                    )
                    
                    # Display webhooks
                    for i, webhook in enumerate(webhooks):
                        self.stdout.write(f"\n🔔 Webhook {i+1}:")
                        self.stdout.write(f"   ID: {webhook.get('id', 'N/A')}")
                        self.stdout.write(f"   Topic: {webhook.get('topic', 'N/A')}")
                        self.stdout.write(f"   Address: {webhook.get('address', 'N/A')}")
                        self.stdout.write(f"   Format: {webhook.get('format', 'N/A')}")
                        self.stdout.write(f"   Created At: {webhook.get('created_at', 'N/A')}")
                    
                    if not webhooks:
                        self.stdout.write("   No webhooks configured")
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Webhooks API failed: {response.status_code}")
                    )
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error fetching webhooks: {e}")
                )
            
            # Test webhook topics
            self.stdout.write("\n📋 Available webhook topics...")
            webhook_topics = [
                'orders/create',
                'orders/delete',
                'orders/updated',
                'orders/paid',
                'orders/cancelled',
                'products/create',
                'products/update',
                'products/delete',
                'customers/create',
                'customers/disable',
                'customers/enable',
                'customers/update',
                'inventory_levels/update',
                'app/uninstalled'
            ]
            
            self.stdout.write("   Available topics:")
            for topic in webhook_topics:
                self.stdout.write(f"     - {topic}")
            
            self.stdout.write("\n💡 To create a webhook, use:")
            self.stdout.write("   POST /admin/api/2024-01/webhooks.json")
            self.stdout.write("   Body: {'webhook': {'topic': 'orders/create', 'address': 'https://your-domain.com/webhook'}}")
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Shopify API Webhooks test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Webhooks test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50) 

    def output_complete_json(self, data, data_type):
        """Output complete JSON response for debugging and analysis"""
        
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"📄 Complete JSON Response for {data_type}")
        self.stdout.write(f"{'='*80}")
        
        # Pretty print the JSON with proper formatting
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Split into manageable chunks for display
        lines = json_str.split('\n')
        chunk_size = 50  # Show 50 lines at a time
        
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i + chunk_size]
            self.stdout.write('\n'.join(chunk))
            
            if i + chunk_size < len(lines):
                self.stdout.write(f"\n... (showing lines {i+1}-{i+chunk_size} of {len(lines)})")
                self.stdout.write("Press Enter to continue or Ctrl+C to stop...")
                try:
                    input()
                except KeyboardInterrupt:
                    self.stdout.write("\n📄 JSON output stopped by user")
                    break
        
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"📊 JSON Summary:")
        self.stdout.write(f"   - Total lines: {len(lines)}")
        self.stdout.write(f"   - Data type: {data_type}")
        
        # Show structure summary
        if isinstance(data, dict):
            self.stdout.write(f"   - Top-level keys: {', '.join(data.keys())}")
            
            # If it's products data, show product count
            if 'products' in data:
                products = data['products']
                self.stdout.write(f"   - Products count: {len(products)}")
                
                # Show sample product structure
                if products:
                    sample_product = products[0]
                    self.stdout.write(f"   - Sample product keys: {', '.join(sample_product.keys())}")
        
        self.stdout.write(f"{'='*80}")
        
        # Save to file option
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shopify_{data_type.lower()}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.stdout.write(f"💾 JSON saved to: {filename}")
            
        except Exception as e:
            self.stdout.write(f"⚠️ Could not save JSON file: {e}") 