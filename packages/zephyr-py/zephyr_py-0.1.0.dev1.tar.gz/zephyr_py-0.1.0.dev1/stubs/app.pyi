from _typeshed import Incomplete
from pydantic import BaseModel
from zephyr import Zephyr
from zephyr.app.requests import Request as Request

pkce_storage: dict[str, str]

class DemoUserSwitchRequest(BaseModel):
    username: str

def create_app() -> Zephyr:
    """Create and configure the Zephyr application."""
async def startup() -> None:
    """Application startup tasks."""

app: Incomplete
