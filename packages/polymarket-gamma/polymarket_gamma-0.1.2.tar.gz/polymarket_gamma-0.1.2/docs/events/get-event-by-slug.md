# Get Event by Slug

## HTTP Method
GET /events/slug/{slug}

## Base URL
https://gamma-api.polymarket.com

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| slug | string (path) | true | - | The unique slug identifier for the event |
| include_chat | boolean | false | - | Include chat information in response |
| include_template | boolean | false | - | Include template information in response |

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
| markets | array[Market] | false | Array of associated markets |
| categories | array[Category] | false | Array of event categories |
| tags | array[Tag] | false | Array of event tags |
| series | array[Series] | false | Array of associated series |
| collections | array[Collection] | false | Array of event collections |
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
  "id": "event_789012",
  "ticker": "SUPERBOWL2024",
  "slug": "super-bowl-2024-winner",
  "title": "Super Bowl 2024 Winner",
  "subtitle": "Which team will win Super Bowl LVIII?",
  "description": "This market predicts the winning team of Super Bowl LVIII between the Kansas City Chiefs and San Francisco 49ers.",
  "resolutionSource": "Official NFL game results",
  "startDate": "2024-01-01T00:00:00Z",
  "creationDate": "2023-12-20T15:45:00Z",
  "endDate": "2024-02-11T23:59:59Z",
  "closedTime": "2024-02-12T00:30:00Z",
  "active": false,
  "closed": true,
  "archived": false,
  "featured": true,
  "restricted": false,
  "liquidity": 5000000.00,
  "volume": 15000000.50,
  "openInterest": 7500000.25,
  "volume24hr": 250000.75,
  "markets": [
    {
      "id": "market_456789",
      "question": "Will the Kansas City Chiefs win Super Bowl LVIII?",
      "description": "This market resolves to Yes if the Kansas City Chiefs win Super Bowl LVIII",
      "outcomes": ["No", "Yes"],
      "outcomePrices": [0.0, 1.0],
      "liquidity": 2500000.00,
      "volume": 7500000.25
    }
  ],
  "categories": [
    {
      "id": 2,
      "name": "Sports",
      "slug": "sports"
    },
    {
      "id": 5,
      "name": "Football",
      "slug": "football"
    }
  ],
  "tags": [
    {
      "id": "tag_nfl",
      "label": "NFL",
      "slug": "nfl",
      "forceShow": true,
      "isCarousel": true
    },
    {
      "id": "tag_super_bowl",
      "label": "Super Bowl",
      "slug": "super-bowl",
      "forceShow": false,
      "isCarousel": true
    }
  ],
  "image": "https://example.com/images/superbowl2024.jpg",
  "icon": "https://example.com/icons/superbowl2024.png",
  "featuredImage": "https://example.com/featured/superbowl2024.jpg",
  "series": [
    {
      "id": "series_super_bowl",
      "name": "Super Bowl Winners",
      "slug": "super-bowl-winners"
    }
  ]
}
```

## Error Responses
**404 Not Found**
```json
{
  "error": "Event not found",
  "message": "Event with slug 'non-existent-event-slug' does not exist"
}
```

## Additional Notes
- The `slug` parameter must be a valid URL slug that corresponds to an existing event
- Slugs are typically URL-friendly versions of event titles (e.g., "super-bowl-2024-winner")
- Use `include_chat=true` to retrieve chat room data associated with the event
- Use `include_template=true` to retrieve template data for event structure
- The response provides comprehensive event data including all associated markets, categories, and metadata
- Date fields are in ISO 8601 format
- All monetary values are in the platform's native currency
- This endpoint is useful for retrieving events using human-readable URLs instead of numeric IDs
- If the event with the specified slug doesn't exist, a 404 error is returned
- Slugs are unique across the platform and can be used for permanent links to events