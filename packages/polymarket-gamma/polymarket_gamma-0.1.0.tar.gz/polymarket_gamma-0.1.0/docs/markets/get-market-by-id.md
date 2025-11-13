# Get Market by ID

## HTTP Method
GET /markets/{id}

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | - | Market identifier (path parameter) |
| include_tag | boolean | No | - | Include tag information in response |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Market identifier |
| question | string | Yes | The market question |
| conditionId | string | No | Smart contract condition ID |
| slug | string | Yes | URL-friendly identifier |
| description | string | Yes | Market description |
| endDate | date-time | Yes | When market ends |
| active | boolean | Yes | Whether market is currently active |
| closed | boolean | Yes | Whether market is closed |
| outcomes | string | Yes | Possible outcomes |
| volume | string | Yes | Trading volume |
| liquidity | string | Yes | Available liquidity |
| categories | array | Yes | Associated categories |
| tags | array | Yes | Associated tags |

## Example Response
```json
{
  "id": "string",
  "question": "string",
  "conditionId": "string",
  "slug": "string",
  "description": "string",
  "endDate": "2023-11-07T05:31:56Z",
  "active": true,
  "closed": false,
  "outcomes": "string",
  "volume": "string",
  "liquidity": "string",
  "categories": [],
  "tags": []
}
```

## Additional Notes
- Returns comprehensive market data including pricing information, creation dates, associated events, and market metadata
- Error response: 404 Not found if market with specified ID does not exist
- Base URL: https://gamma-api.polymarket.com