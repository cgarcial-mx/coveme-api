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
            
    except Exception as e:
        return False, f"Amazon connection test error: {str(e)}"

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
            
    except Exception as e:
        return False, f"Mercado Libre connection test error: {str(e)}"

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
            
    except Exception as e:
        return False, f"Shopify connection test error: {str(e)}"
