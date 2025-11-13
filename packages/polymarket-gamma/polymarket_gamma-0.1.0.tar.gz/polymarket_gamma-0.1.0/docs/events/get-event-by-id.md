# Get Event by ID

## HTTP Method
GET /events/{id}

## Base URL
https://gamma-api.polymarket.com

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer (path) | true | - | Event identifier |
| include_chat | boolean | false | - | Include chat data in response |
| include_template | boolean | false | - | Include template data in response |

## Response Schema
Returns a single Event object with the following structure:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | false | Event identifier |
| ticker | string | true | Event ticker symbol |
| slug | string | true | Unique slug identifier |
| title | string | true | Event title |
| subtitle | string | true | Event subtitle |
| description | string | true | Event description |
| resolutionSource | string | true | Source of event resolution |
| startDate | date-time | true | Event start date |
| creationDate | date-time | true | Event creation date |
| endDate | date-time | true | Event end date |
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
- **Market**: Contains market-specific data including question, outcomes, prices, and trading information
- **Category**: Event category information with ID and name
- **Tag**: Tag objects with ID, label, slug, and metadata
- **Collection**: Collection information for grouped events
- **Series**: Series data for recurring events
- **ImageOptimization**: Object containing optimized image variants and metadata
- **Chat**: Chat room data including messages and participants (when include_chat=true)
- **Template**: Template data for event structure (when include_template=true)

## Example Response
```json
{
  "id": "event_123456",
  "ticker": "ELECTION2024",
  "slug": "us-presidential-election-2024",
  "title": "US Presidential Election 2024",
  "subtitle": "Who will win the 2024 US Presidential Election?",
  "description": "This market predicts the winner of the 2024 US Presidential Election based on official results.",
  "resolutionSource": "Official election results from Federal Election Commission",
  "startDate": "2024-01-01T00:00:00Z",
  "creationDate": "2023-12-15T10:30:00Z",
  "endDate": "2024-11-05T23:59:59Z",
  "closedTime": null,
  "active": true,
  "closed": false,
  "archived": false,
  "featured": true,
  "restricted": false,
  "liquidity": 2500000.75,
  "volume": 8500000.50,
  "openInterest": 3200000.25,
  "volume24hr": 125000.30,
  "volume1wk": 875000.60,
  "volume1mo": 3200000.80,
  "volume1yr": 12500000.00,
  "markets": [
    {
      "id": "market_789",
      "question": "Will the Republican candidate win the 2024 US Presidential Election?",
      "description": "This market resolves to Yes if the Republican candidate wins the 2024 US Presidential Election",
      "outcomes": ["No", "Yes"],
      "outcomePrices": [0.52, 0.48],
      "liquidity": 1250000.50,
      "volume": 4250000.25
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Politics",
      "slug": "politics"
    }
  ],
  "tags": [
    {
      "id": "tag_us_politics",
      "label": "US Politics",
      "slug": "us-politics",
      "forceShow": false,
      "publishedAt": "2023-12-15T10:30:00Z"
    }
  ],
  "image": "https://example.com/images/election2024.jpg",
  "icon": "https://example.com/icons/election2024.png",
  "featuredImage": "https://example.com/featured/election2024.jpg",
  "imageOptimized": {
    "small": "https://example.com/images/election2024-small.jpg",
    "medium": "https://example.com/images/election2024-medium.jpg",
    "large": "https://example.com/images/election2024-large.jpg"
  }
}
```

## Error Responses
**404 Not Found**
```json
{
  "error": "Event not found",
  "message": "Event with ID 999999 does not exist"
}
```

## Additional Notes
- The `id` parameter must be a valid integer event identifier
- Use `include_chat=true` to retrieve chat room data associated with the event
- Use `include_template=true` to retrieve template data for event structure
- The response provides comprehensive event data including all associated markets, categories, and metadata
- Date fields are in ISO 8601 format
- All monetary values are in the platform's native currency
- If the event doesn't exist, a 404 error is returned