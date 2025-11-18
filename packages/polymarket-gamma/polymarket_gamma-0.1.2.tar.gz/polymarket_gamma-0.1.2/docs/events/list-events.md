# List Events

## HTTP Method
GET /events

## Base URL
https://gamma-api.polymarket.com

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | false | min: 0 | Maximum number of results to return |
| offset | integer | false | min: 0 | Pagination offset for results |
| order | string | false | Comma-separated list of fields | Fields to order results by |
| ascending | boolean | false | - | Sort direction (true for ascending) |
| id | array[integer] | false | - | Filter by specific event IDs |
| slug | array[string] | false | - | Filter by specific event slugs |
| tag_id | integer | false | - | Filter by tag ID |
| exclude_tag_id | array[integer] | false | - | Exclude events with these tag IDs |
| related_tags | boolean | false | - | Include related tags in response |
| featured | boolean | false | - | Filter for featured events only |
| cyom | boolean | false | - | Filter for CYOM (Create Your Own Market) events |
| include_chat | boolean | false | - | Include chat data in response |
| include_template | boolean | false | - | Include template data in response |
| recurrence | string | false | - | Filter by recurrence type |
| closed | boolean | false | - | Filter for closed events only |
| start_date_min | date-time | false | - | Minimum start date filter (ISO 8601 format) |
| start_date_max | date-time | false | - | Maximum start date filter (ISO 8601 format) |
| end_date_min | date-time | false | - | Minimum end date filter (ISO 8601 format) |
| end_date_max | date-time | false | - | Maximum end date filter (ISO 8601 format) |

## Response Schema
Returns an array of Event objects with the following structure:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | false | Event identifier |
| ticker | string | true | Event ticker symbol |
| slug | string | true | Unique slug identifier |
| title | string | true | Event title |
| subtitle | string | true | Event subtitle |
| description | string | true | Event description |
| startDate | date-time | true | Event start date |
| endDate | date-time | true | Event end date |
| creationDate | date-time | true | Event creation date |
| closedTime | date-time | true | Event closure time |
| active | boolean | true | Whether event is active |
| closed | boolean | true | Whether event is closed |
| archived | boolean | true | Whether event is archived |
| featured | boolean | true | Whether event is featured |
| restricted | boolean | true | Whether event is restricted |
| liquidity | number | true | Total liquidity in event |
| volume | number | true | Total trading volume |
| openInterest | number | true | Open interest amount |
| volume24hr | number | true | 24-hour trading volume |
| volume1wk | number | true | 1-week trading volume |
| volume1mo | number | true | 1-month trading volume |
| volume1yr | number | true | 1-year trading volume |
| markets | array[Market] | false | Array of associated markets |
| categories | array[Category] | false | Array of event categories |
| tags | array[Tag] | false | Array of event tags |
| collections | array[Collection] | false | Array of event collections |
| series | array[Series] | false | Array of associated series |
| image | string | true | Event image URL |
| icon | string | true | Event icon URL |
| featuredImage | string | true | Featured image URL |
| imageOptimized | ImageOptimization | true | Optimized image data |
| iconOptimized | ImageOptimization | true | Optimized icon data |
| featuredImageOptimized | ImageOptimization | true | Optimized featured image data |
| chat | Chat | true | Chat data (if included) |
| template | Template | true | Template data (if included) |

**Nested Objects:**
- **Market**: Contains market-specific data including prices, outcomes, and trading information
- **Category**: Event category information with metadata
- **Tag**: Tag objects with label, slug, and metadata
- **Collection**: Collection information for grouped events
- **Series**: Series data for recurring events
- **ImageOptimization**: Optimized image variants and metadata
- **Chat**: Chat room data (when include_chat=true)
- **Template**: Template data (when include_template=true)

## Example Response
```json
[
  {
    "id": "event_123",
    "ticker": "ELECTION2024",
    "slug": "us-presidential-election-2024",
    "title": "US Presidential Election 2024",
    "subtitle": "Who will win the 2024 US Presidential Election?",
    "description": "This market predicts the winner of the 2024 US Presidential Election",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2024-11-05T23:59:59Z",
    "active": true,
    "closed": false,
    "featured": true,
    "liquidity": 1500000.50,
    "volume": 5000000.75,
    "openInterest": 2500000.25,
    "markets": [
      {
        "id": "market_456",
        "question": "Will the Republican candidate win?",
        "outcomePrices": [0.45, 0.55]
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "Politics"
      }
    ],
    "tags": [
      {
        "id": "tag_politics",
        "label": "Politics",
        "slug": "politics"
      }
    ]
  }
]
```

## Additional Notes
- All query parameters are optional
- Date parameters should be in ISO 8601 format
- The response includes comprehensive event data with nested objects for markets, categories, and tags
- Use `limit` and `offset` for pagination
- Filtering parameters can be combined for precise results
- Response size can be large; consider using specific filters to reduce payload size