# Get Market by Slug

## HTTP Method
GET /markets/slug/{slug}

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| slug | string | Yes | - | The unique slug identifier for the market (path parameter) |
| include_tag | boolean | No | - | Include tag information in response |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Market identifier |
| question | string | Yes | The market question |
| conditionId | string | No | Smart contract condition ID |
| slug | string | No | URL-friendly identifier |
| description | string | Yes | Market description |
| endDate | date-time | Yes | When market ends |
| startDate | date-time | Yes | Market start date |
| active | boolean | Yes | Whether market is currently active |
| closed | boolean | Yes | Whether market is closed |
| marketType | string | Yes | Type of market |
| outcomes | string | Yes | Possible outcomes |
| volume | string | Yes | Trading volume |
| volumeNum | number | Yes | Numeric volume |
| liquidity | string | Yes | Available liquidity |
| liquidityNum | number | Yes | Numeric liquidity |
| volume24hr | number | Yes | 24-hour volume |
| volume1wk | number | Yes | 1-week volume |
| volume1mo | number | Yes | 1-month volume |
| volume1yr | number | Yes | 1-year volume |
| lastTradePrice | number | Yes | Last trade price |
| bestBid | number | Yes | Best bid price |
| bestAsk | number | Yes | Best ask price |
| createdAt | date-time | Yes | Creation timestamp |
| updatedAt | date-time | Yes | Last update timestamp |
| closedTime | string | Yes | Closure timestamp |
| categories | array[Category] | Yes | Associated categories |
| tags | array[Tag] | Yes | Associated tags |
| events | array[Event] | Yes | Associated events |
| imageOptimized | ImageOptimization | Yes | Optimized image data |
| iconOptimized | ImageOptimization | Yes | Optimized icon data |

## Example Response
```json
{
  "id": "string",
  "question": "string",
  "conditionId": "string",
  "slug": "string",
  "description": "string",
  "endDate": "2023-11-07T05:31:56Z",
  "startDate": "2023-11-07T05:31:56Z",
  "active": true,
  "closed": false,
  "marketType": "string",
  "outcomes": "string",
  "volume": "string",
  "volumeNum": 123,
  "liquidity": "string",
  "liquidityNum": 123,
  "volume24hr": 123,
  "volume1wk": 123,
  "volume1mo": 123,
  "volume1yr": 123,
  "lastTradePrice": 123,
  "bestBid": 123,
  "bestAsk": 123,
  "createdAt": "2023-11-07T05:31:56Z",
  "updatedAt": "2023-11-07T05:31:56Z",
  "closedTime": "string",
  "categories": [],
  "tags": [],
  "events": [],
  "imageOptimized": {},
  "iconOptimized": {}
}
```

## Additional Notes
- Returns extensive trading metadata, price history, order book settings, and related event information for comprehensive market analysis
- The response includes 100+ properties providing complete market information
- Error response: 404 Not found if market with specified slug doesn't exist
- Base URL: https://gamma-api.polymarket.com