import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.solnet.yggdrasil import (
    YggdrasilClient,
    YggdrasilConnectionError,
)


@pytest.fixture
def mock_successful_response():
    """Mock a successful Yggdrasil admin API response."""
    async def _mock_post(*args, **kwargs):
        # Simulate different responses based on the request
        payload = kwargs.get("json", {})
        request_type = payload.get("request")

        if request_type == "getSelf":
            return AsyncMock(
                status=200,
                json=AsyncMock(return_value={
                    "response": {"key": "abc123", "coords": [1, 2, 3]}
                })
            )
        elif request_type == "getPeers":
            return AsyncMock(
                status=200,
                json=AsyncMock(return_value={"response": {"peers": [{"address": "peer1"}]}})
            )
        elif request_type == "getTree":
            return AsyncMock(
                status=200,
                json=AsyncMock(return_value={"response": {"entries": []}})
            )
        return AsyncMock(status=200, json=AsyncMock(return_value={"response": {}}))

    return _mock_post


@pytest.mark.asyncio
async def test_ping_success(mock_successful_response):
    client = YggdrasilClient(endpoint="http://localhost:9001", auto_detect=False)
    with patch("aiohttp.ClientSession.post", new=mock_successful_response):
        result = await client.ping()
        assert result is True


@pytest.mark.asyncio
async def test_ping_failure():
    client = YggdrasilClient(endpoint="http://localhost:9999", auto_detect=False)
    with patch("aiohttp.ClientSession.post", side_effect=Exception("Connection refused")):
        result = await client.ping()
        assert result is False


@pytest.mark.asyncio
async def test_auto_detection_falls_back_to_helpful_error():
    """Should try multiple endpoints and give a useful error message."""
    client = YggdrasilClient(auto_detect=True)  # Will try several endpoints
    with patch("aiohttp.ClientSession.post", side_effect=Exception("Connection refused")):
        with pytest.raises(YggdrasilConnectionError) as exc:
            await client.get_self()

        error_msg = str(exc.value)
        assert "Could not reach Yggdrasil admin API" in error_msg
        assert "Is Yggdrasil running?" in error_msg
        assert "yggdrasil -autoconf" in error_msg


@pytest.mark.asyncio
async def test_get_node_info_success(mock_successful_response):
    client = YggdrasilClient(endpoint="http://localhost:9001", auto_detect=False)
    with patch("aiohttp.ClientSession.post", new=mock_successful_response):
        info = await client.get_node_info()
        assert "self" in info
        assert "peer_count" in info
        assert info["peer_count"] >= 0

# More tests can be added for:
# - add_peer / remove_peer
# - Unix socket path handling
# - Specific error message formatting
