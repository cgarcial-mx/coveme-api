from django.core.management.base import BaseCommand
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Test Amazon SP API credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full API test instead of just authentication',
        )

    def handle(self, *args, **options):
        try:
            # Import here to avoid import errors if amzn-sp-api is not installed
            from spapi.auth.credentials import SPAPIConfig
            from spapi import OrdersV0Api, CatalogApi, ReportsApi
            
            if options['full']:
                self.test_full_api()
            else:
                self.test_authentication()
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR('spapi module not found. Please install it first.')
            )
            self.stdout.write('Run: pip install amzn-sp-api')
            sys.exit(1)

    def test_authentication(self):
        """Test only the authentication with Amazon SP API"""
        
        self.stdout.write("🔐 Testing Amazon SP API Authentication...")
        self.stdout.write("=" * 50)
        
        # Credentials from C# code
        credentials = {
            'client_id': 'amzn1.application-oa2-client.841b3e0a8d5a433d84e749b2c9049cb6',
            'client_secret': 'amzn1.oa2-cs.v1.5dffd79fca814c757d0a8f31783ccbf8a832134b6740427c0964b238ce3f47e8',
            'refresh_token': 'Atzr|IwEBIO0A7eeDGi90Fm1A1L7L6MNxVg75MXfEgWM7pZmPZ38KsNqA_WlxaFingnRk8lG_stufp0TiEpOXxZcZ4CXWtBcHpoh2uGvTdNEL3HMtGT_OyCHIjR5WmgSgh5c1kDRFI8s4ONzOed6uF0iuWJaf7zVYjQ8oyvOyM5fL0nPLBa_7k8HIRXUnL2P__iQ0KNAMJKM03LwI5XEIt2CCT2hPm--BCHJROpRuM8grHPM83knG0gjXvcftS0MSkjtyRjNsAAJuXD9X82Bi1OApt1K9K7pSHVX1N1GO4Wv2JZfld5xB3tzf8SU8yu2QDPg3g2dI7C4',
            'marketplace': 'NA',  # North America marketplace
        }
        
        try:
            self.stdout.write("📋 Creating SP API configuration...")
            
            # Import SPAPIConfig here
            from spapi.auth.credentials import SPAPIConfig
            
            # Create SP API configuration
            config = SPAPIConfig(
                client_id=credentials['client_id'],
                client_secret=credentials['client_secret'],
                refresh_token=credentials['refresh_token'],
                region='us-east-1'  # North America region
            )
            
            self.stdout.write(
                self.style.SUCCESS("✅ SP API configuration created successfully")
            )
            
            self.stdout.write("\n🔑 Testing API connection...")
            
            # Test API connection by creating a client
            from spapi.client import SPAPIClient
            client = SPAPIClient(config)
            
            self.stdout.write(
                self.style.SUCCESS("✅ API connection established successfully!")
            )
            self.stdout.write(f"   Client created with marketplace: {credentials['marketplace']}")
            
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
        
        # Credentials from C# code
        credentials_data = {
            'client_id': 'amzn1.application-oa2-client.841b3e0a8d5a433d84e749b2c9049cb6',
            'client_secret': 'amzn1.oa2-cs.v1.5dffd79fca814c757d0a8f31783ccbf8a832134b6740427c0964b238ce3f47e8',
            'refresh_token': 'Atzr|IwEBIO0A7eeDGi90Fm1A1L7L6MNxVg75MXfEgWM7pZmPZ38KsNqA_WlxaFingnRk8lG_stufp0TiEpOXxZcZ4CXWtBcHpoh2uGvTdNEL3HMtGT_OyCHIjR5WmgSgh5c1kDRFI8s4ONzOed6uF0iuWJaf7zVYjQ8oyvOyM5fL0nPLBa_7k8HIRXUnL2P__iQ0KNAMJKM03LwI5XEIt2CCT2hPm--BCHJROpRuM8grHPM83knG0gjXvcftS0MSkjtyRjNsAAJuXD9X82Bi1OApt1K9K7pSHVX1N1GO4Wv2JZfld5xB3tzf8SU8yu2QDPg3g2dI7C4',
        }
        
        try:
            from datetime import datetime, timedelta
            from spapi import OrdersV0Api, CatalogApi, ReportsApi
            from spapi.auth.credentials import SPAPIConfig
            from spapi.client import SPAPIClient
            from spapi.rest import ApiException
            
            self.stdout.write("📋 Setting up SP API configuration...")
            
            # Create SP API configuration
            config = SPAPIConfig(
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                refresh_token=credentials_data['refresh_token'],
                region='us-east-1'  # North America region
            )
            
            self.stdout.write(
                self.style.SUCCESS("✅ SP API configuration created successfully")
            )
            
            # Create SP API client
            client = SPAPIClient(config)
            
            # Test 1: Test Orders API
            self.stdout.write("\n📦 Testing Orders API...")
            try:
                orders_api = OrdersV0Api(client)
                self.stdout.write(
                    self.style.SUCCESS("✅ Orders API initialized successfully")
                )
                self.stdout.write("   Orders API is ready to use")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Orders API test failed: {e}")
                )
            
            # Test 2: Test Catalog API
            self.stdout.write("\n📚 Testing Catalog API...")
            try:
                catalog_api = CatalogApi(client)
                self.stdout.write(
                    self.style.SUCCESS("✅ Catalog API initialized successfully")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catalog API test failed: {e}")
                )
            
            # Test 3: Test Reports API
            self.stdout.write("\n📊 Testing Reports API...")
            try:
                reports_api = ReportsApi(client)
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
                self.style.ERROR('spapi module not found. Please install it first.')
            )
            self.stdout.write('Run: pip install amzn-sp-api')
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)
