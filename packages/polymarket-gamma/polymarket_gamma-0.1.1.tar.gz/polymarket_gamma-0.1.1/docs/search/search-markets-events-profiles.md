# Search Markets, Events, and Profiles

## HTTP Method
GET https://gamma-api.polymarket.com/public-search

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| q | string | Yes | - | Search query term |
| cache | boolean | No | - | Enable/disable response caching |
| events_status | string | No | - | Filter events by status |
| limit_per_type | integer | No | - | Number of results per type |
| page | integer | No | - | Page number for pagination |
| events_tag | array of strings | No | - | Filter by event tags |
| keep_closed_markets | integer | No | - | Include closed markets |
| sort | string | No | - | Sort order |
| ascending | boolean | No | - | Sort direction |
| search_tags | boolean | No | - | Include tag search |
| search_profiles | boolean | No | - | Include profile search |
| recurrence | string | No | - | Filter by recurrence |
| exclude_tag_id | array of integers | No | - | Exclude tag IDs |
| optimized | boolean | No | - | Enable optimization |

## Response Schema

### Root Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| events | Event[] | Yes | Array of Event objects |
| tags | SearchTag[] | Yes | Array of SearchTag objects |
| profiles | Profile[] | Yes | Array of Profile objects |
| pagination | Pagination | No | Pagination metadata |

### Event Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Event identifier |
| ticker | string | Yes | Event ticker symbol |
| slug | string | Yes | URL-friendly slug |
| title | string | Yes | Event title |
| subtitle | string | Yes | Event subtitle |
| description | string | Yes | Event description |
| startDate | string (date-time) | Yes | Event start date (ISO 8601) |
| endDate | string (date-time) | Yes | Event end date (ISO 8601) |
| active | boolean | Yes | Whether event is active |
| closed | boolean | Yes | Whether event is closed |
| markets | Market[] | No | Array of Market objects |
| categories | Category[] | No | Array of Category objects |
| tags | Tag[] | No | Array of Tag objects |

### Market Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Market identifier |
| question | string | Yes | Market question |
| conditionId | string | No | Condition identifier |
| slug | string | Yes | URL-friendly slug |
| endDate | string (date-time) | Yes | Market end date (ISO 8601) |
| active | boolean | Yes | Whether market is active |
| closed | boolean | Yes | Whether market is closed |
| liquidity | string | Yes | Market liquidity |
| volume | string | Yes | Market volume |

### Category Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Category identifier |
| label | string | Yes | Category label |
| parentCategory | string | Yes | Parent category identifier |
| slug | string | Yes | URL-friendly slug |
| createdAt | string (date-time) | Yes | Creation timestamp (ISO 8601) |
| updatedAt | string (date-time) | Yes | Last update timestamp (ISO 8601) |

### Tag Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Tag identifier |
| label | string | Yes | Tag label |
| slug | string | Yes | URL-friendly slug |
| forceShow | boolean | Yes | Whether to force display |
| isCarousel | boolean | Yes | Whether displayed in carousel |
| createdAt | string (date-time) | Yes | Creation timestamp (ISO 8601) |
| updatedAt | string (date-time) | Yes | Last update timestamp (ISO 8601) |

### SearchTag Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Search tag identifier |
| label | string | No | Search tag label |
| slug | string | No | URL-friendly slug |
| event_count | integer | No | Number of events with this tag |

### Profile Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Profile identifier |
| name | string | Yes | Profile display name |
| user | integer | Yes | User ID |
| pseudonym | string | Yes | Profile pseudonym |
| profileImage | string | Yes | Profile image URL |
| bio | string | Yes | Profile bio/description |

### Pagination Object
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| hasMore | boolean | No | Whether more pages exist |
| totalResults | integer | No | Total number of results |

## Example Response
```json
{
  "events": [
    {
      "id": "0x1234567890abcdef",
      "ticker": "EVENT-2024",
      "slug": "sample-event",
      "title": "Sample Event Title",
      "subtitle": "Event subtitle",
      "description": "Detailed event description",
      "startDate": "2023-11-07T05:31:56Z",
      "endDate": "2023-12-07T05:31:56Z",
      "active": true,
      "closed": false,
      "markets": [
        {
          "id": "0xabcdef1234567890",
          "question": "Will this happen?",
          "conditionId": "0x1234567890abcdef1234567890abcdef",
          "slug": "sample-market",
          "endDate": "2023-12-07T05:31:56Z",
          "active": true,
          "closed": false,
          "liquidity": "1000.50",
          "volume": "5000.25"
        }
      ],
      "categories": [
        {
          "id": "cat_1",
          "label": "Sports",
          "parentCategory": null,
          "slug": "sports",
          "createdAt": "2023-01-01T00:00:00Z",
          "updatedAt": "2023-11-01T12:00:00Z"
        }
      ],
      "tags": [
        {
          "id": "tag_1",
          "label": "Popular",
          "slug": "popular",
          "forceShow": false,
          "isCarousel": true,
          "createdAt": "2023-01-01T00:00:00Z",
          "updatedAt": "2023-11-01T12:00:00Z"
        }
      ]
    }
  ],
  "tags": [
    {
      "id": "tag_1",
      "label": "Popular",
      "slug": "popular",
      "event_count": 25
    }
  ],
  "profiles": [
    {
      "id": "profile_1",
      "name": "John Doe",
      "user": 12345,
      "pseudonym": "TraderJoe",
      "profileImage": "https://example.com/image.jpg",
      "bio": "Experienced trader"
    }
  ],
  "pagination": {
    "hasMore": true,
    "totalResults": 150
  }
}
```

## Additional Notes

- **Authentication**: No authentication required for this endpoint
- **Rate Limiting**: Not specified in documentation
- **Date/Time Format**: All datetime fields use ISO 8601 format (e.g., "2023-11-07T05:31:56Z")
- **Caching**: Can be controlled with the `cache` parameter
- **Pagination**: Supports pagination through `page` and `limit_per_type` parameters
- **Search Scope**: Can search across markets, events, and profiles independently using `search_tags` and `search_profiles` parameters
- **Filtering**: Extensive filtering options including event status, tags, and recurrence
- **Nullability**: Many fields are nullable and may return `null` in responses
- **Performance**: Can enable optimization with `optimized` parameter for better response times