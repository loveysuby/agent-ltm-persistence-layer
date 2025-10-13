# API Documentation

## Endpoints

### Create Memory

```http
POST /memories
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "User prefers Python over JavaScript",
  "memory_type": "semantic",
  "metadata": {"category": "preferences"}
}
```

Response:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "content": "User prefers Python over JavaScript",
  "memory_type": "semantic",
  "metadata": { "category": "preferences" },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Search Memories

```http
POST /memories/search
Content-Type: application/json

{
  "query": "programming preferences",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "limit": 10,
  "threshold": 0.7
}
```

Response:

```json
[
  {
    "memory": { ... },
    "score": 0.85
  }
]
```

### Get User Memories

```http
GET /memories/user/{user_id}?limit=50
```

### Delete Memory

```http
DELETE /memories/{memory_id}?user_id={user_id}
```

## Error Responses

```json
{
  "detail": "Error message"
}
```

Status codes:

- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
