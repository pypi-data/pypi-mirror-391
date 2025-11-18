# Get Tags Related to a Tag ID

## HTTP Method
GET /tags/{id}/related-tags/tags

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | Path parameter | Tag identifier to get related tags for |
| omit_empty | boolean | No | - | Whether to omit empty relationships from results |
| status | string | No | "active", "closed", "all" | Filter by tag status |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Unique identifier for the related tag |
| label | string | Yes | Human-readable label for the related tag |
| slug | string | Yes | URL-friendly slug for the related tag |
| forceShow | boolean | Yes | Whether to force show this related tag |
| publishedAt | string | Yes | When the related tag was published |
| createdBy | integer | Yes | ID of user who created the related tag |
| updatedBy | integer | Yes | ID of user who last updated the related tag |
| createdAt | string | Yes | When the related tag was created (date-time format) |
| updatedAt | string | Yes | When the related tag was last updated (date-time format) |
| forceHide | boolean | Yes | Whether to force hide this related tag |
| isCarousel | boolean | Yes | Whether this related tag is a carousel tag |

## Example Response
```json
[
  {
    "id": "<string>",
    "label": "<string>",
    "slug": "<string>",
    "forceShow": true,
    "publishedAt": "<string>",
    "createdBy": 123,
    "updatedBy": 123,
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z",
    "forceHide": true,
    "isCarousel": true
  }
]
```

## Additional Notes
- Base URL: https://gamma-api.polymarket.com
- Returns an array of complete Tag objects that are related to the specified tag ID
- Unlike the relationships endpoint, this returns full tag objects rather than just relationship metadata
- All timestamp fields use ISO 8601 date-time format when not null
- The response includes all standard tag fields for each related tag