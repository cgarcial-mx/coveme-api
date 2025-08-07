# Test Connection Feature for Marketplace Credentials

## Overview

This feature adds a "Test Connection" button to the Django admin interface for `ClientMarketplaceCredentials` that allows administrators to test the connectivity and authentication of marketplace API credentials directly from the admin panel.

## Features

- **Test Connection Button**: Available in the admin list view and detail view
- **Real-time Status Updates**: Connection status is automatically updated after testing
- **Error Handling**: Detailed error messages are displayed and stored
- **Visual Feedback**: Color-coded status indicators (green for connected, orange for disconnected, red for error)
- **Support for Multiple Marketplaces**: Amazon, Mercado Libre, and Shopify

## How to Use

### 1. Access the Admin Interface

Navigate to the Django admin interface and go to:
```
Admin > Clients > Client marketplace credentials
```

### 2. Test a Connection

1. Find the credential you want to test in the list
2. Click the "Test Connection" button in the "Test Connection" column
3. The system will attempt to authenticate with the marketplace API
4. You'll be redirected back to the detail view with a success or error message

### 3. View Results

- **Success**: The connection status will be updated to "Connected" (green)
- **Error**: The connection status will be updated to "Error" (red) with detailed error information

## Supported Marketplaces

### Amazon
- Tests Amazon SP API authentication
- Requires credentials: `lwa_app_id`, `lwa_client_secret`, `refresh_token`, `aws_access_key_id`, `aws_secret_access_key`, `role_arn`

### Mercado Libre
- Tests Mercado Libre API authentication
- Requires credentials: `access_token`, `refresh_token`, `client_id`, `client_secret`

### Shopify
- Tests Shopify API authentication
- Requires credentials: `shop_url`, `access_token`, `api_key`, `api_secret`

## Technical Implementation

### Files Modified/Created

1. **`clients/utils.py`**: Contains the test connection logic
2. **`clients/admin.py`**: Modified to add the test connection button and functionality
3. **`clients/static/clients/admin.css`**: Custom CSS for styling the admin interface

### Key Functions

- `test_marketplace_connection()`: Main function that routes to specific marketplace tests
- `test_amazon_connection()`: Tests Amazon SP API
- `test_mercadolibre_connection()`: Tests Mercado Libre API
- `test_shopify_connection()`: Tests Shopify API

### Admin Customization

The admin interface includes:
- Custom URL routing for the test connection action
- Color-coded status display
- Styled test connection button
- Organized fieldsets for better data presentation

## Error Handling

The system provides comprehensive error handling:
- Missing credentials
- API authentication failures
- Network connectivity issues
- Invalid credential formats

All errors are logged and displayed to the user with clear, actionable messages.

## Security Considerations

- Credentials are stored in the database as JSON (consider encryption for production)
- Test connections use the same credentials as the actual API calls
- No credentials are exposed in error messages
- All test operations are logged for audit purposes

## Future Enhancements

Potential improvements:
- Batch testing of multiple credentials
- Scheduled automatic testing
- Email notifications for connection failures
- More detailed API response information
- Support for additional marketplaces (eBay, Walmart, etc.)
