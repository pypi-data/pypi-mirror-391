# List Teams

## HTTP Method
GET /teams

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | minimum: 0 | Maximum number of teams to return |
| offset | integer | No | minimum: 0 | Number of teams to skip for pagination |
| order | string | No | Comma-separated list of fields | Fields to order the results by |
| ascending | boolean | No | - | Sort direction (true for ascending, false for descending) |
| league | array of strings | No | - | Filter teams by specific leagues |
| name | array of strings | No | - | Filter teams by specific names |
| abbreviation | array of strings | No | - | Filter teams by specific abbreviations |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | integer | No | Unique identifier for the team |
| name | string | Yes | Full name of the team |
| league | string | Yes | League the team belongs to |
| record | string | Yes | Team's win-loss record |
| logo | string | Yes | URL to team's logo image |
| abbreviation | string | Yes | Team's abbreviation code |
| alias | string | Yes | Alternative name or nickname for the team |
| createdAt | string (date-time) | Yes | Timestamp when the team record was created |
| updatedAt | string (date-time) | Yes | Timestamp when the team record was last updated |

## Example Response
```json
[
  {
    "id": 123,
    "name": "string",
    "league": "string",
    "record": "string",
    "logo": "string",
    "abbreviation": "string",
    "alias": "string",
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z"
  }
]
```

## Additional Notes
- All optional query parameters can be combined for filtering and pagination
- The response returns an array of Team objects
- Most fields are nullable, indicating that some team information may not be available
- The API supports ordering by multiple fields using comma-separated values
- Date-time fields follow ISO 8601 format with UTC timezone (indicated by 'Z')