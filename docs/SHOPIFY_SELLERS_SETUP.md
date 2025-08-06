# Shopify API Setup Guide

This guide will help you set up Shopify API integration for your project.

## Prerequisites

- A Shopify store (can be a development store)
- Admin access to your Shopify store
- Python environment with the required dependencies

## Step 1: Create a Shopify Private App

1. **Log in to your Shopify Admin**
   - Go to your Shopify store admin panel
   - Navigate to `Apps` → `Develop apps`

2. **Create a new private app**
   - Click `Create an app`
   - Enter a name for your app (e.g., "Coveme API Integration")
   - Enter your email address
   - Click `Create app`

3. **Configure API permissions**
   - In your app settings, go to `Configuration` → `Admin API access scopes`
   - Select the following permissions:
     - `read_products` - To access product information
     - `read_orders` - To access order information
     - `read_customers` - To access customer information
     - `read_inventory` - To access inventory information
   - Click `Save`

4. **Generate API credentials**
   - Go to `API credentials` tab
   - Click `Install app` to generate the access token
   - Copy the `Admin API access token` (this is your `SHOPIFY_ACCESS_TOKEN`)

## Step 2: Configure Environment Variables

1. **Create or update your `.env.local` file**
   ```bash
   # Shopify Configuration
   SHOPIFY_SHOP_URL=your-store.myshopify.com
   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
   SHOPIFY_API_VERSION=2024-01
   ```

2. **Replace the placeholder values:**
   - `SHOPIFY_SHOP_URL`: Your store's domain (e.g., `my-store.myshopify.com`)
   - `SHOPIFY_ACCESS_TOKEN`: The access token from step 1
   - `SHOPIFY_API_VERSION`: API version (default: `2024-01`)

## Step 3: Test the Integration

### Basic Authentication Test
```bash
python manage.py test_shopify_api
```

### Full API Test
```bash
python manage.py test_shopify_api --full
```

### Products/Listings Test
```bash
python manage.py test_shopify_api --listings
```

### Orders Test
```bash
python manage.py test_shopify_api --orders
```

### Customers Test
```bash
python manage.py test_shopify_api --customers
```

### Webhooks Test
```bash
python manage.py test_shopify_api --webhook
```

### Debug Mode (with detailed responses)
```bash
python manage.py test_shopify_api --full --debug
```

## API Endpoints Tested

The test script validates the following Shopify API endpoints:

### Core APIs
- **Shop Info**: `/admin/api/{version}/shop.json`
- **Products**: `/admin/api/{version}/products.json`
- **Orders**: `/admin/api/{version}/orders.json`
- **Customers**: `/admin/api/{version}/customers.json`

### Product Details
- **Product Details**: `/admin/api/{version}/products/{id}.json`
- **Product Variants**: `/admin/api/{version}/products/{id}/variants.json`
- **Product Images**: `/admin/api/{version}/products/{id}/images.json`

### Order Details
- **Order Details**: `/admin/api/{version}/orders/{id}.json`

### Customer Details
- **Customer Details**: `/admin/api/{version}/customers/{id}.json`

### Webhooks
- **Webhooks List**: `/admin/api/{version}/webhooks.json`

## Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Check if your `SHOPIFY_ACCESS_TOKEN` is correct
   - Verify the token hasn't expired
   - Ensure the app is properly installed

2. **403 Forbidden Error**
   - Check if your app has the required permissions
   - Verify the API scopes are correctly set

3. **404 Not Found Error**
   - Check if your `SHOPIFY_SHOP_URL` is correct
   - Ensure the shop domain is valid (should end with `.myshopify.com`)

4. **API Version Issues**
   - Check if the API version is supported
   - Update to a newer version if needed

### Debug Mode

Use the `--debug` flag to get detailed information about API requests and responses:

```bash
python manage.py test_shopify_api --debug
```

This will show:
- Request URLs
- Request headers
- Response status codes
- Response headers
- Response body (first 500 characters)

## API Documentation

- **Shopify Admin API**: https://shopify.dev/docs/api/admin
- **API Reference**: https://shopify.dev/docs/api/admin-rest
- **Authentication**: https://shopify.dev/docs/api/admin-rest/getting-started#authentication

## Rate Limits

Shopify API has rate limits:
- **REST Admin API**: 2 requests per second per app
- **GraphQL Admin API**: 1,000 cost points per second per app

The test script respects these limits by using appropriate delays between requests.

## Security Notes

- Keep your access token secure and never commit it to version control
- Use environment variables for sensitive data
- Regularly rotate your access tokens
- Monitor your app's API usage in the Shopify admin

## Next Steps

After successful testing:

1. **Implement data synchronization**
   - Set up regular product sync
   - Implement order processing
   - Add customer data management

2. **Add webhook support**
   - Configure webhooks for real-time updates
   - Handle order notifications
   - Process inventory changes

3. **Error handling**
   - Implement retry logic for failed requests
   - Add logging for API interactions
   - Handle rate limiting gracefully

4. **Monitoring**
   - Set up API usage monitoring
   - Track sync performance
   - Monitor for API changes and deprecations 