# Get Related Tags Relationships by Tag ID

## HTTP Method
GET /tags/{id}/related-tags

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | Path parameter | Tag identifier to get relationships for |
| omit_empty | boolean | No | - | Whether to omit empty relationships from results |
| status | string | No | "active", "closed", "all" | Filter by tag status |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | No | Unique identifier for the relationship |
| tagID | integer | Yes | ID of the primary tag |
| relatedTagID | integer | Yes | ID of the related tag |
| rank | integer | Yes | Ranking/ordering of the relationship |

## Example Response
```json
[
  {
    "id": "<string>",
    "tagID": 123,
    "relatedTagID": 123,
    "rank": 123
  }
]
```

## Additional Notes
- Base URL: https://gamma-api.polymarket.com
- Returns an array of RelatedTag objects
- Response shows relationship metadata between tags, not the full tag objects
- The `rank` field appears to indicate the strength or importance of the relationship
- All numeric fields except `id` can be null