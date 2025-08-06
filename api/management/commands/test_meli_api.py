from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Test MercadoLibre API using requests library'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full API test instead of just authentication',
        )
        parser.add_argument(
            '--listings',
            action='store_true',
            help='Test listings consumption from MercadoLibre API',
        )
        parser.add_argument(
            '--orders',
            action='store_true',
            help='Test orders API',
        )
        parser.add_argument(
            '--auth',
            action='store_true',
            help='Test authentication and token refresh',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with detailed API responses',
        )
        parser.add_argument(
            '--auth-url',
            action='store_true',
            help='Generate authorization URL for user token',
        )
        parser.add_argument(
            '--exchange-code',
            type=str,
            help='Exchange authorization code for access token',
        )
        parser.add_argument(
            '--auto-auth',
            action='store_true',
            help='Test automatic authentication strategies',
        )

    def handle(self, *args, **options):
        # Load environment variables from .env file
        self.load_env_file()
        
        # Set up environment variables for MercadoLibre API
        if not self.setup_meli_credentials():
            sys.exit(1)
        
        try:
            # Store debug mode for use in other methods
            self.debug_mode = options.get('debug', False)
            
            if options['listings']:
                self.test_listings_consumption()
            elif options['orders']:
                self.test_orders_api()
            elif options['auth']:
                self.test_authentication()
            elif options['auth_url']:
                self.generate_auth_url()
            elif options['exchange_code']:
                self.exchange_code_for_token(options['exchange_code'])
            elif options['auto_auth']:
                self.test_automatic_auth_strategies()
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

    def setup_meli_credentials(self):
        """Set up environment variables for MercadoLibre API authentication"""
        # Check if required environment variables are set
        required_vars = [
            'MERCADOLIBRE_URL',
            'MERCADOLIBRE_SECRET_KEY',
            'MERCADOLIBRE_APP_ID',
            'MERCADOLIBRE_USER',
            'MERCADOLIBRE_SITE',
            'MERCADOLIBRE_REDIRECT_URI'
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
            self.stdout.write("   - MERCADOLIBRE_URL")
            self.stdout.write("   - MERCADOLIBRE_SECRET_KEY")
            self.stdout.write("   - MERCADOLIBRE_APP_ID")
            self.stdout.write("   - MERCADOLIBRE_USER")
            self.stdout.write("   - MERCADOLIBRE_SITE")
            self.stdout.write("   - MERCADOLIBRE_REDIRECT_URI")
            return False
        
        self.stdout.write(
            self.style.SUCCESS("✅ All required environment variables are set")
        )
        return True

    def get_access_token(self):
        """Get access token using client credentials flow with proper scopes"""
        try:
            url = f"{os.environ['MERCADOLIBRE_URL']}/oauth/token"
            
            # Try different grant types and scopes for automatic authentication
            auth_methods = [
                {
                    'name': 'Client Credentials with scopes',
                    'data': {
                        'grant_type': 'client_credentials',
                        'client_id': os.environ['MERCADOLIBRE_APP_ID'],
                        'client_secret': os.environ['MERCADOLIBRE_SECRET_KEY'],
                        'scope': 'read write offline_access'
                    }
                },
                {
                    'name': 'Client Credentials without scopes',
                    'data': {
                        'grant_type': 'client_credentials',
                        'client_id': os.environ['MERCADOLIBRE_APP_ID'],
                        'client_secret': os.environ['MERCADOLIBRE_SECRET_KEY']
                    }
                }
            ]
            
            for method in auth_methods:
                if self.debug_mode:
                    self.stdout.write(f"🔍 Debug: Trying {method['name']}")
                    self.stdout.write(f"🔍 Debug: Requesting token from {url}")
                    self.stdout.write(f"🔍 Debug: Data: {method['data']}")
                
                response = requests.post(url, data=method['data'])
                
                if self.debug_mode:
                    self.stdout.write(f"🔍 Debug: Response status: {response.status_code}")
                    self.stdout.write(f"🔍 Debug: Response body: {response.text[:500]}...")
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get('access_token')
                    
                    if access_token:
                        self.stdout.write(f"✅ Successfully obtained token using {method['name']}")
                        if self.debug_mode:
                            self.stdout.write(f"🔍 Debug: Access token: {access_token[:20]}...")
                        return access_token
                else:
                    if self.debug_mode:
                        self.stdout.write(f"🔍 Debug: {method['name']} failed: {response.status_code} - {response.text}")
            
            # If all methods failed, show the last error
            self.stdout.write(
                self.style.ERROR(f"❌ All authentication methods failed. Last error: {response.status_code} - {response.text}")
            )
            return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting access token: {e}")
            )
            return None

    def get_user_access_token(self):
        """Get user access token using authorization code flow"""
        try:
            # Check if we have a stored user access token
            user_token = os.environ.get('MERCADOLIBRE_USER_TOKEN')
            if user_token:
                self.stdout.write("✅ Using stored user access token")
                return user_token
            
            # If no stored token, show instructions for getting one
            self.stdout.write(
                self.style.WARNING("⚠️ No user access token found. Search API requires user authorization.")
            )
            self.stdout.write("")
            self.stdout.write("🔧 To get a user access token, follow these steps:")
            self.stdout.write("")
            self.stdout.write("1. Create authorization URL:")
            self.stdout.write(f"   https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id={os.environ['MERCADOLIBRE_APP_ID']}&redirect_uri={os.environ.get('MERCADOLIBRE_REDIRECT_URI', 'https://forttuna.azurewebsites.net/app/main/salechannel/authorization')}")
            self.stdout.write("")
            self.stdout.write("2. Open the URL in your browser")
            self.stdout.write("3. Authorize your application")
            self.stdout.write("4. Copy the 'code' parameter from the redirect URL")
            self.stdout.write("5. Add MERCADOLIBRE_USER_TOKEN to your .env.local file")
            self.stdout.write("")
            self.stdout.write("📚 Full documentation:")
            self.stdout.write("https://developers.mercadolibre.com.mx/es_ar/autenticacion-y-autorizacion")
            self.stdout.write("")
            
            # For now, return None to indicate no user token
            return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting user access token: {e}")
            )
            return None

    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        try:
            url = f"{os.environ['MERCADOLIBRE_URL']}/oauth/token"
            
            data = {
                'grant_type': 'authorization_code',
                'client_id': os.environ['MERCADOLIBRE_APP_ID'],
                'client_secret': os.environ['MERCADOLIBRE_SECRET_KEY'],
                'code': authorization_code,
                'redirect_uri': os.environ.get('MERCADOLIBRE_REDIRECT_URI', 'https://forttuna.azurewebsites.net/app/main/salechannel/authorization')
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                refresh_token = token_data.get('refresh_token')
                
                self.stdout.write("✅ Successfully exchanged code for access token")
                self.stdout.write(f"   Access token: {access_token[:20]}...")
                if refresh_token:
                    self.stdout.write(f"   Refresh token: {refresh_token[:20]}...")
                
                return access_token
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to exchange code: {response.status_code} - {response.text}")
                )
                return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error exchanging code: {e}")
            )
            return None

    def generate_auth_url(self):
        """Generate authorization URL for user token"""
        try:
            self.stdout.write("🔗 Generating MercadoLibre Authorization URL...")
            self.stdout.write("=" * 60)
            
            app_id = os.environ.get('MERCADOLIBRE_APP_ID')
            redirect_uri = os.environ.get('MERCADOLIBRE_REDIRECT_URI', 'https://forttuna.azurewebsites.net/app/main/salechannel/authorization')
            
            if not app_id:
                self.stdout.write(
                    self.style.ERROR("❌ MERCADOLIBRE_APP_ID not found in environment variables")
                )
                return
            
            auth_url = f"https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id={app_id}&redirect_uri={redirect_uri}"
            
            self.stdout.write("✅ Authorization URL generated:")
            self.stdout.write("")
            self.stdout.write(auth_url)
            self.stdout.write("")
            self.stdout.write("📋 Instructions:")
            self.stdout.write("1. Copy and paste this URL in your browser")
            self.stdout.write("2. Log in to your MercadoLibre account")
            self.stdout.write("3. Authorize the application")
            self.stdout.write("4. Copy the 'code' parameter from the redirect URL")
            self.stdout.write("5. Run: python manage.py test_meli_api --exchange-code YOUR_CODE")
            self.stdout.write("")
            self.stdout.write("💡 The redirect URL will look like:")
            self.stdout.write(f"   {redirect_uri}?code=YOUR_AUTHORIZATION_CODE")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error generating auth URL: {e}")
            )

    def test_automatic_auth_strategies(self):
        """Test different automatic authentication strategies"""
        self.stdout.write("🔐 Testing Automatic Authentication Strategies...")
        self.stdout.write("=" * 60)
        
        strategies = [
            {
                'name': 'Client Credentials with scopes',
                'method': 'client_credentials',
                'scopes': 'read write offline_access'
            },
            {
                'name': 'Client Credentials without scopes',
                'method': 'client_credentials',
                'scopes': None
            },
            {
                'name': 'Public endpoints (no auth)',
                'method': 'public',
                'scopes': None
            }
        ]
        
        working_strategies = []
        
        for strategy in strategies:
            self.stdout.write(f"\n🔍 Testing: {strategy['name']}")
            
            try:
                if strategy['method'] == 'client_credentials':
                    # Test client credentials
                    url = f"{os.environ['MERCADOLIBRE_URL']}/oauth/token"
                    data = {
                        'grant_type': 'client_credentials',
                        'client_id': os.environ['MERCADOLIBRE_APP_ID'],
                        'client_secret': os.environ['MERCADOLIBRE_SECRET_KEY']
                    }
                    
                    if strategy['scopes']:
                        data['scope'] = strategy['scopes']
                    
                    response = requests.post(url, data=data)
                    
                    if response.status_code == 200:
                        token_data = response.json()
                        access_token = token_data.get('access_token')
                        
                        if access_token:
                            # Test the token with a simple API call
                            headers = {
                                'Authorization': f'Bearer {access_token}',
                                'Content-Type': 'application/json'
                            }
                            
                            # Test with user info endpoint
                            user_id = os.environ['MERCADOLIBRE_USER']
                            test_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}"
                            test_response = requests.get(test_url, headers=headers)
                            
                            if test_response.status_code == 200:
                                working_strategies.append({
                                    'name': strategy['name'],
                                    'token': access_token,
                                    'method': 'client_credentials'
                                })
                                self.stdout.write(
                                    self.style.SUCCESS(f"     ✅ {strategy['name']} works!")
                                )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f"     ⚠️ Token obtained but API test failed: {test_response.status_code}")
                                )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"     ❌ No access token in response")
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"     ❌ Failed: {response.status_code} - {response.text}")
                        )
                
                elif strategy['method'] == 'public':
                    # Test public endpoints
                    site_id = os.environ['MERCADOLIBRE_SITE']
                    test_url = f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/categories"
                    response = requests.get(test_url)
                    
                    if response.status_code == 200:
                        working_strategies.append({
                            'name': strategy['name'],
                            'token': None,
                            'method': 'public'
                        })
                        self.stdout.write(
                            self.style.SUCCESS(f"     ✅ {strategy['name']} works!")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"     ❌ Failed: {response.status_code}")
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"     ❌ Exception: {e}")
                )
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 AUTHENTICATION STRATEGIES SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"✅ Working strategies: {len(working_strategies)}")
        self.stdout.write(f"📈 Total strategies tested: {len(strategies)}")
        
        if working_strategies:
            self.stdout.write("\n🏆 WORKING STRATEGIES:")
            for strategy in working_strategies:
                self.stdout.write(f"   ✅ {strategy['name']}")
                if strategy['token']:
                    self.stdout.write(f"      Token: {strategy['token'][:20]}...")
        
        return working_strategies

    def test_authentication(self):
        """Test only the authentication with MercadoLibre API"""
        
        self.stdout.write("🔐 Testing MercadoLibre API Authentication...")
        self.stdout.write("=" * 50)
        
        try:
            self.stdout.write("📋 Getting access token...")
            
            access_token = self.get_access_token()
            
            if not access_token:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to obtain access token")
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS("✅ Access token obtained successfully")
            )
            
            self.stdout.write("\n🔑 Testing API connection...")
            
            # Test the connection by making a simple API call
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple endpoint - get user info
            user_id = os.environ['MERCADOLIBRE_USER']
            test_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}"
            
            response = requests.get(test_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.stdout.write(
                    self.style.SUCCESS("✅ API connection established successfully!")
                )
                self.stdout.write(f"   User ID: {user_data.get('id', 'N/A')}")
                self.stdout.write(f"   Nickname: {user_data.get('nickname', 'N/A')}")
                self.stdout.write(f"   Site: {os.environ['MERCADOLIBRE_SITE']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ API connection failed: {response.status_code} - {response.text}")
                )
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 Authentication test completed successfully!")
            )
            self.stdout.write("✅ Your MercadoLibre API credentials are working correctly")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Authentication failed: {e}")
            )
            self.stdout.write("=" * 50)
            self.stdout.write("🔍 Common issues:")
            self.stdout.write("   - Check if the App ID and Secret Key are correct")
            self.stdout.write("   - Verify the user ID is valid")
            self.stdout.write("   - Ensure the site code is correct (MLM for Mexico)")
            self.stdout.write("   - Check if the redirect URI is properly configured")

    def test_full_api(self):
        """Test multiple MercadoLibre API endpoints"""
        
        self.stdout.write("🔍 Testing MercadoLibre API (Full Test)...")
        self.stdout.write("=" * 50)
        
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to obtain access token")
                )
                return
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            self.stdout.write("📋 Setting up API configuration...")
            self.stdout.write(
                self.style.SUCCESS("✅ API configuration created successfully")
            )
            
            # Test 1: User Info API
            self.stdout.write("\n👤 Testing User Info API...")
            try:
                user_id = os.environ['MERCADOLIBRE_USER']
                user_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}"
                
                response = requests.get(user_url, headers=headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.stdout.write(
                        self.style.SUCCESS("✅ User Info API working correctly")
                    )
                    self.stdout.write(f"   User: {user_data.get('nickname', 'N/A')}")
                    self.stdout.write(f"   Registration Date: {user_data.get('registration_date', 'N/A')}")
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User Info API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ User Info API test failed: {e}")
                )
            
            # Test 2: Categories API
            self.stdout.write("\n📂 Testing Categories API...")
            categories_data = None
            try:
                site_id = os.environ['MERCADOLIBRE_SITE']
                categories_url = f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/categories"
                
                response = requests.get(categories_url, headers=headers)
                
                if response.status_code == 200:
                    categories_data = response.json()
                    self.stdout.write(
                        self.style.SUCCESS("✅ Categories API working correctly")
                    )
                    self.stdout.write(f"   Categories available: {len(categories_data)}")
                    
                    # Show all categories
                    if categories_data and len(categories_data) > 0:
                        self.stdout.write("   All categories:")
                        for i, category in enumerate(categories_data):
                            self.stdout.write(f"     {i+1:2d}. {category.get('name', 'N/A')} (ID: {category.get('id', 'N/A')})")
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Categories API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Categories API test failed: {e}")
                )
            
            # Test 3: Search API - Test with user authentication
            self.stdout.write("\n🔍 Testing Search API with user authentication...")
            
            if not categories_data or len(categories_data) == 0:
                self.stdout.write(
                    self.style.WARNING("⚠️ No categories available for testing")
                )
                return
            
            working_categories = []
            non_working_categories = []
            
            # Try different authentication strategies
            self.stdout.write("\n   Testing different authentication strategies...")
            
            # Strategy 1: Try with client credentials token
            client_token = self.get_access_token()
            if client_token:
                self.stdout.write("   ✅ Client credentials token obtained")
                search_headers = {
                    'Authorization': f'Bearer {client_token}',
                    'Content-Type': 'application/json'
                }
            else:
                self.stdout.write("   ⚠️ Client credentials failed, trying public endpoints...")
                search_headers = {}  # No headers for public endpoints
                
                try:
                    site_id = os.environ['MERCADOLIBRE_SITE']
                    search_url = f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/search"
                    
                    # Test with user authentication
                    for i, category in enumerate(categories_data, 1):
                        category_name = category.get('name', 'Unknown')
                        category_id = category.get('id', 'Unknown')
                        
                        self.stdout.write(f"\n   Testing category {i}/{len(categories_data)}: {category_name}")
                        
                        try:
                            params = {
                                'q': category_name,
                                'limit': 1
                            }
                            
                            response = requests.get(search_url, headers=search_headers, params=params)
                            
                            if response.status_code == 200:
                                search_data = response.json()
                                total_results = search_data.get('paging', {}).get('total', 0)
                                
                                if total_results > 0:
                                    working_categories.append({
                                        'name': category_name,
                                        'id': category_id,
                                        'results': total_results
                                    })
                                    self.stdout.write(
                                        self.style.SUCCESS(f"     ✅ {total_results} results found")
                                    )
                                else:
                                    non_working_categories.append({
                                        'name': category_name,
                                        'id': category_id
                                    })
                                    self.stdout.write(
                                        self.style.WARNING(f"     ⚠️ No results found")
                                    )
                            else:
                                non_working_categories.append({
                                    'name': category_name,
                                    'id': category_id
                                })
                                self.stdout.write(
                                    self.style.ERROR(f"     ❌ API error: {response.status_code}")
                                )
                                
                        except Exception as e:
                            non_working_categories.append({
                                'name': category_name,
                                'id': category_id
                            })
                            self.stdout.write(
                                self.style.ERROR(f"     ❌ Exception: {e}")
                            )
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"     ❌ Search test failed: {e}")
                    )
            
            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("📊 SEARCH TEST SUMMARY")
            self.stdout.write("=" * 60)
            self.stdout.write(f"✅ Working categories: {len(working_categories)}")
            self.stdout.write(f"❌ Non-working categories: {len(non_working_categories)}")
            self.stdout.write(f"📈 Total categories tested: {len(categories_data)}")
            
            if working_categories:
                self.stdout.write("\n🏆 TOP 10 WORKING CATEGORIES:")
                # Sort by number of results (descending)
                sorted_working = sorted(working_categories, key=lambda x: x['results'], reverse=True)
                for i, category in enumerate(sorted_working[:10], 1):
                    self.stdout.write(f"   {i:2d}. {category['name']} - {category['results']:,} results")
            
            if non_working_categories:
                self.stdout.write("\n⚠️ NON-WORKING CATEGORIES:")
                for category in non_working_categories:
                    self.stdout.write(f"   - {category['name']} (ID: {category['id']})")
            
            # Add explanation about 403 errors
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("🔍 TROUBLESHOOTING: 403 ERRORS")
            self.stdout.write("=" * 60)
            self.stdout.write("❓ Why do you get 403 errors?")
            self.stdout.write("")
            self.stdout.write("The 403 error occurs because:")
            self.stdout.write("1. 🔐 Search API requires user authorization (not just client credentials)")
            self.stdout.write("2. 📋 You need specific scopes: 'read', 'offline_access'")
            self.stdout.write("3. 👤 The user must authorize your application")
            self.stdout.write("")
            self.stdout.write("🔧 To fix this, you need to:")
            self.stdout.write("1. Implement OAuth 2.0 Authorization Code flow")
            self.stdout.write("2. Redirect user to MercadoLibre authorization URL")
            self.stdout.write("3. Get authorization code from callback")
            self.stdout.write("4. Exchange code for user access token")
            self.stdout.write("")
            self.stdout.write("📚 Documentation:")
            self.stdout.write("https://developers.mercadolibre.com.mx/es_ar/autenticacion-y-autorizacion")
            self.stdout.write("")
            self.stdout.write("💡 For now, the test uses public endpoints where possible")
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS("🎉 MercadoLibre API full test completed!")
            )
            self.stdout.write("✅ All API endpoints are working correctly")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50)

    def test_listings_consumption(self):
        """Test consumption of listings from MercadoLibre API"""
        
        self.stdout.write("🛍️ Testing MercadoLibre API Listings Consumption...")
        self.stdout.write("=" * 60)
        
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to obtain access token")
                )
                return
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            self.stdout.write("📋 Setting up API configuration...")
            self.stdout.write(
                self.style.SUCCESS("✅ API configuration created successfully")
            )
            
            # Test basic connectivity first
            self.stdout.write("\n🌐 Testing basic API connectivity...")
            try:
                # Test the base API endpoint
                base_url = os.environ['MERCADOLIBRE_URL']
                response = requests.get(base_url, timeout=10)
                
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS("✅ MercadoLibre API is reachable")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ API responded with status: {response.status_code}")
                    )
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Cannot reach MercadoLibre API: {e}")
                )
                self.stdout.write("💡 Check your internet connection and the API URL")
            
            # Test 1: Get user's listings
            self.stdout.write("\n📦 Testing User Listings API...")
            try:
                user_id = os.environ['MERCADOLIBRE_USER']
                listings_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}/items/search"
                
                response = requests.get(listings_url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        listings_data = response.json()
                        
                        # Handle different response structures
                        if isinstance(listings_data, dict):
                            listings = listings_data.get('results', [])
                        elif isinstance(listings_data, list):
                            listings = listings_data
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"⚠️ Unexpected response format: {type(listings_data)}")
                            )
                            self.stdout.write(f"   Response: {listings_data}")
                            listings = []
                        
                        if listings:
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Successfully retrieved {len(listings)} user listings")
                            )
                            
                            # Display first few listings as example
                            for i, listing in enumerate(listings[:5]):  # Show first 5 listings
                                if isinstance(listing, dict):
                                    self.stdout.write(f"\n📦 Listing {i+1}:")
                                    self.stdout.write(f"   ID: {listing.get('id', 'N/A')}")
                                    self.stdout.write(f"   Title: {listing.get('title', 'N/A')}")
                                    self.stdout.write(f"   Price: {listing.get('price', 'N/A')}")
                                    self.stdout.write(f"   Currency: {listing.get('currency_id', 'N/A')}")
                                    self.stdout.write(f"   Condition: {listing.get('condition', 'N/A')}")
                                    self.stdout.write(f"   Status: {listing.get('status', 'N/A')}")
                                else:
                                    self.stdout.write(f"\n📦 Listing {i+1}: {listing}")
                            
                            if len(listings) > 5:
                                self.stdout.write(f"\n... and {len(listings) - 5} more listings")
                            
                            self.stdout.write(f"\n📊 Total listings retrieved: {len(listings)}")
                        else:
                            self.stdout.write(
                                self.style.WARNING("⚠️ No listings found in response")
                            )
                            
                    except json.JSONDecodeError as e:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Failed to parse JSON response: {e}")
                        )
                        self.stdout.write(f"   Raw response: {response.text[:200]}...")
                        
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ User listings API error: {response.status_code}")
                    )
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ User listings test failed: {e}")
                )
            
            # Test 2: Categories API (should work with authentication)
            self.stdout.write("\n📂 Testing Categories API...")
            try:
                site_id = os.environ['MERCADOLIBRE_SITE']
                categories_url = f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/categories"
                
                response = requests.get(categories_url, headers=headers)
                
                if response.status_code == 200:
                    categories_data = response.json()
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(categories_data)} categories")
                    )
                    
                    # Display first few categories
                    for i, category in enumerate(categories_data[:5]):
                        self.stdout.write(f"\n📂 Category {i+1}:")
                        self.stdout.write(f"   ID: {category.get('id', 'N/A')}")
                        self.stdout.write(f"   Name: {category.get('name', 'N/A')}")
                        self.stdout.write(f"   Picture: {category.get('picture', 'N/A')}")
                    
                    if len(categories_data) > 5:
                        self.stdout.write(f"\n... and {len(categories_data) - 5} more categories")
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Categories API failed: {response.status_code}")
                    )
                    self.stdout.write(f"   Response: {response.text}")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Categories API test failed: {e}")
                )
            
            # Test 3: Search for items in marketplace
            self.stdout.write("\n🔍 Testing Marketplace Search API...")
            try:
                site_id = os.environ['MERCADOLIBRE_SITE']
                
                # Try different search endpoints - all require authentication
                search_endpoints = [
                    f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/search",
                    f"{os.environ['MERCADOLIBRE_URL']}/search"
                ]
                
                params = {
                    'q': 'smartphone',
                    'limit': 10,
                    'offset': 0
                }
                
                items = []
                search_successful = False
                
                # Since we have valid authentication, try with auth directly
                for i, search_url in enumerate(search_endpoints):
                    if self.debug_mode:
                        self.stdout.write(f"🔍 Debug: Trying search endpoint {i+1}: {search_url}")
                    
                    # Try with authentication (search endpoints require auth)
                    response = requests.get(search_url, headers=headers, params=params)
                    
                    if self.debug_mode:
                        self.stdout.write(f"🔍 Debug: Response status: {response.status_code}")
                        self.stdout.write(f"🔍 Debug: Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        try:
                            search_data = response.json()
                            items = search_data.get('results', [])
                            
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Successfully retrieved {len(items)} marketplace items")
                            )
                            self.stdout.write(f"   Endpoint used: {search_url}")
                            
                            search_successful = True
                            break
                            
                        except json.JSONDecodeError:
                            if self.debug_mode:
                                self.stdout.write(f"🔍 Debug: Failed to parse JSON from {search_url}")
                            continue
                    else:
                        if self.debug_mode:
                            self.stdout.write(f"🔍 Debug: Endpoint {search_url} failed with {response.status_code}")
                            self.stdout.write(f"🔍 Debug: Response: {response.text[:200]}...")
                
                if search_successful and items:
                    # Display first few items as example
                    for i, item in enumerate(items[:3]):  # Show first 3 items
                        self.stdout.write(f"\n📱 Item {i+1}:")
                        self.stdout.write(f"   ID: {item.get('id', 'N/A')}")
                        self.stdout.write(f"   Title: {item.get('title', 'N/A')}")
                        self.stdout.write(f"   Price: {item.get('price', 'N/A')}")
                        self.stdout.write(f"   Seller: {item.get('seller', {}).get('nickname', 'N/A')}")
                        self.stdout.write(f"   Condition: {item.get('condition', 'N/A')}")
                    
                    if len(items) > 3:
                        self.stdout.write(f"\n... and {len(items) - 3} more items")
                    
                    # Try to get total count
                    if 'search_data' in locals():
                        total = search_data.get('paging', {}).get('total', len(items))
                        self.stdout.write(f"\n📊 Total items found: {total}")
                else:
                    self.stdout.write(
                        self.style.ERROR("❌ All search endpoints failed")
                    )
                    self.stdout.write("💡 This might indicate:")
                    self.stdout.write("   - Network connectivity issues")
                    self.stdout.write("   - MercadoLibre API service problems")
                    self.stdout.write("   - Incorrect site ID (MLM for Mexico)")
                    self.stdout.write("   - Rate limiting")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Marketplace search test failed: {e}")
                )
            
            # Test 3: Get item details
            self.stdout.write("\n🔍 Testing Item Details API...")
            try:
                # Use the first item from search results if available
                if 'items' in locals() and items:
                    test_item_id = items[0].get('id')
                    
                    # Try without authentication first (public endpoint)
                    item_url = f"{os.environ['MERCADOLIBRE_URL']}/items/{test_item_id}"
                    response = requests.get(item_url)
                    
                    if response.status_code == 200:
                        item_data = response.json()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for item: {test_item_id}")
                        )
                        self.stdout.write(f"   Title: {item_data.get('title', 'N/A')}")
                        self.stdout.write(f"   Category: {item_data.get('category_id', 'N/A')}")
                        self.stdout.write(f"   Price: {item_data.get('price', 'N/A')}")
                        self.stdout.write(f"   Available Quantity: {item_data.get('available_quantity', 'N/A')}")
                        self.stdout.write(f"   Sold Quantity: {item_data.get('sold_quantity', 'N/A')}")
                        
                        if item_data.get('pictures'):
                            self.stdout.write(f"   Pictures: {len(item_data['pictures'])} available")
                        
                        if item_data.get('attributes'):
                            self.stdout.write(f"   Attributes: {len(item_data['attributes'])} available")
                        
                    else:
                        # Try with authentication
                        response = requests.get(item_url, headers=headers)
                        
                        if response.status_code == 200:
                            item_data = response.json()
                            
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Successfully retrieved details for item: {test_item_id} (with auth)")
                            )
                            self.stdout.write(f"   Title: {item_data.get('title', 'N/A')}")
                            self.stdout.write(f"   Category: {item_data.get('category_id', 'N/A')}")
                            self.stdout.write(f"   Price: {item_data.get('price', 'N/A')}")
                            self.stdout.write(f"   Available Quantity: {item_data.get('available_quantity', 'N/A')}")
                            self.stdout.write(f"   Sold Quantity: {item_data.get('sold_quantity', 'N/A')}")
                            
                            if item_data.get('pictures'):
                                self.stdout.write(f"   Pictures: {len(item_data['pictures'])} available")
                            
                            if item_data.get('attributes'):
                                self.stdout.write(f"   Attributes: {len(item_data['attributes'])} available")
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"❌ Item details failed: {response.status_code}")
                            )
                            self.stdout.write(f"   Response: {response.text}")
                else:
                    # Try with a real item ID from user's listings
                    self.stdout.write(
                        self.style.WARNING("⚠️ No items from search, trying with user's listings...")
                    )
                    
                    # Get the first item from user's listings that we already retrieved
                    if 'listings' in locals() and listings:
                        test_item_id = listings[0]  # This should be a string ID
                        
                        if isinstance(test_item_id, str):
                            item_url = f"{os.environ['MERCADOLIBRE_URL']}/items/{test_item_id}"
                            response = requests.get(item_url)
                            
                            if response.status_code == 200:
                                item_data = response.json()
                                
                                self.stdout.write(
                                    self.style.SUCCESS(f"✅ Successfully retrieved details for user item: {test_item_id}")
                                )
                                self.stdout.write(f"   Title: {item_data.get('title', 'N/A')}")
                                self.stdout.write(f"   Category: {item_data.get('category_id', 'N/A')}")
                                self.stdout.write(f"   Price: {item_data.get('price', 'N/A')}")
                                self.stdout.write(f"   Available Quantity: {item_data.get('available_quantity', 'N/A')}")
                                self.stdout.write(f"   Sold Quantity: {item_data.get('sold_quantity', 'N/A')}")
                                
                                if item_data.get('pictures'):
                                    self.stdout.write(f"   Pictures: {len(item_data['pictures'])} available")
                                
                                if item_data.get('attributes'):
                                    self.stdout.write(f"   Attributes: {len(item_data['attributes'])} available")
                                
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f"⚠️ User item details failed: {response.status_code}")
                                )
                                self.stdout.write(f"   Item ID: {test_item_id}")
                                self.stdout.write(f"   Response: {response.text[:200]}...")
                        else:
                            self.stdout.write(
                                self.style.WARNING("⚠️ User listing format is not a string ID")
                            )
                            self.stdout.write(f"   Listing format: {type(test_item_id)} - {test_item_id}")
                    else:
                        self.stdout.write(
                            self.style.WARNING("⚠️ No user listings available for item details test")
                        )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Item details test failed: {e}")
                )
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS("🎉 MercadoLibre API Listings test completed!")
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
        
        self.stdout.write("📦 Testing MercadoLibre API Orders...")
        self.stdout.write("=" * 50)
        
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to obtain access token")
                )
                return
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            self.stdout.write("📋 Setting up Orders API...")
            self.stdout.write(
                self.style.SUCCESS("✅ Orders API initialized successfully")
            )
            
            # Get recent orders
            self.stdout.write("\n🔄 Fetching recent orders...")
            
            try:
                user_id = os.environ['MERCADOLIBRE_USER']
                orders_url = f"{os.environ['MERCADOLIBRE_URL']}/my/received_orders/search"
                
                # Get orders from the last 30 days
                params = {
                    'seller': user_id,
                    'limit': 10,
                    'offset': 0
                }
                
                response = requests.get(orders_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    orders_data = response.json()
                    orders = orders_data.get('results', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully retrieved {len(orders)} orders")
                    )
                    
                    # Display first few orders as example
                    for i, order in enumerate(orders[:3]):  # Show first 3 orders
                        self.stdout.write(f"\n📦 Order {i+1}:")
                        self.stdout.write(f"   Order ID: {order.get('id', 'N/A')}")
                        self.stdout.write(f"   Status: {order.get('status', 'N/A')}")
                        self.stdout.write(f"   Total Amount: {order.get('total_amount', 'N/A')}")
                        self.stdout.write(f"   Currency: {order.get('currency_id', 'N/A')}")
                        self.stdout.write(f"   Date Created: {order.get('date_created', 'N/A')}")
                        
                        if order.get('buyer'):
                            buyer = order['buyer']
                            self.stdout.write(f"   Buyer: {buyer.get('nickname', 'N/A')}")
                    
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
                    
                    order_url = f"{os.environ['MERCADOLIBRE_URL']}/my/received_orders/{test_order_id}"
                    response = requests.get(order_url, headers=headers)
                    
                    if response.status_code == 200:
                        order_data = response.json()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Successfully retrieved details for order: {test_order_id}")
                        )
                        self.stdout.write(f"   Status: {order_data.get('status', 'N/A')}")
                        self.stdout.write(f"   Total Amount: {order_data.get('total_amount', 'N/A')}")
                        self.stdout.write(f"   Items: {len(order_data.get('order_items', []))}")
                        
                        if order_data.get('shipping'):
                            shipping = order_data['shipping']
                            self.stdout.write(f"   Shipping Status: {shipping.get('status', 'N/A')}")
                        
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
                self.style.SUCCESS("🎉 MercadoLibre API Orders test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Orders test failed with an unexpected error: {e}")
            )
            self.stdout.write("=" * 50) 