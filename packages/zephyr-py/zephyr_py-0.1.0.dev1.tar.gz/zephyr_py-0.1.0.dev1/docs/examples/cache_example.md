# Caching Example

This example demonstrates how to use caching in a Zephyr application.

```python
from zephyr.core.app import ZephyrApp, AppConfig
from zephyr.cache import RedisCache
from datetime import timedelta

# Configure the application with Redis cache
config = AppConfig(
    cache_url="redis://localhost:6379/0"
)

app = ZephyrApp(config, cache_backend=RedisCache)

# Example route with caching
@app.route("/users/{user_id}")
@app.cache(expire=timedelta(minutes=5))
async def get_user(user_id: int):
    # This result will be cached for 5 minutes
    user = await User.get(id=user_id)
    return user.to_dict()

# Manual cache usage
@app.route("/expensive-operation")
async def expensive_operation():
    # Try to get from cache first
    result = await app.cache.get("expensive_result")
    if result is not None:
        return result
        
    # If not in cache, perform expensive operation
    result = await perform_expensive_calculation()
    
    # Cache the result for 1 hour
    await app.cache.set(
        "expensive_result",
        result,
        expire=timedelta(hours=1)
    )
    
    return result

# Cache invalidation example
@app.route("/users/{user_id}", methods=["PUT"])
async def update_user(user_id: int, data: dict):
    user = await User.get(id=user_id)
    await user.update(**data)
    
    # Invalidate the cached user data
    await app.cache.delete(f"user:{user_id}")
    return user.to_dict()

# Rate limiting example using cache
@app.route("/api/limited")
@app.rate_limit(limit=100, period=timedelta(minutes=1))
async def rate_limited_route():
    return {"message": "This route is rate limited"}

if __name__ == "__main__":
    app.run()
```

## Testing the Cache

```python
# Check if value exists
exists = await app.cache.exists("mykey")

# Increment a counter
value = await app.cache.increment("counter")
print(f"Counter value: {value}")

# Store complex data
user_data = {"id": 1, "name": "John"}
await app.cache.set("user:1", user_data, expire=timedelta(minutes=30))

# Retrieve data
user = await app.cache.get("user:1")
```
