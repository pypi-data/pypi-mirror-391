# List Comments

## HTTP Method
GET /comments

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | Minimum: 0 | Maximum number of comments to return |
| offset | integer | No | Minimum: 0 | Number of comments to skip for pagination |
| order | string | No | Comma-separated list of fields to order by | Fields to sort the comments by |
| ascending | boolean | No | true/false | Sort order direction (true = ascending, false = descending) |
| parent_entity_type | enum | No | "Event", "Series", "market" | Type of the parent entity the comments belong to |
| parent_entity_id | integer | No | Valid integer ID | ID of the parent entity |
| get_positions | boolean | No | true/false | Include user positions in the response |
| holders_only | boolean | No | true/false | Filter to only include comments from token holders |

## Response Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string | false | Comment identifier |
| body | string | true | Comment content/text |
| parentEntityType | string | true | Entity type commented on (Event/Series/market) |
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
- Contains reaction metadata, icon information, and user profile

## Example Response
```json
[
  {
    "id": "comment123",
    "body": "This is a comment",
    "parentEntityType": "market",
    "parentEntityID": 456,
    "userAddress": "0x123...",
    "createdAt": "2023-11-07T05:31:56Z",
    "profile": {
      "name": "User",
      "pseudonym": "username",
      "displayUsernamePublic": true
    },
    "reactions": [],
    "reportCount": 0,
    "reactionCount": 5
  }
]
```

## Additional Notes
- **Base URL**: https://gamma-api.polymarket.com
- **Security**: No authentication required
- **Response Format**: Returns an array of Comment objects
- **Pagination**: Supports limit/offset for pagination
- **Sorting**: Can sort by multiple fields using comma-separated order parameter
- **Filtering**: Can filter by parent entity type/ID and token holders