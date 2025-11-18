# List Series

## HTTP Method
GET /series

## Base URL
https://gamma-api.polymarket.com

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | minimum: 0 | Limit number of results returned |
| offset | integer | No | minimum: 0 | Offset for pagination |
| order | string | No | - | Comma-separated list of fields to order by |
| ascending | boolean | No | - | Sort order direction (true = ascending, false = descending) |
| slug | array of strings | No | - | Filter by slug values |
| categories_ids | array of integers | No | - | Filter by category IDs |
| categories_labels | array of strings | No | - | Filter by category labels |
| closed | boolean | No | - | Filter by closed status |
| include_chat | boolean | No | - | Include chat information in response |
| recurrence | string | No | - | Filter by recurrence type |

## Response Schema
Returns an array of Series objects with the following structure:

### Series Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Unique identifier for the series |
| ticker | string | Yes | Series ticker symbol |
| slug | string | Yes | URL-friendly slug for the series |
| title | string | Yes | Series title |
| subtitle | string | Yes | Series subtitle |
| seriesType | string | Yes | Type of series |
| recurrence | string | Yes | Recurrence pattern |
| description | string | Yes | Series description |
| image | string | Yes | Series image URL |
| icon | string | Yes | Series icon URL |
| layout | string | Yes | Layout type for the series |
| active | boolean | Yes | Whether the series is active |
| closed | boolean | Yes | Whether the series is closed |
| archived | boolean | Yes | Whether the series is archived |
| new | boolean | Yes | Whether the series is marked as new |
| featured | boolean | Yes | Whether the series is featured |
| restricted | boolean | Yes | Whether the series has restrictions |
| isTemplate | boolean | Yes | Whether this is a template series |
| templateVariables | boolean | Yes | Template variables configuration |
| publishedAt | string | Yes | Publication timestamp |
| createdBy | string | Yes | Creator identifier |
| updatedBy | string | Yes | Last updater identifier |
| createdAt | string | Yes | Creation timestamp (ISO 8601) |
| updatedAt | string | Yes | Last update timestamp (ISO 8601) |
| commentsEnabled | boolean | Yes | Whether comments are enabled |
| competitive | string | Yes | Competitive status |
| volume24hr | number | Yes | 24-hour trading volume |
| volume | number | Yes | Total trading volume |
| liquidity | number | Yes | Liquidity measure |
| startDate | string | Yes | Start date (ISO 8601) |
| pythTokenID | string | Yes | Pyth token identifier |
| cgAssetName | string | Yes | CoinGecko asset name |
| score | integer | Yes | Series score |
| commentCount | integer | Yes | Number of comments |
| events | array of Event | No | Events in this series |
| collections | array of Collection | No | Collections in this series |
| categories | array of Category | No | Categories for this series |
| tags | array of Tag | No | Tags for this series |
| chats | array of Chat | No | Chat rooms for this series |

### Nested Object Schemas

#### Event Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Event identifier |
| ticker | string | Yes | Event ticker |
| slug | string | Yes | Event slug |
| title | string | Yes | Event title |
| subtitle | string | Yes | Event subtitle |
| description | string | Yes | Event description |
| image | string | Yes | Event image URL |
| icon | string | Yes | Event icon URL |
| active | boolean | Yes | Whether event is active |
| closed | boolean | Yes | Whether event is closed |
| archived | boolean | Yes | Whether event is archived |
| new | boolean | Yes | Whether event is marked as new |
| featured | boolean | Yes | Whether event is featured |
| restricted | boolean | Yes | Whether event has restrictions |
| startDate | string | Yes | Event start date (ISO 8601) |
| endDate | string | Yes | Event end date (ISO 8601) |
| volume | number | Yes | Total trading volume |
| volume24hr | number | Yes | 24-hour trading volume |
| markets | array of Market | No | Markets in this event |

#### Collection Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Collection identifier |
| ticker | string | Yes | Collection ticker |
| slug | string | Yes | Collection slug |
| title | string | Yes | Collection title |
| subtitle | string | Yes | Collection subtitle |
| collectionType | string | Yes | Type of collection |
| description | string | Yes | Collection description |
| image | string | Yes | Collection image URL |
| icon | string | Yes | Collection icon URL |
| headerImage | string | Yes | Header image URL |
| active | boolean | Yes | Whether collection is active |
| closed | boolean | Yes | Whether collection is closed |
| archived | boolean | Yes | Whether collection is archived |
| imageOptimized | ImageOptimization | Yes | Optimized image data |
| iconOptimized | ImageOptimization | Yes | Optimized icon data |
| headerImageOptimized | ImageOptimization | Yes | Optimized header image data |

#### Category Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Category identifier |
| label | string | Yes | Category label |
| slug | string | Yes | Category slug |
| parentCategory | string | Yes | Parent category identifier |
| publishedAt | string | Yes | Publication timestamp |
| createdBy | string | Yes | Creator identifier |
| updatedBy | string | Yes | Last updater identifier |
| createdAt | string | Yes | Creation timestamp (ISO 8601) |
| updatedAt | string | Yes | Last update timestamp (ISO 8601) |

#### Tag Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Tag identifier |
| label | string | Yes | Tag label |
| slug | string | Yes | Tag slug |
| forceShow | boolean | Yes | Whether to force show this tag |
| forceHide | boolean | Yes | Whether to force hide this tag |
| isCarousel | boolean | Yes | Whether tag is for carousel display |
| publishedAt | string | Yes | Publication timestamp |
| createdBy | integer | Yes | Creator identifier |
| updatedBy | integer | Yes | Last updater identifier |
| createdAt | string | Yes | Creation timestamp (ISO 8601) |
| updatedAt | string | Yes | Last update timestamp (ISO 8601) |

#### Chat Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Chat identifier |
| channelId | string | Yes | Chat channel ID |
| channelName | string | Yes | Chat channel name |
| channelImage | string | Yes | Chat channel image URL |
| live | boolean | Yes | Whether chat is currently live |
| startTime | string | Yes | Chat start time (ISO 8601) |
| endTime | string | Yes | Chat end time (ISO 8601) |

## Example Response
```json
[
  {
    "id": "series123",
    "ticker": "BTC",
    "slug": "bitcoin-series",
    "title": "Bitcoin Markets",
    "subtitle": "Bitcoin-related prediction markets",
    "seriesType": "cryptocurrency",
    "recurrence": "daily",
    "description": "Markets related to Bitcoin price movements and events",
    "image": "https://example.com/bitcoin-series.jpg",
    "icon": "https://example.com/bitcoin-icon.png",
    "active": true,
    "closed": false,
    "archived": false,
    "new": false,
    "featured": true,
    "restricted": false,
    "isTemplate": false,
    "publishedAt": "2023-11-07T05:31:56Z",
    "createdBy": "user123",
    "updatedBy": "user456",
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z",
    "commentsEnabled": true,
    "volume24hr": 1500000.50,
    "volume": 25000000.75,
    "liquidity": 500000.25,
    "events": [
      {
        "id": "event1",
        "title": "Bitcoin Price End of Year",
        "active": true,
        "volume": 1000000.00
      }
    ],
    "categories": [
      {
        "id": "cat1",
        "label": "Cryptocurrency",
        "slug": "cryptocurrency"
      }
    ],
    "tags": [
      {
        "id": "tag1",
        "label": "Bitcoin",
        "slug": "bitcoin"
      }
    ]
  }
]
```

## Additional Notes
- This endpoint uses pagination via `limit` and `offset` parameters
- The `order` parameter accepts comma-separated field names for sorting
- By default, chat information is not included unless `include_chat=true` is specified
- All timestamps are in ISO 8601 format
- The response includes nested objects for complete series information when available
- Use filter parameters to narrow down results based on specific criteria