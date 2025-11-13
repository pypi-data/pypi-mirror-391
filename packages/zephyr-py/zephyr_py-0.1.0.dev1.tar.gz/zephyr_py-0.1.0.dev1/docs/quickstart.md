# Zephyr Framework Quickstart

## Installation

```bash
pip install zephyr-framework
```

## Basic Usage

```python
from zephyr.core.app import ZephyrApp, AppConfig
from zephyr.security import JWTAuthProvider
from zephyr.db import Model, Field

# Define your data model
class User(Model):
    username = Field(str, unique=True)
    email = Field(str, unique=True)
    password = Field(str, encrypted=True)

# Configure the application
config = AppConfig(
    debug=True,
    secret_key="your-secret-key",
    database_url="postgresql://user:pass@localhost/db",
    cache_url="redis://localhost",
    queue_url="redis://localhost",
    email_config={
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "from_address": "noreply@example.com"
    }
)

# Create the application
app = ZephyrApp(config)

# Define your routes
@app.route("/users", methods=["POST"])
async def create_user(data: dict):
    user = User(**data)
    await user.save()
    return {"id": user.id}

@app.route("/users/{user_id}")
@app.auth.required
async def get_user(user_id: int):
    user = await User.get(id=user_id)
    return user.to_dict()

# Run the application
if __name__ == "__main__":
    app.run()
