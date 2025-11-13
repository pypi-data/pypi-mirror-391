# Get Event Tags

## HTTP Method
GET /events/{id}/tags

## Base URL
https://gamma-api.polymarket.com

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer (path) | true | - | Event identifier |

## Response Schema
Returns an array of Tag objects with the following structure:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | false | Unique tag identifier |
| label | string | true | Human-readable tag label |
| slug | string | true | URL-friendly slug for the tag |
| forceShow | boolean | true | Whether to force display of this tag |
| publishedAt | string | true | Publication timestamp (ISO 8601) |
| createdBy | integer | true | ID of user who created the tag |
| updatedBy | integer | true | ID of user who last updated the tag |
| createdAt | date-time | true | Tag creation timestamp (ISO 8601) |
| updatedAt | date-time | true | Tag last update timestamp (ISO 8601) |
| forceHide | boolean | true | Whether to force hide this tag |
| isCarousel | boolean | true | Whether tag appears in carousel display |

## Example Response
```json
[
  {
    "id": "tag_politics_us_election",
    "label": "US Election",
    "slug": "us-election",
    "forceShow": true,
    "publishedAt": "2024-01-15T10:30:00Z",
    "createdBy": 12345,
    "updatedBy": 12345,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z",
    "forceHide": false,
    "isCarousel": true
  },
  {
    "id": "tag_politics_presidential",
    "label": "Presidential",
    "slug": "presidential",
    "forceShow": false,
    "publishedAt": "2024-01-16T14:22:00Z",
    "createdBy": 67890,
    "updatedBy": 67890,
    "createdAt": "2024-01-16T14:22:00Z",
    "updatedAt": "2024-01-16T14:22:00Z",
    "forceHide": false,
    "isCarousel": false
  },
  {
    "id": "tag_sports_football",
    "label": "Football",
    "slug": "football",
    "forceShow": true,
    "publishedAt": "2023-12-01T09:15:00Z",
    "createdBy": null,
    "updatedBy": null,
    "createdAt": "2023-12-01T09:15:00Z",
    "updatedAt": "2023-12-01T09:15:00Z",
    "forceHide": false,
    "isCarousel": true
  }
]
```

## Error Responses
**404 Not Found**
```json
{
  "error": "Event not found",
  "message": "Event with ID 999999 does not exist"
}
```

## Additional Notes
- The `id` parameter must be a valid integer event identifier
- Returns all tags associated with the specified event
- Tags can be used for categorization and filtering of events
- The `forceShow` and `forceHide` fields control tag visibility behavior
- `isCarousel` indicates if the tag should appear in carousel displays
- Date fields are in ISO 8601 format
- If the event doesn't exist, a 404 error is returned
- Empty array may be returned if the event has no associated tags
- Tag metadata includes creation and update tracking with user IDs where applicable