# Shopify Client Configuration Rules

This document outlines the rules and procedures for configuring clients and Shopify credentials through Django Admin.

## Overview

The Coveme API platform allows clients to connect their Shopify stores through the Django Admin interface. This configuration process involves two main steps:
1. Creating/Configuring a Client
2. Setting up Shopify Marketplace Credentials

## Client Configuration Rules

### 1. Client Creation and Management

#### Required Fields:
- **Name**: Company/client name (max 200 characters)
- **Tax ID**: Unique tax identification number (optional but recommended)
- **Subscription Plan**: Choose from Basic, Premium, or Enterprise
- **API Quota**: Default 10,000 requests (configurable)
- **Status**: Active, Inactive, or Suspended

#### Business Rules:
- Each client must have a unique tax ID
- Clients start with 'Active' status by default
- API quota is enforced based on subscription plan
- Suspended clients cannot access API endpoints

#### Admin Interface Location:
- Navigate to Django Admin → Clients → Clients
- Use the "Add Client" button to create new clients
- Use the list view to manage existing clients

### 2. Shopify Credentials Configuration

#### Prerequisites:
Before configuring Shopify credentials in Django Admin, ensure you have:
- A Shopify store (development or production)
- Admin access to the Shopify store
- API credentials from Shopify (see SHOPIFY_SELLERS_SETUP.md)

#### Required Shopify API Credentials:
1. **Shop URL**: Your store's domain (e.g., `my-store.myshopify.com`)
2. **Access Token**: Admin API access token from Shopify
3. **API Version**: Shopify API version (default: `2024-01`)

#### Configuration Steps in Django Admin:

##### Step 1: Access Marketplace Credentials
- Navigate to Django Admin → Clients → Client marketplace credentials
- Click "Add Client marketplace credentials"

##### Step 2: Select Client and Marketplace
- **Client**: Select the client from the dropdown
- **Marketplace Type**: Choose "Shopify" from the options
- **Marketplace Name**: Enter a descriptive name (e.g., "Main Store", "Test Store")

##### Step 3: Configure Credentials JSON
The credentials field requires a JSON object with the following structure:

```json
{
    "shop_url": "your-store.myshopify.com",
    "access_token": "your_shopify_access_token",
    "api_version": "2024-01"
}
```

**Important**: Replace the placeholder values with actual Shopify credentials.

##### Step 4: Configure Settings (Optional)
The settings field can include additional configuration:

```json
{
    "webhook_enabled": true,
    "sync_products": true,
    "sync_orders": true,
    "sync_customers": true,
    "rate_limit_delay": 0.5,
    "timeout": 30
}
```

##### Step 5: Webhook Configuration (Optional)
- **Webhook URL**: Enter the webhook endpoint URL for real-time updates
- Format: `https://your-domain.com/api/webhooks/shopify/`

##### Step 6: Save and Test
- Click "Save" to store the configuration
- The connection status will be set to "Disconnected" initially
- Use the test command to verify the connection

## Validation Rules

### Client Validation:
- Client name cannot be empty
- Tax ID must be unique across all clients
- Subscription plan must be one of the predefined choices
- API quota must be a positive integer

### Shopify Credentials Validation:
- Shop URL must be a valid Shopify domain (ending with `.myshopify.com`)
- Access token cannot be empty
- API version must be a valid Shopify API version
- Client can only have one Shopify configuration per marketplace type

### Security Rules:
- Credentials are stored in encrypted JSON format
- Access tokens should never be logged or exposed
- Failed connection attempts are logged with error details
- Connection status is automatically updated based on API responses

## Testing and Verification

### Manual Testing:
```bash
# Test specific client's Shopify connection
python manage.py test_shopify_api --client-id <client_id>

# Test all Shopify connections
python manage.py test_shopify_api --all-clients

# Debug mode with detailed output
python manage.py test_shopify_api --debug
```

### Connection Status Monitoring:
- **Connected**: API credentials are valid and working
- **Disconnected**: Credentials not tested or connection failed
- **Error**: API credentials are invalid or connection failed

### Error Handling:
- Failed connections are logged with detailed error messages
- Last error is stored in the `last_error` field
- Connection status is updated automatically after testing

## Best Practices

### Client Management:
1. Always verify client information before creating accounts
2. Use descriptive marketplace names for easy identification
3. Monitor API quota usage for each client
4. Regularly review and update client status

### Credential Security:
1. Never share or expose access tokens
2. Use environment variables for sensitive data in development
3. Regularly rotate Shopify access tokens
4. Monitor for unauthorized access attempts

### Configuration Management:
1. Test credentials immediately after configuration
2. Document any custom settings or webhook configurations
3. Keep backup of credential configurations
4. Monitor connection status regularly

## Troubleshooting

### Common Issues:

#### 1. Invalid Shop URL
- Ensure the URL ends with `.myshopify.com`
- Check for typos in the domain name
- Verify the store is active and accessible

#### 2. Invalid Access Token
- Verify the token is copied correctly from Shopify
- Check if the token has expired
- Ensure the app has the required permissions

#### 3. API Version Issues
- Use the latest stable API version
- Check Shopify's API documentation for version compatibility
- Update to newer versions when available

#### 4. Connection Timeout
- Check network connectivity
- Verify firewall settings
- Increase timeout settings if needed

### Debug Commands:
```bash
# Test with detailed output
python manage.py test_shopify_api --debug --client-id <client_id>

# Check specific API endpoints
python manage.py test_shopify_api --endpoint products --client-id <client_id>

# Validate credentials without making API calls
python manage.py test_shopify_api --validate-only --client-id <client_id>
```

## API Integration Rules

### Rate Limiting:
- Respect Shopify's rate limits (2 requests/second for REST API)
- Implement appropriate delays between requests
- Monitor rate limit headers in responses

### Error Handling:
- Implement retry logic for transient failures
- Log all API interactions for debugging
- Handle different HTTP status codes appropriately

### Data Synchronization:
- Sync products, orders, and customers based on client settings
- Implement incremental sync to minimize API usage
- Handle webhook notifications for real-time updates

## Compliance and Monitoring

### Data Protection:
- Ensure GDPR compliance for customer data
- Implement data retention policies
- Monitor data access and usage patterns

### Audit Trail:
- Log all configuration changes
- Track API usage and performance
- Monitor for suspicious activity

### Regular Maintenance:
- Review and update configurations monthly
- Test all connections regularly
- Update API versions as needed
- Monitor Shopify API changes and deprecations

## Support and Documentation

### Resources:
- Shopify API Documentation: https://shopify.dev/docs/api/admin
- Coveme API Documentation: See other docs in this folder
- Technical Support: Contact development team

### Escalation Process:
1. Check this documentation for common solutions
2. Review error logs and connection status
3. Test credentials manually
4. Contact technical support if issues persist

---

**Note**: This document should be updated whenever there are changes to the client configuration process or Shopify API requirements.
