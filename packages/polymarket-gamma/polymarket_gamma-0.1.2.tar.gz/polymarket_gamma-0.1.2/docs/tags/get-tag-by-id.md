# Get Tag by ID

## HTTP Method
GET /tags/{id}

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | Path parameter | Tag identifier |
| include_template | boolean | No | - | Include template information in the response |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Unique identifier for the tag |
| label | string | Yes | Human-readable label for the tag |
| slug | string | Yes | URL-friendly slug for the tag |
| forceShow | boolean | Yes | Whether to force show this tag |
| publishedAt | string | Yes | When the tag was published |
| createdBy | integer | Yes | ID of user who created the tag |
| updatedBy | integer | Yes | ID of user who last updated the tag |
| createdAt | string | Yes | When the tag was created (date-time format) |
| updatedAt | string | Yes | When the tag was last updated (date-time format) |
| forceHide | boolean | Yes | Whether to force hide this tag |
| isCarousel | boolean | Yes | Whether this tag is a carousel tag |

## Example Response
```json
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
```

## Error Response
- **404 Not Found**: Tag with the specified ID does not exist

## Additional Notes
- Base URL: https://gamma-api.polymarket.com
- No authentication required
- All timestamp fields use ISO 8601 date-time format when not null
- Returns a single Tag object