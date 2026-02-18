# User Profile Service

## Implements four endpoints

| API              | Method | Description                                              |
|------------------|--------|----------------------------------------------------------|
| `/users/{user_id}` | GET    | Returns user data by ID. Returns 404 if not found.       |
| `/users`         | GET    | Returns all users.                                       |
| `/users`         | POST   | Creates a new user. Validates input.                     |
| `/users/{user_id}` | PATCH  | Updates a user’s data partially and refreshes the cache. |

## Running API
```docker compose up -d api```

Navigate to ```localhost.8000/docs``` to test apis 


## Running Test Cases
```docker compose run --rm tests```

