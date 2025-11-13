# Get Comments by Comment ID

## HTTP Method
GET /comments/{id}

## Path Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| id | integer | Yes | Valid comment ID | The unique identifier for the comment |

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| get_positions | boolean | No | true/false | Include user positions in the response |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | false | Comment identifier |
| body | string | true | Comment content/text |
| parentEntityType | string | true | Entity type commented on |
| parentEntityID | integer | true | Entity ID the comment belongs to |
| parentCommentID | string | true | Parent comment ID for threaded replies |
| userAddress | string | true | Author's wallet address |
| replyAddress | string | true | Reply target address |
| createdAt | string (date-time) | true | Creation timestamp in ISO format |
| updatedAt | string (date-time) | true | Last update timestamp in ISO format |
| profile | object | false | User profile information (nested CommentProfile) |
| reactions | array | false | List of reactions to the comment (Reaction objects) |
| reportCount | integer | true | Number of reports the comment has received |
| reactionCount | integer | true | Total number of reactions to the comment |

### Nested Objects

**CommentProfile Object**:
- Contains user details, image optimization data, and positions array

**Reaction Object** (in reactions array):
- Each reaction includes reaction metadata, icon, and user profile

## Example Response
```json
[
  {
    "id": "<string>",
    "body": "<string>",
    "parentEntityType": "<string>",
    "parentEntityID": 123,
    "parentCommentID": "<string>",
    "userAddress": "<string>",
    "replyAddress": "<string>",
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z",
    "profile": { ... },
    "reactions": [ ... ],
    "reportCount": 123,
    "reactionCount": 123
  }
]
```

## Additional Notes
- **Base URL**: https://gamma-api.polymarket.com
- **Security**: No authentication required
- **Response Format**: Returns an array of Comment objects (typically single element when querying by ID)
- **Positions**: Use get_positions=true to include user position data in the profile
- **Date Format**: All timestamps are in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)