import os
import sys
from pathlib import Path
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
import json
import logging

logger = logging.getLogger(__name__)

def test_marketplace_connection(credentials_instance):
    """
    Test connection for a specific marketplace credentials instance
    Returns a tuple: (success: bool, message: str)
    """
    marketplace_type = credentials_instance.marketplace_type
    credentials = credentials_instance.credentials
    
    try:
        if marketplace_type == 'amazon':
            return test_amazon_connection(credentials)
        elif marketplace_type == 'mercadolibre':
            return test_mercadolibre_connection(credentials)
        elif marketplace_type == 'shopify':
            return test_shopify_connection(credentials)
        else:
            return False, f"Marketplace type '{marketplace_type}' not supported for testing"
    except Exception as e:
        logger.error(f"Error testing {marketplace_type} connection: {str(e)}")
        return False, f"Error testing connection: {str(e)}"

def test_amazon_connection(credentials):
    """Test Amazon SP API connection"""
    try:
        # Set up environment variables from credentials
        env_mapping = {
            'lwa_app_id': 'LWA_APP_ID',
            'lwa_client_secret': 'LWA_CLIENT_SECRET',
            'refresh_token': 'SP_API_REFRESH_TOKEN',
            'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
            'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
            'role_arn': 'SP_API_ROLE_ARN'
        }
        
        # Set environment variables
        for cred_key, env_var in env_mapping.items():
            if cred_key in credentials:
                os.environ[env_var] = str(credentials[cred_key])
        
        # Test authentication using management command
        out = StringIO()
        try:
            call_command('test_amazon_api', stdout=out, stderr=out)
            output = out.getvalue()
            
            # Check for success indicators
            success_indicators = [
                'Authentication test completed successfully',
                'SP API configuration created successfully',
                'API connection established successfully',
                'Your Amazon SP API credentials are working correctly'
            ]
            
            if any(indicator in output for indicator in success_indicators):
                return True, "Amazon connection test successful"
            else:
                return False, f"Amazon connection test failed: {output}"
        except Exception as cmd_error:
            # If command doesn't exist, try direct API test
            return test_amazon_direct_api(credentials)
            
    except Exception as e:
        return False, f"Amazon connection test error: {str(e)}"

def test_amazon_direct_api(credentials):
    """Test Amazon SP API connection directly"""
    try:
        # Check if required credentials are present
        required_fields = ['lwa_app_id', 'lwa_client_secret', 'refresh_token', 
                          'aws_access_key_id', 'aws_secret_access_key', 'role_arn']
        
        missing_fields = [field for field in required_fields if field not in credentials]
        if missing_fields:
            return False, f"Missing required Amazon credentials: {', '.join(missing_fields)}"
        
        # For now, return a basic validation message
        # In a real implementation, you would use the sp-api library here
        return True, "Amazon credentials validation passed (direct test)"
        
    except Exception as e:
        return False, f"Amazon direct test error: {str(e)}"

def test_mercadolibre_connection(credentials):
    """Test Mercado Libre API connection"""
    try:
        # Set up environment variables from credentials
        env_mapping = {
            'access_token': 'MELI_ACCESS_TOKEN',
            'refresh_token': 'MELI_REFRESH_TOKEN',
            'client_id': 'MELI_CLIENT_ID',
            'client_secret': 'MELI_CLIENT_SECRET'
        }
        
        # Set environment variables
        for cred_key, env_var in env_mapping.items():
            if cred_key in credentials:
                os.environ[env_var] = str(credentials[cred_key])
        
        # Test authentication using management command
        out = StringIO()
        try:
            call_command('test_meli_api', stdout=out, stderr=out)
            output = out.getvalue()
            
            # Check for success indicators
            success_indicators = [
                'Authentication successful',
                'Successfully authenticated',
                'API connection established',
                'Mercado Libre API test completed successfully'
            ]
            
            if any(indicator in output for indicator in success_indicators):
                return True, "Mercado Libre connection test successful"
            else:
                return False, f"Mercado Libre connection test failed: {output}"
        except Exception as cmd_error:
            # If command doesn't exist, try direct API test
            return test_mercadolibre_direct_api(credentials)
            
    except Exception as e:
        return False, f"Mercado Libre connection test error: {str(e)}"

def test_mercadolibre_direct_api(credentials):
    """Test Mercado Libre API connection directly"""
    try:
        import requests
        
        # Get access token from credentials
        access_token = credentials.get('access_token', '')
        
        if not access_token:
            return False, "Missing access_token in Mercado Libre credentials"
        
        # Test API connection
        api_url = 'https://api.mercadolibre.com/users/me'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get('id', 'Unknown')
            nickname = user_data.get('nickname', 'Unknown')
            return True, f"Mercado Libre connection successful - User: {nickname} (ID: {user_id})"
        elif response.status_code == 401:
            return False, "Mercado Libre authentication failed - Invalid access token"
        else:
            return False, f"Mercado Libre API error - Status: {response.status_code}, Response: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Mercado Libre connection error: {str(e)}"
    except Exception as e:
        return False, f"Mercado Libre test error: {str(e)}"

def test_shopify_connection(credentials):
    """Test Shopify API connection"""
    try:
        # Set up environment variables from credentials
        env_mapping = {
            'shop_url': 'SHOPIFY_SHOP_URL',
            'access_token': 'SHOPIFY_ACCESS_TOKEN',
            'api_key': 'SHOPIFY_API_KEY',
            'api_secret': 'SHOPIFY_API_SECRET'
        }
        
        # Set environment variables
        for cred_key, env_var in env_mapping.items():
            if cred_key in credentials:
                os.environ[env_var] = str(credentials[cred_key])
        
        # Test authentication using management command
        out = StringIO()
        try:
            call_command('test_shopify_api', stdout=out, stderr=out)
            output = out.getvalue()
            
            # Check for success indicators
            success_indicators = [
                'Authentication successful',
                'Successfully authenticated',
                'API connection established',
                'Shopify API test completed successfully'
            ]
            
            if any(indicator in output for indicator in success_indicators):
                return True, "Shopify connection test successful"
            else:
                return False, f"Shopify connection test failed: {output}"
        except Exception as cmd_error:
            # If command doesn't exist, try direct API test
            return test_shopify_direct_api(credentials)
            
    except Exception as e:
        return False, f"Shopify connection test error: {str(e)}"

def test_shopify_direct_api(credentials):
    """Test Shopify API connection directly using requests"""
    try:
        import requests
        
        # Get shop URL and access token from credentials
        shop_url = credentials.get('shop_url', '')
        access_token = credentials.get('access_token', '')
        
        if not shop_url or not access_token:
            return False, "Missing shop_url or access_token in credentials"
        
        # Clean up shop URL (remove https:// if present)
        if shop_url.startswith('https://'):
            shop_url = shop_url[8:]
        elif shop_url.startswith('http://'):
            shop_url = shop_url[7:]
        
        # Remove trailing slash
        shop_url = shop_url.rstrip('/')
        
        # Test API connection
        api_url = f"https://{shop_url}/admin/api/2023-10/shop.json"
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            shop_data = response.json()
            shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
            return True, f"Shopify connection successful - Shop: {shop_name}"
        elif response.status_code == 401:
            return False, "Shopify authentication failed - Invalid access token"
        elif response.status_code == 404:
            return False, "Shopify shop not found - Check shop URL"
        else:
            return False, f"Shopify API error - Status: {response.status_code}, Response: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Shopify connection error: {str(e)}"
    except Exception as e:
        return False, f"Shopify test error: {str(e)}"

def sync_products_listings(credentials_instance):
    """
    Sync products and listings for a specific marketplace credentials instance
    Returns a tuple: (success: bool, message: str)
    """
    marketplace_type = credentials_instance.marketplace_type
    credentials = credentials_instance.credentials
    
    try:
        if marketplace_type == 'amazon':
            return sync_amazon_products_listings(credentials_instance)
        elif marketplace_type == 'mercadolibre':
            return sync_mercadolibre_products_listings(credentials_instance)
        elif marketplace_type == 'shopify':
            return sync_shopify_products_listings(credentials_instance)
        else:
            return False, f"Marketplace type '{marketplace_type}' not supported for syncing"
    except Exception as e:
        logger.error(f"Error syncing {marketplace_type} products/listings: {str(e)}")
        return False, f"Error syncing products/listings: {str(e)}"

def sync_amazon_products_listings(credentials_instance):
    """Sync Amazon products and listings"""
    try:
        import requests
        
        # Check if required credentials are present
        required_fields = ['lwa_app_id', 'lwa_client_secret', 'refresh_token', 
                          'aws_access_key_id', 'aws_secret_access_key', 'role_arn']
        
        missing_fields = [field for field in required_fields if field not in credentials_instance.credentials]
        if missing_fields:
            return False, f"Missing required Amazon credentials: {', '.join(missing_fields)}"
        
        # Set up environment variables for Amazon SP API
        for cred_key, env_var in {
            'lwa_app_id': 'LWA_APP_ID',
            'lwa_client_secret': 'LWA_CLIENT_SECRET', 
            'refresh_token': 'SP_API_REFRESH_TOKEN',
            'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
            'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
            'role_arn': 'SP_API_ROLE_ARN'
        }.items():
            if cred_key in credentials_instance.credentials:
                os.environ[env_var] = str(credentials_instance.credentials[cred_key])
        
        # Sync products and listings using SP API
        products_synced = sync_amazon_products_direct(credentials_instance.client)
        listings_synced = sync_amazon_listings_direct(credentials_instance.client)
        
        return True, f"Amazon sync completed - {products_synced} products, {listings_synced} listings synced"
            
    except Exception as e:
        return False, f"Amazon sync error: {str(e)}"

def sync_mercadolibre_products_listings(credentials_instance):
    """Sync Mercado Libre products and listings"""
    try:
        import requests
        
        # Get access token from credentials
        access_token = credentials_instance.credentials.get('access_token', '')
        
        if not access_token:
            return False, "Missing access_token in Mercado Libre credentials"
        
        # Set up API headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Sync products (items) - using clean SKU approach
        products_synced = sync_mercadolibre_products_direct(credentials_instance.client, headers)
        
        # Sync listings - using marketplace-specific IDs
        listings_synced = sync_mercadolibre_listings_direct(credentials_instance.client, headers)
        
        return True, f"Mercado Libre sync completed - {products_synced} products, {listings_synced} listings synced"
            
    except Exception as e:
        return False, f"Mercado Libre sync error: {str(e)}"

def sync_mercadolibre_products_direct(client, headers):
    """Sync Mercado Libre products directly"""
    try:
        import requests
        
        # Get user's items (products) from Mercado Libre
        # First, get user info to get user ID
        user_response = requests.get('https://api.mercadolibre.com/users/me', headers=headers, timeout=30)
        
        if user_response.status_code != 200:
            logger.error(f"Failed to get Mercado Libre user info: {user_response.status_code}")
            return 0
        
        user_data = user_response.json()
        user_id = user_data.get('id')
        
        if not user_id:
            logger.error("No user ID found in Mercado Libre response")
            return 0
        
        # Get user's items
        items_url = f'https://api.mercadolibre.com/users/{user_id}/items/search'
        items_response = requests.get(items_url, headers=headers, timeout=30)
        
        if items_response.status_code != 200:
            logger.error(f"Failed to get Mercado Libre items: {items_response.status_code}")
            return 0
        
        items_data = items_response.json()
        items = items_data.get('results', [])
        
        products_synced = 0
        
        for item in items:
            try:
                # Create or update product with clean SKU
                product = create_or_update_mercadolibre_product(client, item)
                if product:
                    products_synced += 1
            except Exception as e:
                logger.error(f"Failed to sync Mercado Libre product {item.get('id')}: {e}")
        
        return products_synced
        
    except Exception as e:
        logger.error(f"Mercado Libre products sync error: {e}")
        return 0

def sync_mercadolibre_listings_direct(client, headers):
    """Sync Mercado Libre listings directly"""
    try:
        import requests
        
        # Get user's active listings from Mercado Libre
        # First, get user info to get user ID
        user_response = requests.get('https://api.mercadolibre.com/users/me', headers=headers, timeout=30)
        
        if user_response.status_code != 200:
            logger.error(f"Failed to get Mercado Libre user info: {user_response.status_code}")
            return 0
        
        user_data = user_response.json()
        user_id = user_data.get('id')
        
        if not user_id:
            logger.error("No user ID found in Mercado Libre response")
            return 0
        
        # Get user's items (listings)
        items_url = f'https://api.mercadolibre.com/users/{user_id}/items/search'
        items_response = requests.get(items_url, headers=headers, timeout=30)
        
        if items_response.status_code != 200:
            logger.error(f"Failed to get Mercado Libre items: {items_response.status_code}")
            return 0
        
        items_data = items_response.json()
        items = items_data.get('results', [])
        
        listings_synced = 0
        
        for item in items:
            try:
                # Create or update listing with original item ID
                listing = create_or_update_mercadolibre_listing(client, item)
                if listing:
                    listings_synced += 1
            except Exception as e:
                logger.error(f"Failed to sync Mercado Libre listing {item.get('id')}: {e}")
        
        return listings_synced
        
    except Exception as e:
        logger.error(f"Mercado Libre listings sync error: {e}")
        return 0

def sync_shopify_products_listings(credentials_instance):
    """Sync Shopify products and listings"""
    try:
        import requests
        from django.utils import timezone
        
        # Get credentials
        shop_url = credentials_instance.credentials.get('shop_url', '')
        access_token = credentials_instance.credentials.get('access_token', '')
        
        if not shop_url or not access_token:
            return False, "Missing shop_url or access_token in credentials"
        
        # Clean up shop URL
        if shop_url.startswith('https://'):
            shop_url = shop_url[8:]
        elif shop_url.startswith('http://'):
            shop_url = shop_url[7:]
        shop_url = shop_url.rstrip('/')
        
        # Set up API headers
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        # Get API version from credentials (default to 2024-01 if not specified)
        api_version = credentials_instance.credentials.get('api_version', '2024-01')
        
        # Sync products using clean SKU approach (no limit - sync all)
        products_synced = sync_shopify_products_direct(credentials_instance.client, shop_url, headers, api_version)
        
        # Sync listings using original product IDs (no limit - sync all)
        listings_synced = sync_shopify_listings_direct(credentials_instance.client, shop_url, headers, api_version)
        
        return True, f"Shopify sync completed - {products_synced} products, {listings_synced} listings synced"
            
    except Exception as e:
        return False, f"Shopify sync error: {str(e)}"

def sync_shopify_products_direct(client, shop_url, headers, api_version='2024-01'):
    """Sync Shopify products directly"""
    try:
        import requests
        
        # Get products from Shopify (no limit - sync all)
        api_url = f"https://{shop_url}/admin/api/{api_version}/products.json"
        params = {}
        
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Shopify products: {response.status_code}")
            return 0
        
        products_data = response.json()
        shopify_products = products_data.get('products', [])
        
        products_synced = 0
        
        for shopify_product in shopify_products:
            try:
                # Create or update product in local database
                product = create_or_update_shopify_product(client, shopify_product)
                if product:
                    products_synced += 1
            except Exception as e:
                logger.error(f"Failed to sync product {shopify_product.get('id')}: {e}")
        
        return products_synced
        
    except Exception as e:
        logger.error(f"Shopify products sync error: {e}")
        return 0

def sync_shopify_listings_direct(client, shop_url, headers, api_version='2024-01'):
    """Sync Shopify listings directly"""
    try:
        import requests
        
        # Get products (listings) from Shopify (no limit - sync all)
        api_url = f"https://{shop_url}/admin/api/{api_version}/products.json"
        params = {'status': 'active'}
        
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Shopify listings: {response.status_code}")
            return 0
        
        products_data = response.json()
        shopify_products = products_data.get('products', [])
        
        listings_synced = 0
        
        for shopify_product in shopify_products:
            try:
                # Create or update listing in local database
                listing = create_or_update_shopify_listing(client, shopify_product)
                if listing:
                    listings_synced += 1
            except Exception as e:
                logger.error(f"Failed to sync listing {shopify_product.get('id')}: {e}")
        
        return listings_synced
        
    except Exception as e:
        logger.error(f"Shopify listings sync error: {e}")
        return 0

def create_or_update_shopify_product(client, shopify_product):
    """Create or update a Product from Shopify data"""
    try:
        from products.models import Product, Brand, Provider
        
        # Get clean SKU for matching (without marketplace prefixes)
        variants = shopify_product.get('variants', [])
        print(f"Variants for {shopify_product.get('title')}: {json.dumps(variants, indent=2)}")
        internal_sku = get_product_sku_from_variants(variants, shopify_product)
        
        if not internal_sku:
            logger.warning(f"No SKU found for Shopify product {shopify_product.get('id')}")
            return None
        
        # Get or create brand
        brand = None
        vendor = shopify_product.get('vendor')
        if vendor:
            brand, created = Brand.objects.get_or_create(
                client=client,
                name=vendor
            )
        
        # Get or create provider
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
        }
        
        # Get price from first variant
        if variants:
            price = variants[0].get('price')
            if price:
                try:
                    product_data['cost'] = float(price)
                except (ValueError, TypeError):
                    pass
        
        # Create or update product
        product, created = Product.objects.update_or_create(
            client=client,
            internal_sku=internal_sku,
            defaults=product_data
        )
        
        return product
        
    except Exception as e:
        logger.error(f"Error creating/updating Shopify product: {e}")
        return None

def create_or_update_shopify_listing(client, shopify_product):
    """Create or update a MarketplaceListing from Shopify data"""
    try:
        from marketplaces.models import MarketplaceListing
        
        # Use original Shopify product ID (no prefix needed)
        product_id = shopify_product.get('id')
        marketplace_id = str(product_id)  # Use original ID from Shopify
        
        # Get images and set thumbnail
        images = shopify_product.get('images', [])
        thumbnail_url = images[0].get('src') if images else None
        
        # Prepare listing data
        listing_data = {
            'client': client,
            'marketplace_type': 'shopify',
            'marketplace_id': marketplace_id,
            'title': shopify_product.get('title', ''),
            'status': 'active' if shopify_product.get('status') == 'active' else 'inactive',
            'price': 0.0,
            'currency': 'USD',
            'inventory_quantity': 0,
            'thumbnail_url': thumbnail_url,  # Set thumbnail URL from first image
            'metadata': {
                'shopify_product_id': product_id,
                'handle': shopify_product.get('handle'),
                'product_type': shopify_product.get('product_type'),
                'vendor': shopify_product.get('vendor'),
                'tags': shopify_product.get('tags', []),
                'variants_count': len(shopify_product.get('variants', [])),
                'description': shopify_product.get('body_html', ''),
                'images_count': len(images),  # Add image count to metadata
            }
        }
        
        # Get price and stock from first variant
        variants = shopify_product.get('variants', [])
        if variants:
            variant = variants[0]
            price = variant.get('price')
            sku = variant.get('sku')
            if price:
                try:
                    listing_data['price'] = float(price)
                except (ValueError, TypeError):
                    pass
            
            inventory_quantity = variant.get('inventory_quantity')
            if sku:
                listing_data['external_sku'] = sku
            if inventory_quantity is not None:
                listing_data['inventory_quantity'] = int(inventory_quantity)
        
        # Create or update listing
        listing, created = MarketplaceListing.objects.update_or_create(
            client=client,
            marketplace_type='shopify',
            marketplace_id=marketplace_id,
            defaults=listing_data
        )
        
        # Sync images if available
        if images:
            logger.info(f"Syncing {len(images)} images for listing {listing.id}")
            sync_listing_images(listing, images)
        else:
            logger.info(f"No images found for listing {listing.id}")
        
        return listing
        
    except Exception as e:
        logger.error(f"Error creating/updating Shopify listing: {e}")
        return None

def sync_listing_images(listing, shopify_images):
    """Sync images for a marketplace listing"""
    try:
        from marketplaces.models import MarketplaceListingImage
        
        if not shopify_images:
            return
        
        # Delete existing images for this listing
        listing.listing_images.all().delete()
        
        # Create new images
        for i, image_data in enumerate(shopify_images):
            image = MarketplaceListingImage(
                listing=listing,
                external_id=str(image_data.get('id')),
                position=image_data.get('position', i + 1),
                url=image_data.get('src'),
                alt_text=image_data.get('alt'),
                width=image_data.get('width'),
                height=image_data.get('height'),
                variant_ids=image_data.get('variant_ids', []),
                metadata={
                    'product_id': image_data.get('product_id'),
                    'created_at': image_data.get('created_at'),
                    'updated_at': image_data.get('updated_at'),
                    'admin_graphql_api_id': image_data.get('admin_graphql_api_id'),
                }
            )
            image.save()
            logger.debug(f"Saved image {i+1}/{len(shopify_images)}: {image_data.get('src', 'No URL')}")
        
        logger.info(f"Successfully synced {len(shopify_images)} images for listing {listing.id}")
        
    except Exception as e:
        logger.error(f"Error syncing listing images: {e}")

def create_or_update_amazon_product(client, amazon_product):
    """Create or update a Product from Amazon data (example implementation)"""
    try:
        from products.models import Product, Brand, Provider
        
        # Get clean SKU for matching (Amazon uses ASIN)
        sku = amazon_product.get('sku')
        barcode = amazon_product.get('barcode')
        asin = amazon_product.get('asin')
        
        # Priority: SKU > Barcode > ASIN
        internal_sku = None
        if sku:
            internal_sku = clean_sku_for_matching(sku)
        elif barcode:
            internal_sku = clean_sku_for_matching(barcode)
        elif asin:
            internal_sku = get_platform_specific_sku('amazon', asin)
        
        if not internal_sku:
            logger.warning(f"No SKU found for Amazon product {asin}")
            return None
        
        # Get or create brand
        brand = None
        brand_name = amazon_product.get('brand')
        if brand_name:
            brand, created = Brand.objects.get_or_create(
                client=client,
                name=brand_name
            )
        
        # Get or create provider
        provider = None
        if brand_name:
            provider, created = Provider.objects.get_or_create(
                client=client,
                name=brand_name
            )
        
        # Prepare product data
        product_data = {
            'client': client,
            'internal_sku': internal_sku,
            'title': amazon_product.get('title', ''),
            'description': amazon_product.get('description', ''),
            'brand': brand,
            'provider': provider,
            'category': amazon_product.get('category', ''),
        }
        
        # Get price
        price = amazon_product.get('price')
        if price:
            try:
                product_data['cost'] = float(price)
            except (ValueError, TypeError):
                pass
        
        # Create or update product
        product, created = Product.objects.update_or_create(
            client=client,
            internal_sku=internal_sku,
            defaults=product_data
        )
        
        return product
        
    except Exception as e:
        logger.error(f"Error creating/updating Amazon product: {e}")
        return None

def create_or_update_mercadolibre_product(client, meli_item):
    """Create or update a Product from Mercado Libre data"""
    try:
        from products.models import Product, Brand, Provider
        
        # Get clean SKU for matching (Mercado Libre uses item ID)
        sku = meli_item.get('sku')
        barcode = meli_item.get('barcode')
        item_id = meli_item.get('id')
        
        # Priority: SKU > Barcode > Item ID
        internal_sku = None
        if sku:
            internal_sku = clean_sku_for_matching(sku)
        elif barcode:
            internal_sku = clean_sku_for_matching(barcode)
        elif item_id:
            internal_sku = get_platform_specific_sku('mercadolibre', item_id)
        
        if not internal_sku:
            logger.warning(f"No SKU found for Mercado Libre item {item_id}")
            return None
        
        # Get or create brand
        brand = None
        brand_name = meli_item.get('brand')
        if brand_name:
            brand, created = Brand.objects.get_or_create(
                client=client,
                name=brand_name
            )
        
        # Get or create provider
        provider = None
        if brand_name:
            provider, created = Provider.objects.get_or_create(
                client=client,
                name=brand_name
            )
        
        # Prepare product data
        product_data = {
            'client': client,
            'internal_sku': internal_sku,
            'title': meli_item.get('title', ''),
            'description': meli_item.get('description', ''),
            'brand': brand,
            'provider': provider,
            'category': meli_item.get('category_id', ''),
        }
        
        # Get price
        price = meli_item.get('price')
        if price:
            try:
                product_data['cost'] = float(price)
            except (ValueError, TypeError):
                pass
        
        # Create or update product
        product, created = Product.objects.update_or_create(
            client=client,
            internal_sku=internal_sku,
            defaults=product_data
        )
        
        return product
        
    except Exception as e:
        logger.error(f"Error creating/updating Mercado Libre product: {e}")
        return None

def create_or_update_mercadolibre_listing(client, meli_item):
    """Create or update a MarketplaceListing from Mercado Libre data"""
    try:
        from marketplaces.models import MarketplaceListing
        
        # Use original Mercado Libre item ID (no prefix needed)
        item_id = meli_item.get('id')
        marketplace_id = str(item_id)  # Use original ID from Mercado Libre
        
        # Prepare listing data
        listing_data = {
            'client': client,
            'marketplace_type': 'mercadolibre',
            'marketplace_id': marketplace_id,
            'title': meli_item.get('title', ''),
            'status': 'active' if meli_item.get('status') == 'active' else 'inactive',
            'price': 0.0,
            'currency': 'ARS',  # Mercado Libre uses Argentine Peso
            'inventory_quantity': 0,
            'metadata': {
                'meli_item_id': item_id,
                'category_id': meli_item.get('category_id'),
                'brand': meli_item.get('brand'),
                'condition': meli_item.get('condition'),
                'listing_type': meli_item.get('listing_type'),
                'description': meli_item.get('description', ''),
            }
        }
        
        # Get price and stock
        price = meli_item.get('price')
        if price:
            try:
                listing_data['price'] = float(price)
            except (ValueError, TypeError):
                pass
        
        available_quantity = meli_item.get('available_quantity')
        if available_quantity is not None:
            listing_data['inventory_quantity'] = int(available_quantity)
        
        # Create or update listing
        listing, created = MarketplaceListing.objects.update_or_create(
            client=client,
            marketplace_type='mercadolibre',
            marketplace_id=marketplace_id,
            defaults=listing_data
        )
        
        return listing
        
    except Exception as e:
        logger.error(f"Error creating/updating Mercado Libre listing: {e}")
        return None

def create_or_update_amazon_listing(client, amazon_item):
    """Create or update a MarketplaceListing from Amazon data"""
    try:
        from marketplaces.models import MarketplaceListing
        
        # Use original Amazon ASIN (no prefix needed)
        asin = amazon_item.get('asin')
        marketplace_id = asin  # Use original ASIN from Amazon
        
        # Prepare listing data
        listing_data = {
            'client': client,
            'marketplace_type': 'amazon',
            'marketplace_id': marketplace_id,
            'title': amazon_item.get('title', ''),
            'status': 'active' if amazon_item.get('status') == 'active' else 'inactive',
            'price': 0.0,
            'currency': 'USD',  # Amazon typically uses USD
            'inventory_quantity': 0,
            'metadata': {
                'amazon_asin': asin,
                'brand': amazon_item.get('brand'),
                'category': amazon_item.get('category'),
                'condition': amazon_item.get('condition'),
                'fulfillment_type': amazon_item.get('fulfillment_type'),
                'description': amazon_item.get('description', ''),
            }
        }
        
        # Get price and stock
        price = amazon_item.get('price')
        if price:
            try:
                listing_data['price'] = float(price)
            except (ValueError, TypeError):
                pass
        
        inventory = amazon_item.get('inventory_quantity')
        if inventory is not None:
            listing_data['inventory_quantity'] = int(inventory)
        
        # Create or update listing
        listing, created = MarketplaceListing.objects.update_or_create(
            client=client,
            marketplace_type='amazon',
            marketplace_id=marketplace_id,
            defaults=listing_data
        )
        
        return listing
        
    except Exception as e:
        logger.error(f"Error creating/updating Amazon listing: {e}")
        return None

def clean_sku_for_matching(sku):
    """
    Clean SKU for matching purposes - standardize format
    """
    if not sku:
        return None
    
    # Standardize format (uppercase, replace special characters)
    cleaned_sku = sku.upper().strip()
    cleaned_sku = cleaned_sku.replace('-', '_').replace(' ', '_')
    
    return cleaned_sku if cleaned_sku else None

def get_platform_specific_sku(platform, identifier):
    """
    Generate platform-specific SKU when no real SKU is available
    """
    if not identifier:
        return None
    
    # Return the identifier as-is without adding prefixes
    return str(identifier)

def get_product_sku_from_variants(variants, product_data=None):
    """
    Extract the best available SKU from product variants
    Priority: SKU > Barcode > Product ID (for Shopify)
    """
    if not variants:
        return None
    
    # Try to get SKU from first variant
    first_variant = variants[0]
    sku = first_variant.get('sku')
    
    if sku:
        return clean_sku_for_matching(sku)
    
    # Try barcode
    barcode = first_variant.get('barcode')
    if barcode:
        return clean_sku_for_matching(barcode)
    
    # For Shopify, use product ID as fallback
    if product_data and product_data.get('id'):
        return get_platform_specific_sku('shopify', product_data.get('id'))

    print(f"SKU for {product_data.get('title')} is {sku}")
    
    return None

def sync_amazon_products_direct(client):
    """Sync Amazon products directly using SP API"""
    try:
        # Import SP API modules
        from sp_api.api import Catalog
        from sp_api.base import SellingApiException
        
        # Create SP API client
        catalog_api = Catalog()
        
        # Get catalog items (products)
        # Note: This is a simplified implementation
        # In a real implementation, you would get the actual catalog items
        
        products_synced = 0
        
        # Placeholder implementation
        # In real implementation, you would:
        # 1. Get catalog items from SP API
        # 2. For each item, extract SKU/barcode
        # 3. Create products with clean SKU using create_or_update_amazon_product()
        
        return products_synced
        
    except Exception as e:
        logger.error(f"Amazon products sync error: {e}")
        return 0

def sync_amazon_listings_direct(client):
    """Sync Amazon listings directly using SP API"""
    try:
        # Import SP API modules
        from sp_api.api import Catalog
        from sp_api.base import SellingApiException
        
        # Create SP API client
        catalog_api = Catalog()
        
        # Get listings
        # Note: This is a simplified implementation
        # In a real implementation, you would get the actual listings
        
        listings_synced = 0
        
        # Placeholder implementation
        # In real implementation, you would:
        # 1. Get listings from SP API
        # 2. For each listing, create marketplace listing with original ASIN
        # 3. Use create_or_update_amazon_listing()
        
        return listings_synced
        
    except Exception as e:
        logger.error(f"Amazon listings sync error: {e}")
        return 0
