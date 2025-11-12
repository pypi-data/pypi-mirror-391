# Quill Python SDK

## Quickstart

First, install the quillsql package by running:

```bash
$ pip install quillsql
```

Then, add a `/quill` endpoint to your existing python server. For example, if
you were running a FASTAPI app, you would just add the endpoint like this:

```python
from quillsql import Quill

quill = Quill(
    private_key=os.getenv("QULL_PRIVATE_KEY"),
    database_connection_string=os.getenv("POSTGRES_READ"),
    database_type="postgresql"
)

security = HTTPBearer()

async def authenticate_jwt(token: str = Depends(security)):
    # Your JWT validation logic here
    # Return user object or raise HTTPException
    user = validate_jwt_token(token.credentials)
    return user

@app.post("/quill")
async def quill_post(data: Request, user: dict = Depends(authenticate_jwt)):
    # assuming user fetched via auth middleware has an userId
    user_id = user["user_id"]
    body = await data.json()
    metadata = body.get("metadata")

    result = quill.query(
        tenants=[{"tenantField": "user_id", "tenantIds": [user_id]}],
        metadata=metadata
    )
    return result
```

Then you can run your app like normally. Pass in this route to our react library
on the frontend and you all set!
