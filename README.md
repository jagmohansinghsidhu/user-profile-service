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

## Structure
 - ```api/api.py```  : request methods
 - ```api/models.py``` : pydantic and db models for validation and database
 - ```api/db.py``` : database engine/session initialization
 - ```api/cache.py``` : redis related methods including decorators for caching responses

## Notes
1. Db migration initially added using alembic, but ignored for easier setup
2. Redis Caching code include hints from ```https://pypi.org/project/fastapi-redis-cache/```



## TODO
1. logging changes
2. Test cases for update and get APIs
3. kubernetes config
