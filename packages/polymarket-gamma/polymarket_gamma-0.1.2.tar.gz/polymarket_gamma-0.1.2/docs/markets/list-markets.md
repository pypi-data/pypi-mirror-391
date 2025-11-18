# List Markets

## HTTP Method
GET /markets

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | minimum: 0 | Pagination limit |
| offset | integer | No | minimum: 0 | Pagination offset |
| order | string | No | - | Comma-separated list of fields to order by |
| ascending | boolean | No | - | Sort direction |
| id | array[int] | No | - | Filter by market IDs |
| slug | array[string] | No | - | Filter by market slugs |
| clob_token_ids | array[string] | No | - | Filter by CLOB token IDs |
| condition_ids | array[string] | No | - | Filter by condition IDs |
| market_maker_address | array[string] | No | - | Filter by market maker addresses |
| liquidity_num_min | number | No | - | Minimum liquidity |
| liquidity_num_max | number | No | - | Maximum liquidity |
| volume_num_min | number | No | - | Minimum volume |
| volume_num_max | number | No | - | Maximum volume |
| start_date_min | string | No | format: date-time | Minimum start date |
| start_date_max | string | No | format: date-time | Maximum start date |
| end_date_min | string | No | format: date-time | Minimum end date |
| end_date_max | string | No | format: date-time | Maximum end date |
| tag_id | integer | No | - | Filter by tag ID |
| related_tags | boolean | No | - | Include related tags |
| cyom | boolean | No | - | CYOM filter |
| uma_resolution_status | string | No | - | UMA resolution status filter |
| game_id | string | No | - | Filter by game ID |
| sports_market_types | array[string] | No | - | Filter by sports market types |
| rewards_min_size | number | No | - | Minimum reward size |
| question_ids | array[string] | No | - | Filter by question IDs |
| include_tag | boolean | No | - | Include tags |
| closed | boolean | No | - | Filter closed markets |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Market identifier |
| question | string | Yes | Market question |
| conditionId | string | No | Condition identifier |
| slug | string | Yes | URL slug |
| endDate | date-time | Yes | Market end date |
| startDate | date-time | Yes | Market start date |
| category | string | Yes | Market category |
| active | boolean | Yes | Market active status |
| closed | boolean | Yes | Market closed status |
| marketType | string | Yes | Type of market |
| liquidity | string | Yes | Liquidity amount |
| volume | string | Yes | Trading volume |
| volumeNum | number | Yes | Numeric volume |
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
| categories | array[Category] | Yes | Market categories |
| tags | array[Tag] | Yes | Market tags |
| events | array[Event] | Yes | Associated events |
| imageOptimized | ImageOptimization | Yes | Optimized image data |
| iconOptimized | ImageOptimization | Yes | Optimized icon data |

## Example Response
```json
[
  {
    "id": "string",
    "question": "string",
    "conditionId": "string",
    "slug": "string",
    "endDate": "2023-11-07T05:31:56Z",
    "active": true,
    "closed": true,
    "marketType": "string",
    "liquidity": "string",
    "volume": "string",
    "volumeNum": 123,
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
    "events": []
  }
]
```

## Additional Notes
- All parameters are optional for filtering and pagination
- Response includes comprehensive market data including financial metrics, timing information, and relationships
- Supports ordering by multiple fields using the `order` parameter
- Base URL: https://gamma-api.polymarket.com