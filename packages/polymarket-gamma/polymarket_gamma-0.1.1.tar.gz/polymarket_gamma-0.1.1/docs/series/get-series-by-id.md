# Get Series by ID

## HTTP Method
GET /series/{id}

## Base URL
https://gamma-api.polymarket.com

## Path Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | Must be a valid series ID | Unique identifier for the series |

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| include_chat | boolean | No | - | Include chat data in response |

## Response Schema
Returns a Series object with the following structure:

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
| series | array of Series | No | Series this event belongs to |
| collections | array of Collection | No | Collections this event belongs to |
| categories | array of Category | No | Categories for this event |
| tags | array of Tag | No | Tags for this event |

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

#### ImageOptimization Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| src | string | Yes | Optimized image source URL |
| srcSet | string | Yes | Responsive image source set |
| sizes | string | Yes | Image size descriptors |
| width | integer | Yes | Image width |
| height | integer | Yes | Image height |
| aspectRatio | number | Yes | Image aspect ratio |

## Example Response (200 OK)
```json
{
  "id": "12345",
  "ticker": "US_ELECTION_2024",
  "slug": "us-presidential-election-2024",
  "title": "US Presidential Election 2024",
  "subtitle": "Prediction markets for the 2024 US Presidential Election",
  "seriesType": "politics",
  "recurrence": "one-time",
  "description": "Markets predicting the outcome of the 2024 US Presidential Election and related political events",
  "image": "https://example.com/election-2024-banner.jpg",
  "icon": "https://example.com/election-2024-icon.png",
  "layout": "grid",
  "active": true,
  "closed": false,
  "archived": false,
  "new": true,
  "featured": true,
  "restricted": false,
  "isTemplate": false,
  "templateVariables": null,
  "publishedAt": "2024-01-15T10:00:00Z",
  "createdBy": "admin_polymarket",
  "updatedBy": "admin_polymarket",
  "createdAt": "2024-01-15T09:45:00Z",
  "updatedAt": "2024-01-15T10:00:00Z",
  "commentsEnabled": true,
  "competitive": "high",
  "volume24hr": 5000000.75,
  "volume": 85000000.50,
  "liquidity": 2000000.25,
  "startDate": "2024-01-15T10:00:00Z",
  "pythTokenID": "0x1234567890abcdef",
  "cgAssetName": "us-election-2024",
  "score": 95,
  "commentCount": 1250,
  "events": [
    {
      "id": "event_67890",
      "ticker": "BIDEN_WIN_2024",
      "slug": "will-joe-biden-win-2024-election",
      "title": "Will Joe Biden win the 2024 Presidential Election?",
      "subtitle": "Binary market on Joe Biden's election victory",
      "description": "This market resolves to Yes if Joe Biden wins the 2024 US Presidential Election",
      "active": true,
      "closed": false,
      "archived": false,
      "new": false,
      "featured": true,
      "restricted": false,
      "startDate": "2024-01-15T10:00:00Z",
      "endDate": "2024-11-05T23:59:59Z",
      "volume": 25000000.00,
      "volume24hr": 1500000.50
    }
  ],
  "collections": [
    {
      "id": "col_11111",
      "ticker": "ELECTION_COLLECTION",
      "title": "2024 Election Collection",
      "collectionType": "political",
      "active": true,
      "closed": false,
      "archived": false
    }
  ],
  "categories": [
    {
      "id": "cat_politics",
      "label": "Politics",
      "slug": "politics",
      "parentCategory": null,
      "createdAt": "2023-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "tags": [
    {
      "id": "tag_us_election",
      "label": "US Election",
      "slug": "us-election",
      "forceShow": false,
      "forceHide": false,
      "isCarousel": true,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    },
    {
      "id": "tag_presidential",
      "label": "Presidential",
      "slug": "presidential",
      "forceShow": false,
      "forceHide": false,
      "isCarousel": false,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "chats": [
    {
      "id": "chat_abc123",
      "channelId": "election-2024-discussion",
      "channelName": "Election 2024 Discussion",
      "channelImage": "https://example.com/election-chat-icon.png",
      "live": true,
      "startTime": "2024-01-15T10:00:00Z",
      "endTime": null
    }
  ]
}
```

## Error Response (404 Not Found)
```json
{
  "error": "Not found",
  "message": "Series with the specified ID does not exist"
}
```

## Additional Notes
- The series ID in the path parameter must be a valid integer
- Chat information is only included when `include_chat=true` is specified in the query parameters
- All timestamps are in ISO 8601 format (UTC)
- The response includes complete nested object structures when available
- This endpoint provides comprehensive information about a single series including all related events, collections, categories, and tags
- The `competitive` field indicates the competitive level of markets within the series
- Image optimization data is provided for better performance when displaying series images
- The `score` field represents an internal ranking or popularity metric for the series