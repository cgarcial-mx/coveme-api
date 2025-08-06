#!/usr/bin/env python3
"""
Standalone script to test Mercado Libre API with the provided credentials
"""
import os
import requests
import json
from pathlib import Path

print("🚀 Script starting...")

def load_env_file():
    """Load environment variables from .env.local file"""
    print("📂 Loading environment variables...")
    env_file = Path.cwd() / '.env.local'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env.local")
    else:
        print(f"❌ No .env.local file found at: {env_file}")

def test_meli_auth():
    """Test Mercado Libre authentication with refresh token"""
    print("🔐 Testing Mercado Libre API Authentication...")
    print("=" * 50)
    
    # Get credentials from environment
    client_id = os.environ.get('MERCADOLIBRE_APP_ID')
    client_secret = os.environ.get('MERCADOLIBRE_SECRET_KEY')
    refresh_token = os.environ.get('MERCADOLIBRE_REFRESH_TOKEN')
    meli_url = os.environ.get('MERCADOLIBRE_URL', 'https://api.mercadolibre.com')
    
    if not all([client_id, client_secret]):
        print("❌ Missing required credentials in .env.local")
        print("   Required: MERCADOLIBRE_APP_ID, MERCADOLIBRE_SECRET_KEY")
        return None
    
    print(f"✅ Using credentials:")
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {client_secret[:10]}...")
    print(f"   API URL: {meli_url}")
    
    # Try to get access token using refresh token if available
    if refresh_token and refresh_token != 'your_refresh_token_here':
        print(f"\n🔄 Using refresh token: {refresh_token[:20]}...")
        
        url = f"{meli_url}/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            print(f"🔍 Response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                new_refresh_token = token_data.get('refresh_token')
                
                print("✅ Successfully obtained access token using refresh token")
                print(f"   Access token: {access_token[:20]}...")
                if new_refresh_token:
                    print(f"   New refresh token: {new_refresh_token[:20]}...")
                
                return access_token
            else:
                print(f"❌ Failed to refresh token: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
    
    # Fallback to client credentials
    print("\n🔄 Trying client credentials flow...")
    
    url = f"{meli_url}/oauth/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            print("✅ Successfully obtained access token using client credentials")
            print(f"   Access token: {access_token[:20]}...")
            
            return access_token
        else:
            print(f"❌ Failed to get client credentials token: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting client credentials token: {e}")
    
    return None

def test_listings(access_token):
    """Test listings consumption with access token"""
    print("\n🛍️ Testing Mercado Libre API Listings...")
    print("=" * 50)
    
    if not access_token:
        print("❌ No access token available for listings test")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    meli_url = os.environ.get('MERCADOLIBRE_URL', 'https://api.mercadolibre.com')
    user_id = os.environ.get('MERCADOLIBRE_USER')
    site_id = os.environ.get('MERCADOLIBRE_SITE', 'MLM')
    
    # Test 1: Categories API (should work with client credentials)
    print("\n📂 Testing Categories API...")
    try:
        categories_url = f"{meli_url}/sites/{site_id}/categories"
        response = requests.get(categories_url, headers=headers)
        
        if response.status_code == 200:
            categories_data = response.json()
            print(f"✅ Successfully retrieved {len(categories_data)} categories")
            
            # Show first 5 categories
            for i, category in enumerate(categories_data[:5]):
                print(f"   {i+1}. {category.get('name', 'N/A')} (ID: {category.get('id', 'N/A')})")
            
            if len(categories_data) > 5:
                print(f"   ... and {len(categories_data) - 5} more categories")
                
        else:
            print(f"❌ Categories API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Categories API test failed: {e}")
    
    # Test 2: Search API (requires user authorization)
    print("\n🔍 Testing Search API...")
    try:
        search_url = f"{meli_url}/sites/{site_id}/search"
        params = {
            'q': 'smartphone',
            'limit': 5
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            search_data = response.json()
            items = search_data.get('results', [])
            
            print(f"✅ Successfully retrieved {len(items)} items from search")
            
            for i, item in enumerate(items[:3]):
                print(f"\n📱 Item {i+1}:")
                print(f"   ID: {item.get('id', 'N/A')}")
                print(f"   Title: {item.get('title', 'N/A')}")
                print(f"   Price: {item.get('price', 'N/A')}")
                print(f"   Seller: {item.get('seller', {}).get('nickname', 'N/A')}")
            
            if len(items) > 3:
                print(f"\n... and {len(items) - 3} more items")
                
        elif response.status_code == 403:
            print("❌ Search API requires user authorization (403 Forbidden)")
            print("💡 This is expected with client credentials only")
            print("🔧 To fix this, you need to:")
            print("   1. Implement OAuth 2.0 Authorization Code flow")
            print("   2. Get user authorization")
            print("   3. Use user access token instead of client credentials")
            
        else:
            print(f"❌ Search API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Search API test failed: {e}")
    
    # Test 3: User listings (if user_id is provided)
    if user_id and user_id != 'your_mercadolibre_user':
        print(f"\n📦 Testing User Listings API for user: {user_id}...")
        try:
            listings_url = f"{meli_url}/users/{user_id}/items/search"
            response = requests.get(listings_url, headers=headers)
            
            if response.status_code == 200:
                listings_data = response.json()
                listings = listings_data.get('results', [])
                
                print(f"✅ Successfully retrieved {len(listings)} user listings")
                
                for i, listing in enumerate(listings[:3]):
                    print(f"\n📦 Listing {i+1}:")
                    print(f"   ID: {listing.get('id', 'N/A')}")
                    print(f"   Title: {listing.get('title', 'N/A')}")
                    print(f"   Price: {listing.get('price', 'N/A')}")
                    print(f"   Status: {listing.get('status', 'N/A')}")
                
                if len(listings) > 3:
                    print(f"\n... and {len(listings) - 3} more listings")
                    
            else:
                print(f"❌ User listings failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ User listings test failed: {e}")
    else:
        print("\n⚠️ Skipping user listings test - no user ID provided")

def generate_auth_url():
    """Generate authorization URL for user token"""
    print("\n🔗 Generating Mercado Libre Authorization URL...")
    print("=" * 60)
    
    client_id = os.environ.get('MERCADOLIBRE_APP_ID')
    redirect_uri = os.environ.get('MERCADOLIBRE_REDIRECT_URI', 'https://forttuna.azurewebsites.net/app/main/salechannel/authorization')
    
    if not client_id:
        print("❌ MERCADOLIBRE_APP_ID not found in environment variables")
        return
    
    auth_url = f"https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    
    print("✅ Authorization URL generated:")
    print("")
    print(auth_url)
    print("")
    print("📋 Instructions:")
    print("1. Copy and paste this URL in your browser")
    print("2. Log in to your Mercado Libre account")
    print("3. Authorize the application")
    print("4. Copy the 'code' parameter from the redirect URL")
    print("5. Add the code to your .env.local file as MERCADOLIBRE_AUTH_CODE")
    print("")
    print("💡 The redirect URL will look like:")
    print(f"   {redirect_uri}?code=YOUR_AUTHORIZATION_CODE")

def main():
    """Main function to test Mercado Libre API"""
    print("🚀 Mercado Libre API Test")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Test authentication
    access_token = test_meli_auth()
    
    # Test listings
    test_listings(access_token)
    
    # Generate auth URL for user authorization
    generate_auth_url()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("💡 Next steps:")
    print("   - Use the authorization URL to get user access token")
    print("   - Add the authorization code to .env.local")
    print("   - Run the test again with user authorization")

if __name__ == "__main__":
    main() 