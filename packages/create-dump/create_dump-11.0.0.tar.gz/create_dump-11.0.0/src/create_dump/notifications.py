import anyio
import httpx
from .logging import logger

async def send_ntfy_notification(topic: str, message: str, title: str):
    """Sends a simple, best-effort POST to ntfy.sh."""
    try:
        url = f"https://ntfy.sh/{topic}"
        response = await httpx.post(
            url,
            data=message.encode('utf-8'),
            headers={"Title": title},
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("Sent ntfy notification", topic=topic)
    except Exception as e:
        logger.warning("Failed to send ntfy notification", topic=topic, error=str(e))
