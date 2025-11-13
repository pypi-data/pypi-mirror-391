# Get Sports Metadata Information

## HTTP Method
GET /sports

## Query Parameters
No query parameters required for this endpoint.

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| sport | string | No | The sport identifier or abbreviation |
| image | string (URI) | No | URL to the sport's logo or image asset |
| resolution | string (URI) | No | URL to the official resolution source |
| ordering | string | No | Preferred ordering for sport display, typically 'home' or 'away' |
| tags | string | No | Comma-separated list of tag IDs |
| series | string | No | Series identifier linking the sport to a specific tournament |

## Example Response
```json
[
  {
    "sport": "string",
    "image": "string",
    "resolution": "string",
    "ordering": "string",
    "tags": "string",
    "series": "string"
  }
]
```

## Additional Notes
- This endpoint returns metadata about all available sports in the system
- No authentication or query parameters are required
- The response is always an array, even if only one sport is available
- The `image` and `resolution` fields contain URLs that should be accessible for fetching sport-related assets
- The `ordering` field determines how teams in this sport should be ordered in displays (typically 'home' or 'away')
- The `tags` field contains a comma-separated list of identifiers that can be used for categorization or filtering
- The `series` field links the sport to specific tournament or series identifiers