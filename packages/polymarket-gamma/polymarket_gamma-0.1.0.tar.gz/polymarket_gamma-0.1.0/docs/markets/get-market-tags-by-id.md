# Get Market Tags by ID

## HTTP Method
GET /markets/{id}/tags

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | - | Market identifier (path parameter) |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Tag identifier |
| label | string | Yes | Tag label |
| slug | string | Yes | Tag slug |
| forceShow | boolean | Yes | Whether to force show this tag |
| publishedAt | string | Yes | Publication timestamp |
| createdBy | integer | Yes | Creator user ID |
| updatedBy | integer | Yes | Last updater user ID |
| createdAt | date-time | Yes | Creation timestamp |
| updatedAt | date-time | Yes | Last update timestamp |
| forceHide | boolean | Yes | Whether to force hide this tag |
| isCarousel | boolean | Yes | Whether tag appears in carousel |

## Example Response
```json
[
  {
    "id": "string",
    "label": "string",
    "slug": "string",
    "forceShow": true,
    "publishedAt": "string",
    "createdBy": 123,
    "updatedBy": 123,
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z",
    "forceHide": false,
    "isCarousel": true
  }
]
```

## Additional Notes
- Returns tags attached to the specified market
- Error response: 404 Not found if market with specified ID does not exist
- No additional query parameters required
- Base URL: https://gamma-api.polymarket.com