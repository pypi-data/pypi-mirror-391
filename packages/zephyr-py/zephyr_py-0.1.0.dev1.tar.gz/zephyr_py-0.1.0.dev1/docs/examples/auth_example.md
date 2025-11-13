# Authentication Example

This example demonstrates how to implement authentication in a Zephyr application.

```python
from zephyr.core.app import ZephyrApp, AppConfig
from zephyr.security import JWTAuthProvider
from zephyr.db import Model, Field

# Define User model
class User(Model):
    username = Field(str, unique=True)
    password = Field(str, encrypted=True)
    email = Field(str, unique=True)
    is_active = Field(bool, default=True)

# Configure the application
config = AppConfig(
    secret_key="your-secret-key",
    database_url="postgresql://user:pass@localhost/db"
)

app = ZephyrApp(config)

# Authentication routes
@app.route("/auth/login", methods=["POST"])
async def login(request):
    data = await request.json()
    user = await User.get(username=data["username"])
    
    if not user or not app.auth.verify_password(data["password"], user.password):
        return {"error": "Invalid credentials"}, 401
    
    token = await app.auth.create_token({"user_id": user.id})
    return {"token": token}

@app.route("/auth/me")
@app.auth.required
async def get_current_user(request):
    user_id = request.auth["user_id"]
    user = await User.get(id=user_id)
    return user.to_dict()

# Protected route example
@app.route("/protected")
@app.auth.required
@app.rbac.requires("admin")
async def protected_route():
    return {"message": "This is a protected route"}

if __name__ == "__main__":
    app.run()
```

## Testing the Authentication

```bash
# Create a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123", "email": "test@example.com"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Access protected route
curl http://localhost:8000/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```
