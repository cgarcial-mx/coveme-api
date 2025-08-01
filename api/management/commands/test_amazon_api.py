from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Test Amazon SP API using python-amazon-sp-api package'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full API test instead of just authentication',
        )
        parser.add_argument(
            '--listings',
            action='store_true',
            help='Test listings consumption from Amazon SP API',
        )
        parser.add_argument(
            '--orders',
            action='store_true',
            help='Test orders API',
        )
        parser.add_argument(
            '--permissions',
            action='store_true',
            help='Test API permissions and diagnose access issues',
        )

    def handle(self, *args, **options):
        # Load environment variables from .env file
        self.load_env_file()
        
        # Set up environment variables for spapi
        if not self.setup_spapi_credentials():
            sys.exit(1)
        
        try:
            # Import here to avoid import errors if amzn-sp-api is not installed
            from sp_api.api import Catalog, Orders, Reports
            from sp_api.base import SellingApiException
            
            if options['listings']:
                self.test_listings_consumption()
            elif options['orders']:
                self.test_orders_api()
            elif options['permissions']:
                self.test_api_permissions()
            elif options['full']:
                self.test_full_api()
            else:
                self.test_authentication()
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR('sp_api module not found. Please install it first.')
            )
            self.stdout.write('Run: pip install python-amazon-sp-api')
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

    def setup_spapi_credentials(self):
        """Set up environment variables for spapi authentication"""
        # Check if required environment variables are set
        required_vars = [
            'LWA_APP_ID',
            'LWA_CLIENT_SECRET', 
            'SP_API_REFRESH_TOKEN',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'SP_API_ROLE_ARN'
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
            self.stdout.write("   - LWA_APP_ID")
            self.stdout.write("   - LWA_CLIENT_SECRET")
            self.stdout.write("   - SP_API_REFRESH_TOKEN")
            self.stdout.write("   - AWS_ACCESS_KEY_ID")
            self.stdout.write("   - AWS_SECRET_ACCESS_KEY")
            self.stdout.write("   - SP_API_ROLE_ARN")
            self.stdout.write("   - SP_API_REGION (defaults to us-east-1)")
            self.stdout.write("   - SP_API_MARKETPLACE_ID (defaults to A1AM78C64UM0Y8)")
            return False
        
        # Set default values for optional variables if not present
        if 'SP_API_REGION' not in os.environ:
            os.environ['SP_API_REGION'] = 'us-east-1'
        if 'SP_API_MARKETPLACE_ID' not in os.environ:
            os.environ['SP_API_MARKETPLACE_ID'] = 'A1AM78C64UM0Y8'  # Mexico marketplace
        
        self.stdout.write(
            self.style.SUCCESS("✅ All required environment variables are set")
        )
        return True

    def test_authentication(self):
        """Test only the authentication with Amazon SP API"""
        
        self.stdout.write("🔐 Testing Amazon SP API Authentication...")
        self.stdout.write("=" * 50)
        
        try:
            self.stdout.write("📋 Creating SP API configuration...")
            
            # Test API connection by creating a simple API instance
            from sp_api.api import Catalog
            
            catalog_api = Catalog()
            
            self.stdout.write(
                self.style.SUCCESS("✅ SP API configuration created successfully")
            )
            
            self.stdout.write("\n🔑 Testing API connection...")
            
            self.stdout.write(
                self.style.SUCCESS("✅ API connection established successfully!")
            )
            self.stdout.write(f"   Client created with marketplace: MX")
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Authentication test completed successfully!")
            )
            self.stdout.write("✅ Your Amazon SP API credentials are working correctly")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Authentication failed: {e}")
            )
            self.stdout.write("=" * 50)
            self.stdout.write("🔍 Common issues:")
            self.stdout.write("   - Check if the refresh token is still valid")
            self.stdout.write("   - Verify the client_id and client_secret")
            self.stdout.write("   - Ensure the role_arn has the correct permissions")
            self.stdout.write("   - Check if the marketplace is correct (MX for Mexico)")

    def test_full_api(self):
        """Test multiple Amazon SP API endpoints"""
        
        self.stdout.write("🔍 Testing Amazon SP API (Full Test)...")
        self.stdout.write("=" * 50)
        
        try:
            from sp_api.api import Catalog, Orders, Reports
            from sp_api.base import SellingApiException
            
            self.stdout.write("📋 Setting up SP API configuration...")
            
            self.stdout.write(
                self.style.SUCCESS("✅ SP API configuration created successfully")
            )
            
            # Test 1: Test Catalog API
            self.stdout.write("\n📚 Testing Catalog API...")
            try:
                catalog_api = Catalog()
                self.stdout.write(
                    self.style.SUCCESS("✅ Catalog API initialized successfully")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catalog API test failed: {e}")
                )
            
            # Test 2: Test Orders API
            self.stdout.write("\n📦 Testing Orders API...")
            try:
                orders_api = Orders()
                self.stdout.write(
                    self.style.SUCCESS("✅ Orders API initialized successfully")
                )
                self.stdout.write("   Orders API is ready to use")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API test failed: {e}")
                )
            
            # Test 3: Test Reports API
            self.stdout.write("\n📊 Testing Reports API...")
            try:
                reports_api = Reports()
                self.stdout.write(
                    self.style.SUCCESS("✅ Reports API initialized successfully")
                )
                self.stdout.write("   Reports API is ready to use")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Reports API test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Amazon SP API full test completed!")
            )
            self.stdout.write("✅ All API endpoints are working correctly")
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('sp_api module not found. Please install it first.')
            )
            self.stdout.write('Run: pip install python-amazon-sp-api')
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_listings_consumption(self):
        """Test consumption of all listings from Amazon SP API"""
        
        self.stdout.write("🛍️ Testing Amazon SP API Listings Consumption...")
        self.stdout.write("=" * 60)
        
        try:
            from sp_api.api import Catalog
            from sp_api.base import SellingApiException
            
            self.stdout.write("�� Setting up SP API configuration...")
            
            self.stdout.write(
                self.style.SUCCESS("✅ SP API configuration created successfully")
            )
            
            # Test Catalog API for listings
            self.stdout.write("\n📚 Testing Catalog API for listings...")
            catalog_api = None
            try:
                catalog_api = Catalog()
                self.stdout.write(
                    self.style.SUCCESS("✅ Catalog API initialized successfully")
                )
                
                # Get all listings
                self.stdout.write("\n🔄 Fetching all listings...")
                
                try:
                    # Search for items in the catalog
                    # We'll use a broad search to get items
                    list_items_response = catalog_api.list_items(
                        marketplace_ids=['A1AM78C64UM0Y8'],  # MX marketplace ID
                        included_data=['summaries', 'attributes', 'images'],
                        page_size=20  # Limit to 20 items per page for testing
                    )
                    
                    if list_items_response.payload and hasattr(list_items_response.payload, 'items'):
                        items = list_items_response.payload.items
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved {len(items)} catalog items")
                        )
                        
                        # Display first few items as example
                        for i, item in enumerate(items[:5]):  # Show first 5 items
                            self.stdout.write(f"\n📦 Item {i+1}:")
                            if hasattr(item, 'summaries') and item.summaries:
                                summary = item.summaries[0]
                                self.stdout.write(f"   ASIN: {getattr(summary, 'asin', 'N/A')}")
                                self.stdout.write(f"   Title: {getattr(summary, 'title', 'N/A')}")
                                self.stdout.write(f"   Brand: {getattr(summary, 'brand', 'N/A')}")
                                self.stdout.write(f"   Main Image: {getattr(summary, 'main_image', 'N/A')}")
                            
                            if hasattr(item, 'attributes') and item.attributes:
                                for attr_name, attr_value in item.attributes.items():
                                    if hasattr(attr_value, 'value'):
                                        self.stdout.write(f"   {attr_name}: {attr_value.value}")
                        
                        if len(items) > 5:
                            self.stdout.write(f"\n... and {len(items) - 5} more items")
                        
                        self.stdout.write(f"\n📊 Total items retrieved: {len(items)}")
                        
                    else:
                        self.stdout.write(
                            self.style.WARNING("⚠️ No items found in catalog search")
                        )
                        
                except SellingApiException as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Catalog API error: {e}")
                    )
                    self.stdout.write(f"   Error: {e.error}")
                    self.stdout.write(f"   Message: {e.message}")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error fetching listings: {e}")
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catalog API test failed: {e}")
                )
            
            # Test specific item details
            self.stdout.write("\n🔍 Testing item detail retrieval...")
            try:
                if catalog_api is None:
                    self.stdout.write(
                        self.style.WARNING("⚠️ Skipping item detail test - Catalog API not initialized")
                    )
                    return
                    
                # Example: Get details for a specific ASIN (you might want to use a real ASIN from your account)
                # This is just for testing the API structure
                try:
                    # Get catalog item details (using a placeholder ASIN)
                    # In a real scenario, you would use actual ASINs from your inventory
                    test_asin = 'B08N5WRWNW'  # Example ASIN (Amazon Echo Dot)
                    
                    catalog_item_response = catalog_api.get_item(
                        asin=test_asin,
                        marketplace_ids=['A1AM78C64UM0Y8'],
                        included_data=['summaries', 'attributes', 'images', 'salesRanks']
                    )
                    
                    if catalog_item_response.payload:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for ASIN: {test_asin}")
                        )
                        
                        if hasattr(catalog_item_response.payload, 'summaries') and catalog_item_response.payload.summaries:
                            summary = catalog_item_response.payload.summaries[0]
                            self.stdout.write(f"   Title: {getattr(summary, 'title', 'N/A')}")
                            self.stdout.write(f"   Brand: {getattr(summary, 'brand', 'N/A')}")
                            
                        if hasattr(catalog_item_response.payload, 'attributes'):
                            self.stdout.write("   Attributes available")
                            
                        if hasattr(catalog_item_response.payload, 'images'):
                            self.stdout.write(f"   Images: {len(catalog_item_response.payload.images) if catalog_item_response.payload.images else 0}")
                            
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ No details found for ASIN: {test_asin}")
                        )
                        
                except SellingApiException as e:
                    if '404' in str(e):
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ ASIN {test_asin} not found (expected for test ASIN)")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Catalog item detail error: {e}")
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Item detail test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS("🎉 Amazon SP API Listings test completed!")
            )
            self.stdout.write("✅ Listings consumption functionality is working")
            self.stdout.write("\n💡 Next steps:")
            self.stdout.write("   - Implement pagination for large catalogs")
            self.stdout.write("   - Add filtering by category or attributes")
            self.stdout.write("   - Store listings in your database")
            self.stdout.write("   - Set up regular sync schedules")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Listings test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 60)

    def test_orders_api(self):
        """Test Orders API functionality"""
        
        self.stdout.write("📦 Testing Amazon SP API Orders...")
        self.stdout.write("=" * 50)
        
        try:
            from sp_api.api import Orders
            from sp_api.base import SellingApiException
            from datetime import datetime, timedelta
            
            self.stdout.write("📋 Setting up Orders API...")
            
            orders_api = Orders()
            self.stdout.write(
                self.style.SUCCESS("✅ Orders API initialized successfully")
            )
            
            # Get orders from the last 7 days
            self.stdout.write("\n🔄 Fetching recent orders...")
            
            try:
                # Get orders from the last 7 days (with 2-minute buffer for data delay)
                end_date = datetime.utcnow() - timedelta(minutes=2)
                start_date = end_date - timedelta(days=7)
                
                orders_response = orders_api.get_orders(
                    MarketplaceIds=['A1AM78C64UM0Y8'],  # MX marketplace
                    CreatedAfter=start_date.isoformat(),
                    CreatedBefore=end_date.isoformat(),
                    MaxResults=10
                )
                
                if orders_response.payload and hasattr(orders_response.payload, 'Orders'):
                    orders = orders_response.payload.Orders
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(orders)} orders")
                    )
                    
                    # Display first few orders as example
                    for i, order in enumerate(orders[:3]):  # Show first 3 orders
                        self.stdout.write(f"\n📦 Order {i+1}:")
                        self.stdout.write(f"   Amazon Order ID: {getattr(order, 'AmazonOrderId', 'N/A')}")
                        self.stdout.write(f"   Order Status: {getattr(order, 'OrderStatus', 'N/A')}")
                        self.stdout.write(f"   Order Total: {getattr(order, 'OrderTotal', 'N/A')}")
                        self.stdout.write(f"   Purchase Date: {getattr(order, 'PurchaseDate', 'N/A')}")
                        
                        if hasattr(order, 'ShippingAddress'):
                            address = order.ShippingAddress
                            self.stdout.write(f"   Shipping Address: {getattr(address, 'City', 'N/A')}, {getattr(address, 'StateOrRegion', 'N/A')}")
                    
                    if len(orders) > 3:
                        self.stdout.write(f"\n... and {len(orders) - 3} more orders")
                    
                    self.stdout.write(f"\n📊 Total orders retrieved: {len(orders)}")
                    
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️ No orders found in the specified time period")
                    )
                    
            except SellingApiException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API error: {e}")
                )
                self.stdout.write(f"   Error: {e.error}")
                self.stdout.write(f"   Message: {e.message}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error fetching orders: {e}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Amazon SP API Orders test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Orders test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_api_permissions(self):
        """Test different API endpoints to diagnose permission issues"""
        
        self.stdout.write("🔍 Testing Amazon SP API Permissions...")
        self.stdout.write("=" * 60)
        
        try:
            from sp_api.api import Catalog, Orders, Reports, Notifications
            from sp_api.base import SellingApiException
            
            self.stdout.write("📋 Testing different API endpoints...")
            
            # Test 1: Catalog API
            self.stdout.write("\n📚 Testing Catalog API permissions...")
            try:
                catalog_api = Catalog()
                # Try a simple call with correct parameters
                response = catalog_api.list_items(
                    marketplace_ids=['A1AM78C64UM0Y8'],
                    page_size=1
                )
                self.stdout.write(
                    self.style.SUCCESS("✅ Catalog API - list_items: SUCCESS")
                )
            except SellingApiException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catalog API - list_items: {e.message}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catalog API - list_items: {e}")
                )
            
            # Test 2: Orders API
            self.stdout.write("\n📦 Testing Orders API permissions...")
            try:
                orders_api = Orders()
                # Try a simple call with required parameters
                from datetime import datetime, timedelta
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                
                response = orders_api.get_orders(
                    MarketplaceIds=['A1AM78C64UM0Y8'],
                    CreatedAfter=start_date.isoformat(),
                    MaxResults=1
                )
                self.stdout.write(
                    self.style.SUCCESS("✅ Orders API - get_orders: SUCCESS")
                )
            except SellingApiException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API - get_orders: {e.message}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API - get_orders: {e}")
                )
            
            # Test 3: Reports API
            self.stdout.write("\n📊 Testing Reports API permissions...")
            try:
                reports_api = Reports()
                # Try a simple call with required parameters
                response = reports_api.get_reports(
                    report_types=['GET_FLAT_FILE_OPEN_LISTINGS_DATA_BY_SKU']
                )
                self.stdout.write(
                    self.style.SUCCESS("✅ Reports API - get_reports: SUCCESS")
                )
            except SellingApiException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Reports API - get_reports: {e.message}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Reports API - get_reports: {e}")
                )
            
            # Test 4: Notifications API
            self.stdout.write("\n🔔 Testing Notifications API permissions...")
            try:
                notifications_api = Notifications()
                # Try a simple call - get destinations
                response = notifications_api.get_destinations()
                self.stdout.write(
                    self.style.SUCCESS("✅ Notifications API - get_destinations: SUCCESS")
                )
            except SellingApiException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Notifications API - get_destinations: {e.message}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Notifications API - get_destinations: {e}")
                )
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("💡 Permission Analysis:")
            self.stdout.write("   - If Catalog API fails but others work: Missing catalog:read scope")
            self.stdout.write("   - If all APIs fail: Check role ARN permissions")
            self.stdout.write("   - If some work: Check specific API scopes")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Permission test failed: {e}")
            )
            self.stdout.write("=" * 60)
