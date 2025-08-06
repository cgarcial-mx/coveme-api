# API JSON Response Comparison: Product Listings

This document shows the JSON response structures for product listings from Amazon SP-API, Mercado Libre API, and Shopify API.

## 📦 Amazon SP-API Product Listings

### Endpoint
```
GET /catalog/v0/items
```

### Sample JSON Response
```json
{
  "items": [
    {
      "asin": "B08N5WRWNW",
      "summaries": [
        {
          "asin": "B08N5WRWNW",
          "title": "Echo Dot (4th Gen) | Smart speaker with Alexa | Charcoal",
          "brand": "Amazon",
          "mainImage": {
            "link": "https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg",
            "height": 1000,
            "width": 1000
          },
          "images": [
            {
              "link": "https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg",
              "height": 1000,
              "width": 1000
            }
          ],
          "features": [
            "Meet the Echo Dot - Our most popular smart speaker with Alexa"
          ],
          "productGroup": "CE",
          "partNumber": "B08N5WRWNW",
          "itemClassification": "BASE_PRODUCT",
          "browseClassification": {
            "displayGroupId": "2619525011",
            "displayGroupName": "Echo & Alexa"
          },
          "color": "Charcoal",
          "itemDimensions": {
            "height": {
              "value": 3.9,
              "unit": "IN"
            },
            "length": {
              "value": 3.9,
              "unit": "IN"
            },
            "width": {
              "value": 3.9,
              "unit": "IN"
            },
            "weight": {
              "value": 12.0,
              "unit": "OZ"
            }
          },
          "externalIds": [
            {
              "identifier": "B08N5WRWNW",
              "identifierType": "ASIN"
            }
          ],
          "manufacturerInfo": {
            "itemName": "Echo Dot (4th Gen)",
            "brand": "Amazon"
          },
          "vendorItemIdentifier": "B08N5WRWNW",
          "marketplaceId": "A1AM78C64UM0Y8"
        }
      ],
      "attributes": {
        "brand": {
          "value": "Amazon",
          "displayValue": "Amazon"
        },
        "color": {
          "value": "Charcoal",
          "displayValue": "Charcoal"
        },
        "model": {
          "value": "B08N5WRWNW",
          "displayValue": "B08N5WRWNW"
        }
      },
      "dimensions": [
        {
          "height": {
            "value": 3.9,
            "unit": "IN"
          },
          "length": {
            "value": 3.9,
            "unit": "IN"
          },
          "width": {
            "value": 3.9,
            "unit": "IN"
          },
          "weight": {
            "value": 12.0,
            "unit": "OZ"
          }
        }
      ],
      "identifiers": {
        "identifiers": [
          {
            "identifier": "B08N5WRWNW",
            "identifierType": "ASIN"
          }
        ],
        "marketplaceIds": [
          "A1AM78C64UM0Y8"
        ]
      },
      "images": [
        {
          "link": "https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg",
          "height": 1000,
          "width": 1000,
          "variant": "MAIN"
        }
      ],
      "productTypes": [
        {
          "productType": "CE",
          "displayName": "Consumer Electronics"
        }
      ],
      "salesRanks": [
        {
          "productCategoryId": "2619525011",
          "rank": 1,
          "title": "Echo & Alexa"
        }
      ],
      "summaries": [
        {
          "asin": "B08N5WRWNW",
          "title": "Echo Dot (4th Gen) | Smart speaker with Alexa | Charcoal",
          "brand": "Amazon",
          "mainImage": {
            "link": "https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg",
            "height": 1000,
            "width": 1000
          }
        }
      ]
    }
  ],
  "pagination": {
    "nextToken": "eyJzZWFyY2hBZnRlciI6IkI..."
  }
}
```

### Key Fields
- **asin**: Amazon Standard Identification Number
- **summaries**: Product information including title, brand, images
- **attributes**: Product attributes like color, brand, model
- **dimensions**: Physical dimensions and weight
- **images**: Product images with URLs and dimensions
- **salesRanks**: Sales ranking information

---

## 🛒 Mercado Libre API Product Listings

### Endpoint
```
GET /sites/{site_id}/search
```

### Sample JSON Response
```json
{
  "site_id": "MLM",
  "query": "smartphone",
  "paging": {
    "total": 1000,
    "offset": 0,
    "limit": 50,
    "primary_results": 1000
  },
  "results": [
    {
      "id": "MLM123456789",
      "site_id": "MLM",
      "title": "iPhone 13 Pro Max 256GB Sierra Blue",
      "seller": {
        "id": 123456,
        "nickname": "TecnoStore",
        "car_dealer": false,
        "real_estate_agency": false,
        "_tags": []
      },
      "price": 25000,
      "currency_id": "MXN",
      "available_quantity": 5,
      "sold_quantity": 12,
      "buying_mode": "buy_it_now",
      "listing_type_id": "gold_special",
      "stop_time": "2024-12-31T23:59:59.000-06:00",
      "condition": "new",
      "permalink": "https://articulo.mercadolibre.com.mx/MLM-123456789-iphone-13-pro-max-256gb-sierra-blue",
      "thumbnail": "https://http2.mlstatic.com/D_123456-MLM123456789_123456-O.jpg",
      "secure_thumbnail": "https://http2.mlstatic.com/D_123456-MLM123456789_123456-O.jpg",
      "pictures": [
        {
          "id": "123456-MLM123456789_123456",
          "url": "https://http2.mlstatic.com/D_123456-MLM123456789_123456-O.jpg",
          "secure_url": "https://http2.mlstatic.com/D_123456-MLM123456789_123456-O.jpg",
          "size": "500x500",
          "max_size": "1200x1200",
          "quality": ""
        }
      ],
      "video_id": null,
      "descriptions": [
        {
          "id": "MLM123456789-123456789"
        }
      ],
      "accepts_mercadopago": true,
      "non_mercado_pago_payment_methods": [],
      "shipping": {
        "mode": "me2",
        "free_methods": [
          {
            "id": 73328,
            "rule": {
              "default": true,
              "free_mode": "country",
              "free_shipping_flag": true
            }
          }
        ],
        "local_pick_up": true,
        "free_shipping": true,
        "store_pick_up": false
      },
      "seller_address": {
        "id": 123456,
        "comment": "",
        "address_line": "",
        "zip_code": "",
        "country": {
          "id": "MX",
          "name": "México"
        },
        "state": {
          "id": "MX-DIF",
          "name": "Distrito Federal"
        },
        "city": {
          "id": "MX-DIF-001",
          "name": "Álvaro Obregón"
        },
        "latitude": 19.4326,
        "longitude": -99.1332
      },
      "seller_contact": null,
      "location": {
        "address_line": "",
        "zip_code": "",
        "subneighborhood": null,
        "neighborhood": {
          "id": null,
          "name": ""
        },
        "city": {
          "id": "MX-DIF-001",
          "name": "Álvaro Obregón"
        },
        "state": {
          "id": "MX-DIF",
          "name": "Distrito Federal"
        },
        "country": {
          "id": "MX",
          "name": "México"
        },
        "latitude": 19.4326,
        "longitude": -99.1332
      },
      "attributes": [
        {
          "id": "BRAND",
          "name": "Marca",
          "value_id": "1234",
          "value_name": "Apple",
          "attribute_group_id": "OTHERS",
          "attribute_group_name": "Otros"
        },
        {
          "id": "MODEL",
          "name": "Modelo",
          "value_id": "5678",
          "value_name": "iPhone 13 Pro Max",
          "attribute_group_id": "OTHERS",
          "attribute_group_name": "Otros"
        }
      ],
      "variations": [
        {
          "id": 123456789,
          "price": 25000,
          "attribute_combinations": [
            {
              "id": "COLOR",
              "name": "Color",
              "value_id": "1234",
              "value_name": "Sierra Blue"
            },
            {
              "id": "STORAGE",
              "name": "Almacenamiento",
              "value_id": "5678",
              "value_name": "256 GB"
            }
          ],
          "available_quantity": 5,
          "sold_quantity": 12,
          "sale_terms": [],
          "picture_ids": [
            "123456-MLM123456789_123456"
          ],
          "catalog_product_id": "MLM123456789"
        }
      ],
      "status": "active",
      "sub_status": [],
      "tags": [
        "good_quality_picture",
        "good_quality_thumbnail",
        "immediate_payment",
        "cart_eligible"
      ],
      "warranty": "Garantía del vendedor",
      "catalog_product_id": "MLM123456789",
      "domain_id": "MLM-CELLPHONES",
      "parent_item_id": null,
      "differential_pricing": null,
      "deal_ids": [],
      "automatic_relist": false,
      "date_created": "2024-01-15T10:30:00.000-06:00",
      "last_updated": "2024-01-20T14:45:00.000-06:00",
      "health": 0.95,
      "catalog_listing": true,
      "channels": [
        "marketplace"
      ]
    }
  ],
  "secondary_results": [],
  "related_results": [],
  "sort": {
    "id": "relevance",
    "name": "Más relevantes"
  },
  "available_sorts": [
    {
      "id": "price_asc",
      "name": "Menor precio"
    },
    {
      "id": "price_desc",
      "name": "Mayor precio"
    },
    {
      "id": "relevance",
      "name": "Más relevantes"
    }
  ],
  "filters": [
    {
      "id": "category",
      "name": "Categorías",
      "type": "text",
      "values": [
        {
          "id": "MLM-CELLPHONES",
          "name": "Celulares y Teléfonos",
          "results": 1000
        }
      ]
    }
  ],
  "available_filters": [
    {
      "id": "BRAND",
      "name": "Marca",
      "type": "STRING",
      "values": [
        {
          "id": "1234",
          "name": "Apple",
          "results": 500
        }
      ]
    }
  ]
}
```

### Key Fields
- **id**: Mercado Libre product ID
- **title**: Product title
- **price**: Product price in local currency
- **seller**: Seller information
- **pictures**: Product images
- **attributes**: Product attributes and specifications
- **variations**: Product variants (color, size, etc.)
- **shipping**: Shipping information
- **location**: Geographic location

---

## 🛍️ Shopify API Product Listings

### Endpoint
```
GET /admin/api/{version}/products.json
```

### Sample JSON Response
```json
{
  "products": [
    {
      "id": 123456789,
      "title": "iPhone 13 Pro Max 256GB Sierra Blue",
      "body_html": "<p>Experience the latest iPhone with advanced features and stunning design.</p>",
      "vendor": "Apple Store",
      "product_type": "Electronics",
      "created_at": "2024-01-15T10:30:00-05:00",
      "handle": "iphone-13-pro-max-256gb-sierra-blue",
      "updated_at": "2024-01-20T14:45:00-05:00",
      "published_at": "2024-01-15T10:30:00-05:00",
      "template_suffix": null,
      "status": "active",
      "published_scope": "web",
      "tags": "iphone, smartphone, apple, 5g",
      "admin_graphql_api_id": "gid://shopify/Product/123456789",
      "variants": [
        {
          "id": 987654321,
          "product_id": 123456789,
          "title": "Sierra Blue / 256 GB",
          "price": "1299.00",
          "sku": "IPHONE13PM-256-SB",
          "position": 1,
          "inventory_policy": "deny",
          "compare_at_price": "1399.00",
          "fulfillment_service": "manual",
          "inventory_management": "shopify",
          "option1": "Sierra Blue",
          "option2": "256 GB",
          "option3": null,
          "created_at": "2024-01-15T10:30:00-05:00",
          "updated_at": "2024-01-20T14:45:00-05:00",
          "taxable": true,
          "barcode": "1234567890123",
          "grams": 240,
          "image_id": 444555666,
          "weight": 0.53,
          "weight_unit": "kg",
          "inventory_item_id": 111222333,
          "inventory_quantity": 25,
          "old_inventory_quantity": 25,
          "requires_shipping": true,
          "admin_graphql_api_id": "gid://shopify/ProductVariant/987654321"
        }
      ],
      "options": [
        {
          "id": 111222333,
          "product_id": 123456789,
          "name": "Color",
          "position": 1,
          "values": [
            "Sierra Blue",
            "Graphite",
            "Gold",
            "Silver"
          ]
        },
        {
          "id": 222333444,
          "product_id": 123456789,
          "name": "Storage",
          "position": 2,
          "values": [
            "128 GB",
            "256 GB",
            "512 GB",
            "1 TB"
          ]
        }
      ],
      "images": [
        {
          "id": 444555666,
          "product_id": 123456789,
          "position": 1,
          "created_at": "2024-01-15T10:30:00-05:00",
          "updated_at": "2024-01-20T14:45:00-05:00",
          "alt": "iPhone 13 Pro Max Sierra Blue",
          "width": 1200,
          "height": 1200,
          "src": "https://cdn.shopify.com/s/files/1/1234/5678/products/iphone13pm-sierra-blue.jpg",
          "variant_ids": [987654321],
          "admin_graphql_api_id": "gid://shopify/ProductImage/444555666"
        }
      ],
      "image": {
        "id": 444555666,
        "product_id": 123456789,
        "position": 1,
        "created_at": "2024-01-15T10:30:00-05:00",
        "updated_at": "2024-01-20T14:45:00-05:00",
        "alt": "iPhone 13 Pro Max Sierra Blue",
        "width": 1200,
        "height": 1200,
        "src": "https://cdn.shopify.com/s/files/1/1234/5678/products/iphone13pm-sierra-blue.jpg",
        "variant_ids": [987654321],
        "admin_graphql_api_id": "gid://shopify/ProductImage/444555666"
      },
      "seo": {
        "title": "iPhone 13 Pro Max 256GB Sierra Blue | Apple Store",
        "description": "Experience the latest iPhone with advanced features and stunning design. Available in Sierra Blue with 256GB storage."
      },
      "gift_card": false,
      "google_product_category": "Electronics > Mobile Phones",
      "google_shopping_google_product_category": "Electronics > Mobile Phones",
      "google_shopping_google_product_type": "Electronics > Mobile Phones",
      "google_shopping_google_product_title": "iPhone 13 Pro Max 256GB Sierra Blue",
      "google_shopping_google_product_description": "Experience the latest iPhone with advanced features and stunning design.",
      "google_shopping_google_product_condition": "new",
      "google_shopping_google_product_brand": "Apple",
      "google_shopping_google_product_gtin": "1234567890123",
      "google_shopping_google_product_mpn": "IPHONE13PM-256-SB",
      "google_shopping_google_product_additional_image_link": [
        "https://cdn.shopify.com/s/files/1/1234/5678/products/iphone13pm-sierra-blue-2.jpg"
      ],
      "google_shopping_google_product_additional_variant_attribute": [
        {
          "name": "Color",
          "value": "Sierra Blue"
        },
        {
          "name": "Storage",
          "value": "256 GB"
        }
      ],
      "metafields": [
        {
          "id": 111222333,
          "namespace": "custom",
          "key": "warranty",
          "value": "1 Year Limited Warranty",
          "type": "single_line_text_field",
          "created_at": "2024-01-15T10:30:00-05:00",
          "updated_at": "2024-01-20T14:45:00-05:00"
        }
      ],
      "collections": [
        {
          "id": 111222333,
          "handle": "smartphones",
          "title": "Smartphones",
          "updated_at": "2024-01-20T14:45:00-05:00",
          "body_html": "<p>Latest smartphones from top brands</p>",
          "published_at": "2024-01-15T10:30:00-05:00",
          "sort_order": "manual",
          "template_suffix": null,
          "admin_graphql_api_id": "gid://shopify/Collection/111222333"
        }
      ]
    }
  ]
}
```

### Key Fields
- **id**: Shopify product ID
- **title**: Product title
- **body_html**: Product description in HTML
- **vendor**: Product vendor/brand
- **product_type**: Product category
- **variants**: Product variants with pricing and inventory
- **options**: Product options (color, size, etc.)
- **images**: Product images with URLs and metadata
- **seo**: SEO information
- **metafields**: Custom product metadata
- **collections**: Associated collections

---

## 📊 Comparison Summary

| Feature | Amazon SP-API | Mercado Libre | Shopify |
|---------|---------------|---------------|---------|
| **Product ID** | ASIN | MLM ID | Shopify ID |
| **Title** | ✅ | ✅ | ✅ |
| **Description** | ✅ | ✅ | ✅ |
| **Price** | ❌ (via separate API) | ✅ | ✅ |
| **Images** | ✅ | ✅ | ✅ |
| **Variants** | ✅ | ✅ | ✅ |
| **Inventory** | ❌ (via separate API) | ✅ | ✅ |
| **Categories** | ✅ | ✅ | ✅ |
| **SEO Data** | ✅ | ✅ | ✅ |
| **Shipping** | ❌ | ✅ | ❌ |
| **Seller Info** | ❌ | ✅ | ❌ |
| **Location** | ❌ | ✅ | ❌ |
| **Reviews** | ❌ | ❌ | ❌ |

### Key Differences:

1. **Amazon SP-API**: Focuses on catalog data, requires separate APIs for pricing and inventory
2. **Mercado Libre**: Comprehensive marketplace data including seller and shipping info
3. **Shopify**: Complete e-commerce platform data with variants, options, and metafields

### Common Fields Across All APIs:
- Product ID
- Title
- Description
- Images
- Categories
- Variants/Options
- SEO information 