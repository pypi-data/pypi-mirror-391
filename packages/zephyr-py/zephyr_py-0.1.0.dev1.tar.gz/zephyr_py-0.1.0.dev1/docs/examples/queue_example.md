# Queue System Example

This example demonstrates how to use the queue system in a Zephyr application.

```python
from zephyr.core.app import ZephyrApp, AppConfig
from zephyr.queue import QueueManager
from datetime import timedelta

# Configure the application
config = AppConfig(
    queue_url="redis://localhost:6379/1"
)

app = ZephyrApp(config)

# Create a queue for email processing
email_queue = await app.queue.create_queue("email_notifications")

# Producer example - Adding jobs to queue
@app.route("/send-notification", methods=["POST"])
async def schedule_notification(request):
    data = await request.json()
    
    # Add message to queue
    await email_queue.push({
        "to": data["email"],
        "subject": "Welcome!",
        "template": "welcome_email",
        "context": {
            "username": data["username"]
        }
    })
    
    return {"message": "Notification scheduled"}

# Consumer example - Processing queue messages
@app.queue_worker("email_notifications")
async def process_email_notifications(message):
    # Send email using the email system
    await app.email.send_email(
        to=message["to"],
        subject=message["subject"],
        template=message["template"],
        context=message["context"]
    )

# Batch processing example
@app.queue_worker("data_processing", batch_size=100)
async def process_data_batch(messages):
    # Process multiple messages at once
    for message in messages:
        await process_data_item(message)

# Error handling example
@app.queue_worker("critical_tasks", retries=3)
async def process_critical_task(message):
    try:
        await perform_critical_operation(message)
    except Exception as e:
        # Log error and retry
        app.logger.error(f"Error processing task: {e}")
        raise  # This will trigger a retry

# Delayed processing example
@app.route("/schedule-reminder", methods=["POST"])
async def schedule_reminder(request):
    data = await request.json()
    
    # Schedule reminder for future processing
    await app.queue.schedule(
        queue="reminders",
        message=data,
        delay=timedelta(hours=24)
    )
    
    return {"message": "Reminder scheduled"}

if __name__ == "__main__":
    # Start the queue workers
    app.queue_workers.start()
    app.run()
```

## Testing the Queue System

```python
# Push messages to queue
await queue.push({"task": "important_task", "data": {...}})

# Process messages
message = await queue.pop()
if message:
    try:
        await process_message(message)
        await queue.ack(message.id)
    except Exception:
        await queue.nack(message.id)  # Return to queue

# Check queue size
size = await queue.size()
print(f"Queue size: {size}")

# Clear queue
await queue.clear()
```
