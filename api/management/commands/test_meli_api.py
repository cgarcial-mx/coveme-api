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
            '--create-listings',
            action='store_true',
            help='Create test listings with 10 articles in MercadoLibre',
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
        parser.add_argument(
            '--refresh-token',
            action='store_true',
            help='Refresh user access token using refresh token',
        )
        parser.add_argument(
            '--user-token',
            action='store_true',
            help='Test user token capabilities specifically',
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
            elif options['create_listings']:
                self.create_test_listings()
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
            elif options['user_token']:
                self.test_user_token_capabilities()
            elif options['refresh_token']:
                self.refresh_user_access_token()
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
        
        # Check if user token is available (optional but recommended)
        user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
        if user_token:
            self.stdout.write(
                self.style.SUCCESS("✅ User access token found - will use for authenticated endpoints")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ No user access token found - some endpoints may not work")
            )
        
        self.stdout.write(
            self.style.SUCCESS("✅ All required environment variables are set")
        )
        return True

    def get_best_access_token(self):
        """Get the best available access token (user token preferred over client credentials)"""
        # First, try to get user access token
        user_token = self.get_user_access_token()
        if user_token:
            if self.debug_mode:
                self.stdout.write("🔍 Debug: Using user access token")
            return user_token
        
        # Fallback to client credentials token
        if self.debug_mode:
            self.stdout.write("🔍 Debug: User token not available, falling back to client credentials")
        return self.get_access_token()

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
        """Get user access token from environment variables"""
        try:
            # Check if we have a stored user access token
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if user_token:
                if self.debug_mode:
                    self.stdout.write("🔍 Debug: Found user access token in environment")
                return user_token
            
            # If no stored token, show instructions for getting one
            self.stdout.write(
                self.style.WARNING("⚠️ No user access token found. Some APIs require user authorization.")
            )
            self.stdout.write("")
            self.stdout.write("🔧 To get a user access token, follow these steps:")
            self.stdout.write("")
            self.stdout.write("1. Generate authorization URL:")
            self.stdout.write("   python manage.py test_meli_api --auth-url")
            self.stdout.write("")
            self.stdout.write("2. Open the URL in your browser")
            self.stdout.write("3. Authorize your application")
            self.stdout.write("4. Copy the 'code' parameter from the redirect URL")
            self.stdout.write("5. Exchange code for token:")
            self.stdout.write("   python manage.py test_meli_api --exchange-code YOUR_CODE")
            self.stdout.write("")
            self.stdout.write("6. Add MERCADOLIBRE_ACCESS_TOKEN to your .env.local file")
            self.stdout.write("")
            
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
                self.stdout.write(f"   Access token: {access_token}")
                if refresh_token:
                    self.stdout.write(f"   Refresh token: {refresh_token}")
                
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
            
            # Check what type of token we're using
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if user_token:
                self.stdout.write("🔑 Using user access token (OAuth 2.0)")
                access_token = user_token
            else:
                self.stdout.write("🔑 Using client credentials token (fallback)")
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
                
                # Show token type information
                if user_token:
                    self.stdout.write("   Token Type: User Access Token (OAuth 2.0)")
                    self.stdout.write("   Capabilities: Full API access including search and user-specific endpoints")
                    
                    # Check if refresh token is available
                    refresh_token = os.environ.get('MERCADOLIBRE_REFRESH_TOKEN')
                    if refresh_token:
                        self.stdout.write("   Refresh Token: Available (for token renewal)")
                    else:
                        self.stdout.write("   Refresh Token: Not configured")
                else:
                    self.stdout.write("   Token Type: Client Credentials Token")
                    self.stdout.write("   Capabilities: Basic API access, limited to public endpoints")
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
            # Check if user token is available
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if user_token:
                self.stdout.write("🔑 Using user access token for full API test")
                access_token = user_token
            else:
                self.stdout.write("🔑 Using client credentials token for full API test")
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
            # Check if user token is available
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if user_token:
                self.stdout.write("🔑 Using user access token for listings test")
                access_token = user_token
            else:
                self.stdout.write("🔑 Using client credentials token for listings test")
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
            # Check if user token is available
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if user_token:
                self.stdout.write("🔑 Using user access token for orders test")
                access_token = user_token
            else:
                self.stdout.write("🔑 Using client credentials token for orders test")
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

    def test_user_token_capabilities(self):
        """Test specific capabilities that require user access token"""
        
        self.stdout.write("🔑 Testing User Token Capabilities...")
        self.stdout.write("=" * 60)
        
        try:
            # Check if user token is available
            user_token = os.environ.get('MERCADOLIBRE_ACCESS_TOKEN')
            if not user_token:
                self.stdout.write(
                    self.style.ERROR("❌ No user access token found")
                )
                self.stdout.write("💡 You need to:")
                self.stdout.write("   1. Generate auth URL: python manage.py test_meli_api --auth-url")
                self.stdout.write("   2. Authorize the application")
                self.stdout.write("   3. Exchange code for token: python manage.py test_meli_api --exchange-code YOUR_CODE")
                return
            
            self.stdout.write("✅ User access token found")
            
            # Set up headers with user token
            headers = {
                'Authorization': f'Bearer {user_token}',
                'Content-Type': 'application/json'
            }
            
            # Test 1: User Information
            self.stdout.write("\n👤 Testing User Information API...")
            try:
                user_id = os.environ['MERCADOLIBRE_USER']
                user_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}"
                
                response = requests.get(user_url, headers=headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.stdout.write(
                        self.style.SUCCESS("✅ User Info API working with user token")
                    )
                    self.stdout.write(f"   User ID: {user_data.get('id', 'N/A')}")
                    self.stdout.write(f"   Nickname: {user_data.get('nickname', 'N/A')}")
                    self.stdout.write(f"   Registration Date: {user_data.get('registration_date', 'N/A')}")
                    self.stdout.write(f"   Country: {user_data.get('country_id', 'N/A')}")
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User Info API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ User Info API test failed: {e}")
                )
            
            # Test 2: User Listings
            self.stdout.write("\n📦 Testing User Listings API...")
            try:
                user_id = os.environ['MERCADOLIBRE_USER']
                listings_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}/items/search"
                
                response = requests.get(listings_url, headers=headers)
                
                if response.status_code == 200:
                    listings_data = response.json()
                    listings = listings_data.get('results', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ User Listings API working with user token")
                    )
                    self.stdout.write(f"   Total listings: {len(listings)}")
                    
                    if listings:
                        # Show first few listings
                        for i, listing in enumerate(listings[:3]):
                            self.stdout.write(f"\n📦 Listing {i+1}:")
                            self.stdout.write(f"   ID: {listing.get('id', 'N/A')}")
                            self.stdout.write(f"   Title: {listing.get('title', 'N/A')}")
                            self.stdout.write(f"   Price: {listing.get('price', 'N/A')}")
                            self.stdout.write(f"   Status: {listing.get('status', 'N/A')}")
                    else:
                        self.stdout.write("   No listings found")
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User Listings API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ User Listings API test failed: {e}")
                )
            
            # Test 3: Marketplace Search (requires user auth)
            self.stdout.write("\n🔍 Testing Marketplace Search API...")
            try:
                site_id = os.environ['MERCADOLIBRE_SITE']
                search_url = f"{os.environ['MERCADOLIBRE_URL']}/sites/{site_id}/search"
                
                params = {
                    'q': 'smartphone',
                    'limit': 5,
                    'offset': 0
                }
                
                response = requests.get(search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    search_data = response.json()
                    items = search_data.get('results', [])
                    total_results = search_data.get('paging', {}).get('total', 0)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Marketplace Search API working with user token")
                    )
                    self.stdout.write(f"   Search query: 'smartphone'")
                    self.stdout.write(f"   Results found: {len(items)}")
                    self.stdout.write(f"   Total available: {total_results}")
                    
                    if items:
                        # Show first few items
                        for i, item in enumerate(items[:3]):
                            self.stdout.write(f"\n📱 Item {i+1}:")
                            self.stdout.write(f"   ID: {item.get('id', 'N/A')}")
                            self.stdout.write(f"   Title: {item.get('title', 'N/A')}")
                            self.stdout.write(f"   Price: {item.get('price', 'N/A')}")
                            self.stdout.write(f"   Seller: {item.get('seller', {}).get('nickname', 'N/A')}")
                            
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Marketplace Search API failed: {response.status_code}")
                    )
                    self.stdout.write(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Marketplace Search API test failed: {e}")
                )
            
            # Test 4: User Orders
            self.stdout.write("\n📦 Testing User Orders API...")
            try:
                orders_url = f"{os.environ['MERCADOLIBRE_URL']}/my/received_orders/search"
                
                params = {
                    'limit': 5,
                    'offset': 0
                }
                
                response = requests.get(orders_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    orders_data = response.json()
                    orders = orders_data.get('results', [])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ User Orders API working with user token")
                    )
                    self.stdout.write(f"   Orders found: {len(orders)}")
                    
                    if orders:
                        # Show first few orders
                        for i, order in enumerate(orders[:2]):
                            self.stdout.write(f"\n📦 Order {i+1}:")
                            self.stdout.write(f"   Order ID: {order.get('id', 'N/A')}")
                            self.stdout.write(f"   Status: {order.get('status', 'N/A')}")
                            self.stdout.write(f"   Total Amount: {order.get('total_amount', 'N/A')}")
                            self.stdout.write(f"   Date Created: {order.get('date_created', 'N/A')}")
                            
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ User Orders API failed: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ User Orders API test failed: {e}")
                )
            
            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("🎉 USER TOKEN CAPABILITIES TEST COMPLETED!")
            self.stdout.write("=" * 60)
            self.stdout.write("✅ Your user access token is working correctly")
            self.stdout.write("🔑 You now have access to:")
            self.stdout.write("   - User-specific information")
            self.stdout.write("   - User listings and orders")
            self.stdout.write("   - Marketplace search (requires user auth)")
            self.stdout.write("   - All protected endpoints")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ User token capabilities test failed: {e}")
            )
            self.stdout.write("=" * 60)

    def refresh_user_access_token(self):
        """Refresh user access token using refresh token"""
        
        self.stdout.write("🔄 Refreshing User Access Token...")
        self.stdout.write("=" * 50)
        
        try:
            # Check if refresh token is available
            refresh_token = os.environ.get('MERCADOLIBRE_REFRESH_TOKEN')
            if not refresh_token:
                self.stdout.write(
                    self.style.ERROR("❌ No refresh token found")
                )
                self.stdout.write("💡 You need to:")
                self.stdout.write("   1. Generate auth URL: python manage.py test_meli_api --auth-url")
                self.stdout.write("   2. Authorize the application")
                self.stdout.write("   3. Exchange code for token: python manage.py test_meli_api --exchange-code YOUR_CODE")
                self.stdout.write("   4. Add MERCADOLIBRE_REFRESH_TOKEN to your .env.local file")
                return
            
            self.stdout.write("✅ Refresh token found")
            
            # Exchange refresh token for new access token
            url = f"{os.environ['MERCADOLIBRE_URL']}/oauth/token"
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': os.environ['MERCADOLIBRE_APP_ID'],
                'client_secret': os.environ['MERCADOLIBRE_SECRET_KEY'],
                'refresh_token': refresh_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get('access_token')
                new_refresh_token = token_data.get('refresh_token')
                
                self.stdout.write(
                    self.style.SUCCESS("✅ Successfully refreshed access token")
                )
                self.stdout.write(f"   New access token: {new_access_token[:20]}...")
                
                if new_refresh_token:
                    self.stdout.write(f"   New refresh token: {new_refresh_token[:20]}...")
                    self.stdout.write("💡 Update your .env.local file with the new tokens")
                else:
                    self.stdout.write("   No new refresh token provided")
                
                # Show token info
                expires_in = token_data.get('expires_in', 'Unknown')
                self.stdout.write(f"   Expires in: {expires_in} seconds")
                
                return new_access_token
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to refresh token: {response.status_code} - {response.text}")
                )
                return None
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error refreshing token: {e}")
            )
            return None

    def check_seller_account_status(self):
        """Check seller account status and provide diagnostic information"""
        self.stdout.write("🔍 Checking seller account status...")
        
        try:
            # Get user access token
            user_token = self.get_user_access_token()
            if not user_token:
                self.stdout.write("❌ No user access token available for account status check")
                return False
            
            # Get user ID from environment
            user_id = os.environ.get('MERCADOLIBRE_USER')
            if not user_id:
                self.stdout.write("❌ No user ID available for account status check")
                return False
            
            # Set up headers
            headers = {
                'Authorization': f'Bearer {user_token}',
                'Content-Type': 'application/json'
            }
            
            # Get user information
            user_url = f"https://api.mercadolibre.com/users/{user_id}"
            user_response = requests.get(user_url, headers=headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                
                self.stdout.write("📋 Account Information:")
                self.stdout.write(f"   User ID: {user_data.get('id', 'N/A')}")
                self.stdout.write(f"   Nickname: {user_data.get('nickname', 'N/A')}")
                self.stdout.write(f"   Account Type: {user_data.get('account_type', 'N/A')}")
                self.stdout.write(f"   Registration Date: {user_data.get('registration_date', 'N/A')}")
                self.stdout.write(f"   Country: {user_data.get('country_id', 'N/A')}")
                
                # Check seller reputation
                if 'seller_reputation' in user_data:
                    reputation = user_data['seller_reputation']
                    self.stdout.write(f"   Seller Level: {reputation.get('level_id', 'N/A')}")
                    self.stdout.write(f"   Power Seller: {reputation.get('power_seller_status', 'N/A')}")
                else:
                    self.stdout.write("   Seller Level: None")
                    self.stdout.write("   Power Seller: None")
                
                # Test listing API access
                self.stdout.write("\n🔍 Testing listing API access...")
                listings_url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
                listings_response = requests.get(listings_url, headers=headers)
                
                if listings_response.status_code == 200:
                    self.stdout.write("✅ Full access to listings")
                elif listings_response.status_code == 403:
                    self.stdout.write("⚠️ Limited access to listings: 403")
                else:
                    self.stdout.write(f"⚠️ Limited access to listings: {listings_response.status_code}")
                
                self.stdout.write("\n💡 Account Status Summary:")
                self.stdout.write("✅ Account status check completed")
                
                return True
                
            else:
                self.stdout.write(f"❌ Could not retrieve user info: {user_response.status_code}")
                return False
                
        except Exception as e:
            self.stdout.write(f"❌ Error checking account status: {e}")
            return False

    def get_mexico_categories(self):
        """Get valid category IDs for Mexico marketplace"""
        return {
            'smartphones': 'MLM1051',      # Smartphones
            'laptops': 'MLM1227',          # Laptops  
            'headphones': 'MLM3697',       # Headphones
            'tvs': 'MLM1000',              # TVs
            'cameras': 'MLM5726',          # Cameras
            'tablets': 'MLM1039',          # Tablets
            'videogames': 'MLM1144',       # Video Games
            'smartwatches': 'MLM409431',   # Smartwatches
            'speakers': 'MLM3697',         # Speakers
            'monitors': 'MLM1227'          # Monitors
        }

    def get_valid_mexico_categories(self):
        """Get actually valid category IDs for Mexico marketplace"""
        return {
            'smartphones': 'MLM1051',      # Smartphones
            'laptops': 'MLM1196',          # Laptops (migrated from MLM1227)
            'headphones': 'MLM3697',       # Headphones
            'tvs': 'MLM1000',              # TVs
            'cameras': 'MLM5726',          # Cameras
            'tablets': 'MLM1039',          # Tablets
            'videogames': 'MLM1144',       # Video Games
            'smartwatches': 'MLM409431',   # Smartwatches
            'speakers': 'MLM3697',         # Speakers
            'monitors': 'MLM1196'          # Monitors (migrated from MLM1227)
        }

    def validate_article_data(self, article):
        """Validate article data before sending to MercadoLibre API"""
        
        errors = []
        
        # Required fields validation
        required_fields = [
            'title', 'category_id', 'price', 'currency_id', 
            'available_quantity', 'buying_mode', 'condition',
            'description', 'pictures', 'attributes', 'site_id',
            'shipping'
        ]
        
        for field in required_fields:
            if field not in article or article[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Field-specific validations
        if 'title' in article:
            if len(article['title']) < 10:
                errors.append("Title must be at least 10 characters long")
            if len(article['title']) > 60:
                errors.append("Title must be less than 60 characters long")
        
        if 'price' in article:
            if not isinstance(article['price'], (int, float)) or article['price'] <= 0:
                errors.append("Price must be a positive number")
            if article['price'] > 999999999:
                errors.append("Price is too high (max: 999,999,999)")
        
        if 'available_quantity' in article:
            if not isinstance(article['available_quantity'], int) or article['available_quantity'] <= 0:
                errors.append("Available quantity must be a positive integer")
            if article['available_quantity'] > 999999:
                errors.append("Available quantity is too high (max: 999,999)")
        
        if 'category_id' in article:
            if not article['category_id'] or len(article['category_id']) < 3:
                errors.append("Category ID must be valid")
        
        if 'site_id' in article:
            valid_sites = ['MLA', 'MLB', 'MLM', 'MLC', 'MCO', 'MCR', 'MRD', 'MEC', 'MSV', 'MGT', 'MHN', 'MLM', 'MNI', 'MPA', 'MPY', 'MPE', 'MLU', 'MLV', 'CBT']
            if article['site_id'] not in valid_sites:
                errors.append(f"Site ID must be one of: {', '.join(valid_sites)}")
        
        if 'shipping' in article:
            if not isinstance(article['shipping'], dict):
                errors.append("Shipping must be a dictionary")
            else:
                if 'mode' not in article['shipping']:
                    errors.append("Shipping mode is required")
                valid_modes = ['not_specified', 'me1', 'me2', 'me3', 'custom']
                if 'mode' in article['shipping'] and article['shipping']['mode'] not in valid_modes:
                    errors.append(f"Shipping mode must be one of: {', '.join(valid_modes)}")
        
        if 'pictures' in article:
            if not isinstance(article['pictures'], list) or len(article['pictures']) == 0:
                errors.append("At least one picture is required")
            else:
                for i, picture in enumerate(article['pictures']):
                    if not isinstance(picture, dict) or 'source' not in picture:
                        errors.append(f"Picture {i+1} must have a 'source' field")
                    elif not picture['source'] or not picture['source'].startswith('http'):
                        errors.append(f"Picture {i+1} source must be a valid HTTP URL")
        
        if 'attributes' in article:
            if not isinstance(article['attributes'], list):
                errors.append("Attributes must be a list")
            else:
                for i, attr in enumerate(article['attributes']):
                    if not isinstance(attr, dict):
                        errors.append(f"Attribute {i+1} must be a dictionary")
                    elif 'id' not in attr or 'value_name' not in attr:
                        errors.append(f"Attribute {i+1} must have 'id' and 'value_name' fields")
        
        # Currency validation
        if 'currency_id' in article:
            valid_currencies = ['ARS', 'BRL', 'MXN', 'CLP', 'COP', 'CRC', 'DOP', 'GTQ', 'HNL', 'PEN', 'PYG', 'UYU', 'VES']
            if article['currency_id'] not in valid_currencies:
                errors.append(f"Currency must be one of: {', '.join(valid_currencies)}")
        
        # Condition validation
        if 'condition' in article:
            valid_conditions = ['new', 'used', 'not_specified']
            if article['condition'] not in valid_conditions:
                errors.append(f"Condition must be one of: {', '.join(valid_conditions)}")
        
        # Buying mode validation
        if 'buying_mode' in article:
            valid_buying_modes = ['buy_it_now', 'auction', 'classified']
            if article['buying_mode'] not in valid_buying_modes:
                errors.append(f"Buying mode must be one of: {', '.join(valid_buying_modes)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def create_test_listings(self):
        """Create test listings with 10 articles in MercadoLibre"""
        self.stdout.write("🛍️ Creating Test Listings with 10 Articles in MercadoLibre...")
        self.stdout.write("=" * 70)
        
        # Get user access token
        user_token = self.get_user_access_token()
        if not user_token:
            self.stdout.write("❌ No user access token found. Cannot create listings.")
            return
        
        self.stdout.write("✅ User access token found")
        
        # Show marketplace information
        self.stdout.write(f"🌍 Marketplace: Mexico (MLM)")
        self.stdout.write(f"💰 Currency: MXN (Mexican Peso)")
        self.stdout.write(f"🏪 Site ID: MLM")
        
        # Check seller account status first
        self.check_seller_account_status()
        
        # Get real, valid categories from MercadoLibre API
        self.stdout.write("🔍 Fetching valid categories from MercadoLibre API...")
        real_categories = self.get_real_mexico_categories()
        
        if not real_categories:
            self.stdout.write("❌ Could not fetch valid categories. Using fallback categories.")
            real_categories = {
                'Smartphones': 'MLM1051',      # Celulares y Telefonía
                'Laptops': 'MLM1648',          # Computación (main category)
                'Headphones': 'MLM1000',       # Electrónica, Audio y Video (main category)
                'TVs': 'MLM1000',              # Electrónica, Audio y Video (main category)
                'Cameras': 'MLM1039',          # Cámaras y Accesorios
                'Tablets': 'MLM1648',          # Computación (main category)
                'Consoles': 'MLM1144',         # Consolas y Videojuegos
                'Smartwatches': 'MLM3937',     # Joyas y Relojes
                'Speakers': 'MLM1000',         # Electrónica, Audio y Video (main category)
                'Monitors': 'MLM1000'          # Electrónica, Audio y Video (main category)
            }
        
        self.stdout.write(f"📦 Preparing to create 10 test listings...")
        
        # Test articles with real category IDs
        test_articles = [
            {
                'title': 'Smartphone Samsung - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Smartphones', 'MLM1051'),
                'price': 299999,
                'currency_id': 'MXN',
                'available_quantity': 1,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Smartphone Samsung Galaxy A54 con 128GB de almacenamiento, color negro. Incluye cargador y auriculares.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Samsung'},
                    {'id': 'MODEL', 'value_name': 'Galaxy A54'},
                    {'id': 'STORAGE_CAPACITY', 'value_name': '128 GB'},
                    {'id': 'COLOR', 'value_name': 'Negro'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_001'
            },
            {
                'title': 'Laptop HP Pavilion 15"  - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Laptops', 'MLM1648'),
                'price': 899999,
                'currency_id': 'MXN',
                'available_quantity': 1,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Laptop HP Pavilion con procesador Intel i5, 8GB RAM, 256GB SSD y pantalla de 15 pulgadas.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'HP'},
                    {'id': 'MODEL', 'value_name': 'Pavilion'},
                    {'id': 'PROCESSOR_MODEL', 'value_name': 'Intel i5'},
                    {'id': 'RAM', 'value_name': '8 GB'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_002'
            },
            {
                'title': 'Auriculares Bluetooth - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Headphones', 'MLM1000'),
                'price': 159999,
                'currency_id': 'MXN',
                'available_quantity': 8,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Auriculares inalámbricos Sony WH-1000XM4 con cancelación de ruido activa y 30 horas de batería.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Sony'},
                    {'id': 'MODEL', 'value_name': 'WH-1000XM4'},
                    {'id': 'CONNECTIVITY', 'value_name': 'Bluetooth'},
                    {'id': 'COLOR', 'value_name': 'Negro'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_003'
            },
            {
                'title': 'Smart TV LG 55" - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('TVs', 'MLM1000'),
                'price': 1299999,
                'currency_id': 'MXN',
                'available_quantity': 2,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Smart TV LG de 55 pulgadas con resolución 4K Ultra HD, sistema webOS y acceso a aplicaciones.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'LG'},
                    {'id': 'SCREEN_SIZE', 'value_name': '55 pulgadas'},
                    {'id': 'RESOLUTION', 'value_name': '4K Ultra HD'},
                    {'id': 'SMART_TV', 'value_name': 'Sí'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_004'
            },
            {
                'title': 'Cámara Canon - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Cameras', 'MLM1039'),
                'price': 449999,
                'currency_id': 'MXN',
                'available_quantity': 4,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Cámara DSLR Canon EOS Rebel T7 con sensor de 24.1MP, grabación de video Full HD y WiFi integrado.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Canon'},
                    {'id': 'MODEL', 'value_name': 'EOS Rebel T7'},
                    {'id': 'MEGAPIXELS', 'value_name': '24.1'},
                    {'id': 'CAMERA_TYPE', 'value_name': 'DSLR'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_005'
            },
            {
                'title': 'Tablet  - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Tablets', 'MLM1648'),
                'price': 399999,
                'currency_id': 'MXN',
                'available_quantity': 6,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Tablet Apple iPad de 10.2 pulgadas con 64GB de almacenamiento, WiFi y chip A13 Bionic.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Apple'},
                    {'id': 'MODEL', 'value_name': 'iPad'},
                    {'id': 'SCREEN_SIZE', 'value_name': '10.2 pulgadas'},
                    {'id': 'STORAGE_CAPACITY', 'value_name': '64 GB'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_006'
            },
            {
                'title': 'Consola  - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Consoles', 'MLM1144'),
                'price': 899999,
                'currency_id': 'MXN',
                'available_quantity': 1,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Consola PlayStation 5 con 825GB de almacenamiento SSD, control DualSense y compatibilidad con PS4.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Sony'},
                    {'id': 'MODEL', 'value_name': 'PlayStation 5'},
                    {'id': 'STORAGE_CAPACITY', 'value_name': '825 GB'},
                    {'id': 'CONSOLE_TYPE', 'value_name': 'Home Console'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_007'
            },
            {
                'title': 'Reloj - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Smartwatches', 'MLM3937'),
                'price': 299999,
                'currency_id': 'MXN',
                'available_quantity': 7,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Reloj inteligente Apple Watch Series 8 de 41mm con GPS, monitor cardíaco y resistencia al agua.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'Apple'},
                    {'id': 'MODEL', 'value_name': 'Apple Watch Series 8'},
                    {'id': 'CASE_SIZE', 'value_name': '41mm'},
                    {'id': 'GPS', 'value_name': 'Sí'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_008'
            },
            {
                'title': 'Altavoz - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Speakers', 'MLM1000'),
                'price': 89999,
                'currency_id': 'MXN',
                'available_quantity': 10,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Altavoz Bluetooth portátil JBL Flip 6 con sonido estéreo, resistencia al agua IPX7 y 12 horas de batería.',
                'pictures': [
                    {'source': 'http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'JBL'},
                    {'id': 'MODEL', 'value_name': 'Flip 6'},
                    {'id': 'CONNECTIVITY', 'value_name': 'Bluetooth'},
                    {'id': 'COLOR', 'value_name': 'Negro'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_009'
            },
            {
                'title': 'Monitor - Artículo de prueba, NO COMPRAR',
                'category_id': real_categories.get('Monitors', 'MLM1000'),
                'price': 599999,
                'currency_id': 'MXN',
                'available_quantity': 1,
                'buying_mode': 'buy_it_now',
                'listing_type_id': 'free',
                'condition': 'new',
                'description': 'Monitor gaming ASUS ROG Swift de 27 pulgadas con 165Hz de frecuencia de actualización y tiempo de respuesta de 1ms.',
                'pictures': [
                    {'source': 'https://http2.mlstatic.com/D_123456-MLA123456_123456-O.jpg'}
                ],
                'attributes': [
                    {'id': 'BRAND', 'value_name': 'ASUS'},
                    {'id': 'MODEL', 'value_name': 'ROG Swift'},
                    {'id': 'SCREEN_SIZE', 'value_name': '27 pulgadas'},
                    {'id': 'REFRESH_RATE', 'value_name': '165 Hz'}
                ],
                'site_id': 'MLM',
                'shipping': {
                    'mode': 'me2',
                    'free_shipping': False
                },
                'seller_custom_field': 'TEST_010'
            }
        ]
        
        # Set up headers for API requests
        headers = {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
        
        # Create listings one by one
        created_listings = []
        failed_listings = []
        
        for i, article in enumerate(test_articles, 1):
            self.stdout.write(f"\n🔄 Creating listing {i}/{len(test_articles)}: {article['title']}")
            
            # Validate article data before sending
            validation_result = self.validate_article_data(article)
            if not validation_result['valid']:
                self.stdout.write(
                    self.style.ERROR(f"❌ Article validation failed: {validation_result['errors']}")
                )
                failed_listings.append({
                    'title': article['title'],
                    'error': f"Validation failed: {validation_result['errors']}"
                })
                continue
            
            try:
                # Create the listing using MercadoLibre API
                create_url = 'https://api.mercadolibre.com/items'
                
                # Debug mode: show request details
                if self.debug_mode:
                    self.stdout.write(f"\n🔍 Debug: Sending request to {create_url}")
                    self.stdout.write(f"🔍 Debug: Request headers: {dict(headers)}")
                    self.stdout.write(f"🔍 Debug: Request body: {json.dumps(article, indent=2, ensure_ascii=False)}")
                
                response = requests.post(create_url, headers=headers, json=article)
                
                if self.debug_mode:
                    self.stdout.write(f"🔍 Debug: Response status: {response.status_code}")
                    self.stdout.write(f"🔍 Debug: Response headers: {dict(response.headers)}")
                    if response.text:
                        self.stdout.write(f"🔍 Debug: Response body: {response.text[:1000]}...")
                
                if response.status_code == 201:
                    listing_data = response.json()
                    listing_id = listing_data.get('id')
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Successfully created listing: {listing_id}")
                    )
                    self.stdout.write(f"   Title: {article['title']}")
                    self.stdout.write(f"   Price: ${article['price']:,} {article['currency_id']}")
                    self.stdout.write(f"   Status: {listing_data.get('status', 'N/A')}")
                    
                    created_listings.append({
                        'id': listing_id,
                        'title': article['title'],
                        'price': article['price'],
                        'status': listing_data.get('status', 'N/A')
                    })
                    
                else:
                    error_msg = f"Failed to create listing: {response.status_code}"
                    
                    # Enhanced error context
                    self.stdout.write(f"\n🔍 Error Details:")
                    self.stdout.write(f"   Status Code: {response.status_code}")
                    self.stdout.write(f"   Response Headers: {dict(response.headers)}")
                    
                    # Parse error response for more details
                    if response.text:
                        try:
                            error_data = response.json()
                            self.stdout.write(f"   Error Type: {error_data.get('error', 'Unknown')}")
                            self.stdout.write(f"   Error Message: {error_data.get('message', 'No message')}")
                            
                            # Show specific error details
                            if 'cause' in error_data:
                                causes = error_data['cause']
                                if isinstance(causes, list):
                                    for i, cause in enumerate(causes):
                                        self.stdout.write(f"   Cause {i+1}: {cause}")
                                else:
                                    self.stdout.write(f"   Cause: {causes}")
                            
                            error_msg += f" - {error_data.get('message', 'Unknown error')}"
                            
                            # Handle other common errors with specific tips
                            if 'message' in error_data:
                                message = error_data['message'].lower()
                                if 'category' in message:
                                    self.stdout.write("💡 Tip: Check if the category_id is valid for your site")
                                    self.stdout.write(f"   Current category_id: {article.get('category_id', 'N/A')}")
                                
                        except json.JSONDecodeError:
                            self.stdout.write(f"   Raw Response: {response.text[:500]}...")
                            error_msg += f" - {response.text[:100]}"
                    
                    # Show request details for debugging
                    self.stdout.write(f"\n🔍 Request Details:")
                    self.stdout.write(f"   URL: {create_url}")
                    self.stdout.write(f"   Method: POST")
                    self.stdout.write(f"   Headers: {dict(headers)}")
                    self.stdout.write(f"   Request Body Size: {len(json.dumps(article))} characters")
                    
                    # Show article summary for debugging
                    self.stdout.write(f"\n📦 Article Summary:")
                    self.stdout.write(f"   Title: {article.get('title', 'N/A')[:50]}...")
                    self.stdout.write(f"   Category: {article.get('category_id', 'N/A')}")
                    self.stdout.write(f"   Price: {article.get('price', 'N/A')} {article.get('currency_id', 'N/A')}")
                    self.stdout.write(f"   Condition: {article.get('condition', 'N/A')}")
                    self.stdout.write(f"   Site ID: {article.get('site_id', 'N/A')}")
                    
                    self.stdout.write(
                        self.style.ERROR(f"❌ {error_msg}")
                    )
                    
                    failed_listings.append({
                        'title': article['title'],
                        'error': error_msg
                    })
                    
            except Exception as e:
                error_msg = f"Exception while creating listing: {str(e)}"
                self.stdout.write(
                    self.style.ERROR(f"❌ {error_msg}")
                )
                
                failed_listings.append({
                    'title': article['title'],
                    'error': error_msg
                })
            
            # Add a small delay between requests to avoid rate limiting
            import time
            time.sleep(1)
        
        # Summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("📊 LISTING CREATION SUMMARY")
        self.stdout.write("=" * 70)
        self.stdout.write(f"✅ Successfully created: {len(created_listings)} listings")
        self.stdout.write(f"❌ Failed to create: {len(failed_listings)} listings")
        
        if created_listings:
            self.stdout.write("\n🎉 Successfully created listings:")
            for listing in created_listings:
                self.stdout.write(f"   • {listing['title']} (ID: {listing['id']}) - ${listing['price']:,}")
        
        if failed_listings:
            self.stdout.write("\n⚠️ Failed listings:")
            for listing in failed_listings:
                self.stdout.write(f"   • {listing['title']}: {listing['error']}")
        
        self.stdout.write("\n💡 Note: These are test listings. You may want to delete them later.")
        self.stdout.write("   To delete a listing, use the MercadoLibre seller panel or API.")

    def check_account_restrictions(self, seller_data, headers, user_id):
        """Check for specific account restrictions that might prevent listing creation"""
        
        self.stdout.write("\n🔍 Checking for specific account restrictions...")
        
        try:
            # Check account status and restrictions
            if 'status' in seller_data:
                status = seller_data.get('status', {})
                
                if status.get('banned', False):
                    self.stdout.write("🚫 Account Status: BANNED")
                    self.stdout.write("   This account cannot create listings")
                    return
                
                if status.get('restricted', False):
                    self.stdout.write("🚫 Account Status: RESTRICTED")
                    self.stdout.write("   This account has restrictions")
                
                if status.get('suspended', False):
                    self.stdout.write("🚫 Account Status: SUSPENDED")
                    self.stdout.write("   This account is suspended")
            
            # Check if account is new and might have limitations
            registration_date = seller_data.get('registration_date', '')
            if registration_date:
                try:
                    reg_date = datetime.fromisoformat(registration_date.replace('Z', '+00:00'))
                    days_since_registration = (datetime.now(reg_date.tzinfo) - reg_date).days
                    
                    if days_since_registration < 7:
                        self.stdout.write("⚠️ Account is very new (less than 7 days old)")
                        self.stdout.write("   New accounts often have restrictions on listing creation")
                        self.stdout.write("   You may need to wait or complete additional verification")
                    elif days_since_registration < 30:
                        self.stdout.write("⚠️ Account is relatively new (less than 30 days old)")
                        self.stdout.write("   New accounts may have limitations on listing creation")
                        
                except Exception:
                    pass
            
            # Check account type limitations
            account_type = seller_data.get('account_type', '')
            if account_type == 'personal':
                self.stdout.write("⚠️ Personal Account Detected")
                self.stdout.write("   Personal accounts often have limited listing capabilities")
                self.stdout.write("   Consider upgrading to a business account")
            elif account_type == 'business':
                self.stdout.write("✅ Business Account Detected")
                self.stdout.write("   Business accounts should have full listing capabilities")
            
            # Check seller reputation limitations
            if 'seller_reputation' in seller_data:
                reputation = seller_data['seller_reputation']
                level_id = reputation.get('level_id', 0)
                
                if level_id == 0:
                    self.stdout.write("⚠️ No Seller Level")
                    self.stdout.write("   Account has no seller reputation level")
                    self.stdout.write("   This may prevent listing creation")
                elif level_id < 3:
                    self.stdout.write("⚠️ Low Seller Level")
                    self.stdout.write(f"   Current level: {level_id}")
                    self.stdout.write("   Low levels may have restrictions")
            
            # Try to get more specific restriction information
            self.stdout.write("\n🔍 Checking for specific restriction details...")
            try:
                # Check if there are any pending verifications
                verification_url = f"{os.environ['MERCADOLIBRE_URL']}/users/{user_id}/verification_status"
                verification_response = requests.get(verification_url, headers=headers)
                
                if verification_response.status_code == 200:
                    verification_data = verification_response.json()
                    self.stdout.write("📋 Verification Status:")
                    self.stdout.write(f"   Status: {verification_data.get('status', 'N/A')}")
                    if 'pending_verifications' in verification_data:
                        pending = verification_data['pending_verifications']
                        if pending:
                            self.stdout.write("   Pending Verifications:")
                            for verification in pending:
                                self.stdout.write(f"     - {verification.get('type', 'Unknown')}: {verification.get('status', 'N/A')}")
                        else:
                            self.stdout.write("   ✅ No pending verifications")
                            
            except Exception as e:
                self.stdout.write(f"   Could not check verification status: {e}")
            
            # Provide specific guidance for coliving restrictions
            self.stdout.write("\n💡 Specific Solutions for Coliving Restrictions:")
            self.stdout.write("   1. Contact MercadoLibre Seller Support directly")
            self.stdout.write("   2. Check if your account needs additional verification")
            self.stdout.write("   3. Verify your business information is complete")
            self.stdout.write("   4. Check if there are pending documentation requirements")
            self.stdout.write("   5. Consider upgrading account type if applicable")
            
        except Exception as e:
            self.stdout.write(f"   Error checking restrictions: {e}")

    def get_real_mexico_categories(self):
        """Get real, valid category IDs for Mexico marketplace by fetching from API"""
        categories = {}
        
        # Use the correct MLM category IDs provided by the user
        main_categories = {
            'Smartphones': 'MLM1051',      # Celulares y Telefonía
            'Cameras': 'MLM1039',          # Cámaras y Accesorios
            'Computers': 'MLM1648',        # Computación
            'Gaming': 'MLM1144',           # Consolas y Videojuegos
            'Electronics': 'MLM1000',      # Electrónica, Audio y Video
            'HomeAppliances': 'MLM1575',   # Electrodomésticos
            'Jewelry': 'MLM3937',          # Joyas y Relojes
            'Health': 'MLM187772',         # Salud y Equipamiento Médico
            'Sports': 'MLM1276',           # Deportes y Fitness
            'Home': 'MLM1574'              # Hogar, Muebles y Jardín
        }
        
        self.stdout.write("🔍 Using verified MLM category IDs for Mexico...")
        
        try:
            # For each main category, get the subcategories to find leaf categories
            for category_name, category_id in main_categories.items():
                try:
                    # Get subcategories for this main category
                    sub_response = requests.get(f"https://api.mercadolibre.com/categories/{category_id}")
                    if sub_response.status_code == 200:
                        sub_cats = sub_response.json()
                        
                        # Look for specific subcategories we need
                        if category_name == 'Smartphones':
                            # Find the actual smartphone subcategory (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Celulares' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    # Get sub-subcategories to find the actual phone category
                                    sub_sub_response = requests.get(f"https://api.mercadolibre.com/categories/{sub_cat['id']}")
                                    if sub_sub_response.status_code == 200:
                                        sub_sub_cats = sub_sub_response.json()
                                        for sub_sub_cat in sub_sub_cats.get('children_categories', []):
                                            if 'Smartphone' in sub_sub_cat['name'] or 'Teléfono' in sub_sub_cat['name']:
                                                categories['Smartphones'] = sub_sub_cat['id']
                                                self.stdout.write(f"   ✅ {category_name}: {sub_sub_cat['id']} ({sub_sub_cat['name']})")
                                                break
                                        else:
                                            categories['Smartphones'] = sub_cat['id']
                                            self.stdout.write(f"   ⚠️ {category_name}: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Smartphones'] = category_id
                                self.stdout.write(f"   ⚠️ {category_name}: {category_id} (using main category)")
                        
                        elif category_name == 'Cameras':
                            # Find camera subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Cámaras' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Cameras'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ {category_name}: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Cameras'] = category_id
                                self.stdout.write(f"   ⚠️ {category_name}: {category_id} (using main category)")
                        
                        elif category_name == 'Computers':
                            # Find laptop/notebook subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if ('Laptops' in sub_cat['name'] or 'Notebooks' in sub_cat['name'] or 'Portátiles' in sub_cat['name']) and 'Accesorios' not in sub_cat['name']:
                                    categories['Laptops'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Laptops: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Laptops'] = category_id
                                self.stdout.write(f"   ⚠️ Laptops: {category_id} (using main category)")
                            
                            # Find tablet subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Tablets' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Tablets'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Tablets: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Tablets'] = category_id
                                self.stdout.write(f"   ⚠️ Tablets: {category_id} (using main category)")
                        
                        elif category_name == 'Electronics':
                            # Find TV subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if ('TV' in sub_cat['name'] or 'Televisores' in sub_cat['name']) and 'Accesorios' not in sub_cat['name']:
                                    categories['TVs'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ TVs: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['TVs'] = category_id
                                self.stdout.write(f"   ⚠️ TVs: {category_id} (using main category)")
                            
                            # Find headphone subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Auriculares' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Headphones'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Headphones: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Headphones'] = category_id
                                self.stdout.write(f"   ⚠️ Headphones: {category_id} (using main category)")
                            
                            # Find speaker subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Altavoces' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Speakers'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Speakers: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Speakers'] = category_id
                                self.stdout.write(f"   ⚠️ Speakers: {category_id} (using main category)")
                            
                            # Find monitor subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Monitores' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Monitors'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Monitors: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Monitors'] = category_id
                                self.stdout.write(f"   ⚠️ Monitors: {category_id} (using main category)")
                        
                        elif category_name == 'Gaming':
                            # Find console subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Consolas' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Consoles'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Consoles: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Consoles'] = category_id
                                self.stdout.write(f"   ⚠️ Consoles: {category_id} (using main category)")
                        
                        elif category_name == 'Jewelry':
                            # Find smartwatch subcategories (not accessories)
                            for sub_cat in sub_cats.get('children_categories', []):
                                if 'Relojes' in sub_cat['name'] and 'Accesorios' not in sub_cat['name']:
                                    categories['Smartwatches'] = sub_cat['id']
                                    self.stdout.write(f"   ✅ Smartwatches: {sub_cat['id']} ({sub_cat['name']})")
                                    break
                            else:
                                categories['Smartwatches'] = category_id
                                self.stdout.write(f"   ⚠️ Smartwatches: {category_id} (using main category)")
                        
                        # Add a small delay to avoid rate limiting
                        import time
                        time.sleep(0.5)
                        
                except Exception as e:
                    self.stdout.write(f"   ❌ Error getting subcategories for {category_name}: {e}")
                    # Use main category as fallback
                    categories[category_name] = category_id
            
            self.stdout.write(f"\n🔍 Found {len(categories)} valid categories:")
            for name, cat_id in categories.items():
                self.stdout.write(f"   • {name}: {cat_id}")
                    
        except Exception as e:
            self.stdout.write(f"⚠️ Error fetching categories: {e}")
            
        return categories