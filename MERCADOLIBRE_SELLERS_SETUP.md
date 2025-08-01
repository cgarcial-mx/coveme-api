# MercadoLibre Sellers Setup Guide

This guide will help you set up MercadoLibre API integration for your application. Follow these steps to configure authentication, test the API, and start using MercadoLibre's marketplace features.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [MercadoLibre Developer Account Setup](#mercadolibre-developer-account-setup)
3. [Application Registration](#application-registration)
4. [Environment Configuration](#environment-configuration)
5. [Authentication Setup](#authentication-setup)
6. [Testing the Integration](#testing-the-integration)
7. [API Endpoints Overview](#api-endpoints-overview)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## 🔧 Prerequisites

Before starting, ensure you have:

- A MercadoLibre seller account
- Access to MercadoLibre's developer portal
- Python 3.8+ installed
- Django project set up
- `requests` library installed

## 🏢 MercadoLibre Developer Account Setup

### 1. Create Developer Account

1. Go to [MercadoLibre Developers](https://developers.mercadolibre.com.mx/)
2. Click "Sign Up" or "Create Account"
3. Use your existing MercadoLibre account or create a new one
4. Complete the developer registration process

### 2. Access Developer Portal

1. Log in to the [Developer Portal](https://developers.mercadolibre.com.mx/)
2. Navigate to "My Applications" section
3. Familiarize yourself with the dashboard

## 📱 Application Registration

### 1. Create New Application

1. In the Developer Portal, click "Create Application"
2. Fill in the application details:
   - **Application Name**: Your app name (e.g., "Forttuna Integration")
   - **Description**: Brief description of your application
   - **Platform**: Web Application
   - **Redirect URI**: `https://forttuna.azurewebsites.net/app/main/salechannel/authorization`

### 2. Get Application Credentials

After creating the application, you'll receive:

- **App ID**: Your application identifier
- **Client Secret**: Your application secret key
- **User ID**: Your MercadoLibre user ID

### 3. Configure Application Settings

1. Set the **Redirect URI** to your application's authorization callback URL
2. Configure the **Site ID** (MLM for Mexico)
3. Set appropriate **scopes** for your application:
   - `offline_access`: For long-term access
   - `read`: For reading data
   - `write`: For creating/updating data

## ⚙️ Environment Configuration

### 1. Environment Variables

Create or update your `.env.local` file with the following variables:

```bash
# MercadoLibre Configuration
MERCADOLIBRE_URL=https://api.mercadolibre.com
MERCADOLIBRE_SECRET_KEY=your_secret_key_here
MERCADOLIBRE_APP_ID=your_app_id_here
MERCADOLIBRE_USER=your_user_id_here
MERCADOLIBRE_SITE=MLM
MERCADOLIBRE_REDIRECT_URI=https://forttuna.azurewebsites.net/app/main/salechannel/authorization
```

### 2. Production Environment

For production, create `.env.production` with the same variables but production-specific values:

```bash
# MercadoLibre Configuration (Production)
MERCADOLIBRE_URL=https://api.mercadolibre.com
MERCADOLIBRE_SECRET_KEY=your_production_secret_key
MERCADOLIBRE_APP_ID=your_production_app_id
MERCADOLIBRE_USER=your_production_user_id
MERCADOLIBRE_SITE=MLM
MERCADOLIBRE_REDIRECT_URI=https://forttuna.azurewebsites.net/app/main/salechannel/authorization
```

## 🔐 Authentication Setup

### 1. OAuth 2.0 Flow

MercadoLibre uses OAuth 2.0 for authentication. The integration supports:

- **Client Credentials Flow**: For server-to-server communication
- **Authorization Code Flow**: For user-specific operations

### 2. Access Token Management

The application automatically handles:
- Token generation using client credentials
- Token refresh when needed
- Secure token storage

### 3. Authentication Scopes

Configure these scopes based on your needs:

| Scope | Description | Required |
|-------|-------------|----------|
| `offline_access` | Long-term access without user interaction | ✅ |
| `read` | Read user data, listings, orders | ✅ |
| `write` | Create/update listings, manage orders | ✅ |

## 🧪 Testing the Integration

### 1. Basic Authentication Test

Test if your credentials are working:

```bash
python manage.py test_meli_api --auth
```

Expected output:
```
🔐 Testing MercadoLibre API Authentication...
✅ Access token obtained successfully
✅ API connection established successfully!
```

### 2. Full API Test

Test all API endpoints:

```bash
python manage.py test_meli_api --full
```

This will test:
- Authentication
- User information
- Categories
- Search functionality

### 3. Listings Test

Test listings consumption:

```bash
python manage.py test_meli_api --listings
```

This will:
- Retrieve your user listings
- Test marketplace search
- Get item details

### 4. Orders Test

Test orders functionality:

```bash
python manage.py test_meli_api --orders
```

This will:
- Retrieve recent orders
- Get order details
- Test order management

### 5. Debug Mode

For troubleshooting, use debug mode:

```bash
python manage.py test_meli_api --listings --debug
```

This provides detailed information about:
- API requests and responses
- Authentication flow
- Error details

## 📡 API Endpoints Overview

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/oauth/token` | POST | Get access token | Client credentials |
| `/users/{id}` | GET | Get user information | Bearer token |
| `/users/{id}/items/search` | GET | Get user listings | Bearer token |
| `/sites/{site}/categories` | GET | Get categories | Bearer token |
| `/sites/{site}/search` | GET | Search items | Bearer token |
| `/items/{id}` | GET | Get item details | Public/Bearer |
| `/my/received_orders/search` | GET | Get orders | Bearer token |

### Response Formats

#### User Information
```json
{
  "id": 337038705,
  "nickname": "USER_NICKNAME",
  "registration_date": "2020-01-01T00:00:00.000-04:00",
  "country_id": "ML",
  "address": {
    "city": "City Name",
    "state": "State Name"
  }
}
```

#### Item Listing
```json
{
  "id": "MLM1234567890",
  "title": "Product Title",
  "price": 100.00,
  "currency_id": "MXN",
  "condition": "new",
  "status": "active",
  "available_quantity": 10,
  "sold_quantity": 5
}
```

#### Order Information
```json
{
  "id": 123456789,
  "status": "paid",
  "total_amount": 150.00,
  "currency_id": "MXN",
  "date_created": "2024-01-01T00:00:00.000-04:00",
  "buyer": {
    "id": 123456,
    "nickname": "BUYER_NICKNAME"
  }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors (401/403)

**Symptoms:**
- "unauthorized" error messages
- 401 or 403 status codes

**Solutions:**
- Verify App ID and Secret Key are correct
- Check if the application is properly registered
- Ensure redirect URI matches exactly
- Verify user ID is correct

#### 2. Search API Failures

**Symptoms:**
- Search endpoints returning 401/403
- No results from search

**Solutions:**
- Use authentication for search endpoints
- Verify site ID (MLM for Mexico)
- Check search parameters

#### 3. Rate Limiting

**Symptoms:**
- 429 status codes
- "Too many requests" errors

**Solutions:**
- Implement request throttling
- Add delays between requests
- Use pagination for large datasets

#### 4. Network Issues

**Symptoms:**
- Connection timeouts
- DNS resolution errors

**Solutions:**
- Check internet connectivity
- Verify API URL is correct
- Check firewall settings

### Debug Commands

Use these commands for troubleshooting:

```bash
# Test basic connectivity
python manage.py test_meli_api --auth --debug

# Test specific functionality
python manage.py test_meli_api --listings --debug

# Check environment variables
python manage.py test_meli_api --auth
```

### Error Codes Reference

| Error Code | Description | Solution |
|------------|-------------|----------|
| 401 | Unauthorized | Check credentials and authentication |
| 403 | Forbidden | Verify permissions and scopes |
| 404 | Not Found | Check endpoint URL and parameters |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Contact MercadoLibre support |

## 📚 Best Practices

### 1. Security

- **Never commit credentials** to version control
- Use environment variables for sensitive data
- Implement proper token storage and refresh
- Use HTTPS for all API communications

### 2. Performance

- Implement request caching where appropriate
- Use pagination for large datasets
- Add request throttling to avoid rate limits
- Monitor API response times

### 3. Error Handling

- Implement comprehensive error handling
- Log API errors for debugging
- Provide user-friendly error messages
- Implement retry logic for transient failures

### 4. Data Management

- Store only necessary data locally
- Implement data synchronization
- Handle data conflicts gracefully
- Maintain data consistency

### 5. Monitoring

- Monitor API usage and limits
- Track authentication failures
- Monitor response times
- Set up alerts for critical errors

## 🔄 Integration Workflow

### 1. Initial Setup

1. Register application in MercadoLibre Developer Portal
2. Configure environment variables
3. Test authentication
4. Verify API access

### 2. Data Synchronization

1. Retrieve user listings
2. Sync marketplace data
3. Update local inventory
4. Handle order updates

### 3. Ongoing Operations

1. Monitor API health
2. Handle token refresh
3. Process new orders
4. Update listings as needed

## 📞 Support

### MercadoLibre Resources

- [Developer Documentation](https://developers.mercadolibre.com.mx/)
- [API Reference](https://developers.mercadolibre.com.mx/es_ar/items-y-busquedas)
- [Authentication Guide](https://developers.mercadolibre.com.mx/es_ar/autenticacion-y-autorizacion)
- [Support Forum](https://developers.mercadolibre.com.mx/es_ar/community)

### Application Support

For issues with this integration:
1. Check the troubleshooting section
2. Use debug mode for detailed information
3. Review error logs
4. Contact your development team

## 📝 Changelog

### Version 1.0.0
- Initial MercadoLibre integration
- OAuth 2.0 authentication
- Basic API endpoints support
- Testing framework
- Documentation

---

**Note**: This setup guide is specific to MercadoLibre Mexico (MLM). For other countries, adjust the site ID and endpoints accordingly. 