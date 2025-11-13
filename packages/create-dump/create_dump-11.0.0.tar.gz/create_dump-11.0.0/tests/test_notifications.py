import pytest
from unittest.mock import AsyncMock, patch
import httpx

from create_dump.notifications import send_ntfy_notification

@pytest.mark.asyncio
async def test_send_ntfy_notification_success(mocker):
    """
    Tests that send_ntfy_notification calls httpx.post with the correct arguments.
    """
    mock_post = mocker.patch("httpx.post", new_callable=AsyncMock)

    await send_ntfy_notification("test_topic", "test_message", "test_title")

    mock_post.assert_called_once_with(
        "https://ntfy.sh/test_topic",
        data=b"test_message",
        headers={"Title": "test_title"},
        timeout=10.0,
    )

@pytest.mark.asyncio
async def test_send_ntfy_notification_http_error(mocker):
    """
    Tests that an httpx.HTTPStatusError is caught and logged.
    """
    mocker.patch(
        "httpx.post",
        side_effect=httpx.HTTPStatusError(
            "Error", request=AsyncMock(), response=AsyncMock()
        ),
    )
    mock_logger_warning = mocker.patch("create_dump.notifications.logger.warning")

    await send_ntfy_notification("test_topic", "test_message", "test_title")

    mock_logger_warning.assert_called_once()
