# List Tags

## HTTP Method
GET /tags

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | min: 0 | Maximum number of results to return |
| offset | integer | No | min: 0 | Number of results to skip for pagination |
| order | string | No | - | Comma-separated list of fields to order by |
| ascending | boolean | No | - | Sort order (true for ascending, false for descending) |
| include_template | boolean | No | - | Include template tags in the response |
| is_carousel | boolean | No | - | Filter by carousel flag |

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
- Returns an array of Tag objects
- All timestamp fields use ISO 8601 date-time format when not null