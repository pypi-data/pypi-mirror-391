# Get Comments by User Address

## HTTP Method
GET /comments/user_address/{user_address}

## Path Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_address | string | Yes | Valid Ethereum wallet address | User wallet address |

## Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| limit | integer | No | Minimum: 0 | Maximum number of comments to return |
| offset | integer | No | Minimum: 0 | Number of comments to skip for pagination |
| order | string | No | Comma-separated list of fields to order by | Fields to sort the comments by |
| ascending | boolean | No | true/false | Sort order direction (true = ascending, false = descending) |

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
| profile | object | true | User profile information |
| reactions | array | false | List of reactions to the comment |
| reportCount | integer | true | Number of reports the comment has received |
| reactionCount | integer | true | Total number of reactions to the comment |

### Nested Objects

**Profile Object**:
- name (string): User display name
- pseudonym (string): Username
- displayUsernamePublic (boolean): Whether to display username publicly

**Reactions Array**:
- Array of reaction objects with metadata and user information

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
- **Response Format**: Returns an array of Comment objects belonging to the specified user
- **Pagination**: Supports limit/offset for pagination through user's comment history
- **Sorting**: Can sort by multiple fields using comma-separated order parameter
- **Address Format**: User address should be a valid Ethereum wallet address (0x...)