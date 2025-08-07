# Database Schema

This document outlines the database schema for the application, including all tables, their columns, and their relationships.

## Entities

The following are the main entities of the application:

- **Product:** Represents a product.
- **Brand:** Represents a brand.
- **Subbrand:** Represents a sub-brand.
- **Provider:** Represents a provider.
- **ProductPriceHistory:** Records the price history of a product.
- **ProductTracing:** Represents the tracing information of a product.
- **ProductTracingHistory:** Records the tracing history of a product.
- **MeLiOrder:** Represents an order from Mercado Libre.
- **UserBrand:** Associates a user with a brand.
- **UserProvider:** Associates a user with a provider.
- **Mojoneta:** Represents a "mojoneta."
- **SaleChannel:** Represents a sale channel.
- **User:** Represents a user.

## Table Definitions

The following is a detailed description of each table in the database:

### `Products`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the product. |
| `MeliProductId` | `string` | Required | The product's ID on Mercado Libre. |
| `Name` | `string` | Required | The name of the product. |
| `Sku` | `string` | | The product's stock keeping unit. |
| `Cost` | `decimal` | | The cost of the product. |
| `Thumbnail` | `string` | | A URL to a thumbnail image of the product. |
| `Details` | `string` | | A detailed description of the product. |
| `SaleChannelId` | `int` | Foreign Key | The ID of the sale channel for the product. |
| `Price` | `decimal` | | The price of the product. |
| `SoldQuantity` | `double` | Nullable | The number of units sold. |
| `AvailableQuantity` | `double` | Nullable | The number of units available. |
| `Status` | `string` | | The status of the product. |
| `IsFulfillment` | `bool` | | Whether the product is fulfilled by the marketplace. |
| `ListingFee` | `double` | | The fee for listing the product. |
| `CategoryName` | `string` | | The name of the product's category. |
| `OfficialStoreName` | `string` | | The name of the official store for the product. |
| `ShipmentFee` | `double` | | The fee for shipping the product. |
| `Brand` | `string` | | The brand of the product. |
| `SubBrand` | `string` | | The sub-brand of the product. |
| `ProviderName` | `string` | | The name of the provider of the product. |
| `CostWithDiscount` | `decimal` | Nullable | The cost of the product with a discount. |
| `IsIvaIncluded` | `bool` | | Whether the price includes IVA. |
| `ListingTypeName` | `string` | | The name of the listing type. |
| `Barcode` | `string` | | The product's barcode. |
| `PeriodTotalSales` | `int` | Nullable | The total sales for the period. |
| `UtilityPercentage` | `double` | Nullable | The utility percentage for the product. |
| `BestPrice` | `bool` | | Whether the product has the best price. |
| `HasTracingProducts` | `bool` | | Whether the product has tracing products. |
| `PriceDifference` | `decimal` | Nullable | The difference in price. |
| `BrandId` | `long` | Foreign Key, Nullable | The ID of the brand for the product. |
| `SubBrandId` | `long` | Foreign Key, Nullable | The ID of the sub-brand for the product. |
| `ProviderId` | `long` | Foreign Key, Nullable | The ID of the provider for the product. |
| `IsSupermarket` | `bool` | | Whether the product is a supermarket product. |

### `Brands`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the brand. |
| `Name` | `string` | Required | The name of the brand. |

### `Subbrands`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the sub-brand. |
| `Name` | `string` | Required | The name of the sub-brand. |
| `BrandId` | `long` | Foreign Key | The ID of the brand for the sub-brand. |

### `Providers`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the provider. |
| `Name` | `string` | Required | The name of the provider. |
| `Email` | `string` | | The email of the provider. |

### `ProductPriceHistory`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the price history record. |
| `PreviousPrice` | `decimal` | | The previous price of the product. |
| `NewPrice` | `decimal` | | The new price of the product. |
| `TotalSales` | `double` | Nullable | The total sales for the product. |
| `Utility` | `double` | Nullable | The utility for the product. |
| `Conversion` | `double` | Nullable | The conversion rate for the product. |
| `MarketShare` | `double` | Nullable | The market share for the product. |
| `ProductId` | `long` | Foreign Key | The ID of the product. |

### `ProductTracing`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the tracing record. |
| `LastCheckedPrice` | `decimal` | | The last checked price of the product. |
| `MeliProductId` | `string` | | The product's ID on Mercado Libre. |
| `Name` | `string` | | The name of the product. |
| `Thumbnail` | `string` | | A URL to a thumbnail image of the product. |
| `Permalink` | `string` | | A URL to the product's page. |
| `SellerName` | `string` | | The name of the seller. |
| `Sales` | `int` | | The number of sales. |
| `Category` | `string` | | The category of the product. |
| `ProductId` | `long` | Foreign Key | The ID of the product. |
| `ListingType` | `string` | | The listing type of the product. |
| `Status` | `string` | | The status of the product. |
| `IsFulfillment` | `bool` | | Whether the product is fulfilled by the marketplace. |
| `Level` | `int` | | The level of the product. |
| `PowerSellerStatus` | `string` | | The power seller status of the seller. |
| `Inventory` | `double` | Nullable | The inventory of the product. |
| `SellerId` | `string` | | The ID of the seller. |

### `ProductTracingHistory`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the tracing history record. |
| `Sales` | `int` | Nullable | The number of sales. |
| `Inventory` | `double` | Nullable | The inventory of the product. |
| `Price` | `decimal` | | The price of the product. |
| `ProductTracingId` | `long` | Foreign Key | The ID of the product tracing record. |

### `MeLiOrders`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the order. |
| `LogisticType` | `string` | | The logistic type for the order. |
| `SaleQuantity` | `double` | | The quantity of the sale. |
| `SalePrice` | `decimal` | | The price of the sale. |
| `Sku` | `string` | | The product's stock keeping unit. |
| `IsVariation` | `bool` | | Whether the order is for a variation. |
| `SaleFee` | `decimal` | | The fee for the sale. |
| `Status` | `string` | | The status of the order. |
| `Tags` | `string` | | The tags for the order. |
| `ProductName` | `string` | | The name of the product. |
| `VariationsAttributes` | `string` | | The attributes of the variations. |
| `ItemId` | `string` | | The ID of the item. |
| `OrderId` | `string` | | The ID of the order. |
| `OrderCreationDateTime` | `DateTime` | | The date and time the order was created. |
| `Cost` | `decimal` | Nullable | The cost of the order. |
| `ShipmentFee` | `double` | Nullable | The fee for shipping the order. |
| `ProductId` | `long` | Foreign Key, Nullable | The ID of the product. |

### `UserBrands`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the user-brand association. |
| `UserId` | `long` | Foreign Key | The ID of the user. |
| `BrandId` | `long` | Foreign Key | The ID of the brand. |

### `UserProviders`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the user-provider association. |
| `UserId` | `long` | Foreign Key | The ID of the user. |
| `ProviderId` | `long` | Foreign Key | The ID of the provider. |

### `Mojonetas`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `int` | Primary Key | Unique identifier for the mojoneta. |
| `name` | `string` | | The name of the mojoneta. |

### `SaleChannels`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `int` | Primary Key | Unique identifier for the sale channel. |

### `Users`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `Id` | `long` | Primary Key | Unique identifier for the user. |
