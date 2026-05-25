"""Unit tests for the web (URL) parser.

httpx is mocked so no real network calls are made.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.parsers.web_parser import parse_url


def _mock_response(html: str, status: int = 200):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    if status >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status}")
    return resp


@pytest.mark.asyncio
async def test_parse_url_extracts_visible_text():
    html = "<html><body><h1>Welcome</h1><p>This is a test page.</p></body></html>"
    resp = _mock_response(html)

    with patch("app.parsers.web_parser.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await parse_url("https://example.com")

    assert "Welcome" in result
    assert "This is a test page." in result


@pytest.mark.asyncio
async def test_parse_url_strips_script_and_style():
    html = (
        "<html><body>"
        "<script>var x = 1;</script>"
        "<style>.foo { color: red }</style>"
        "<p>Real content here.</p>"
        "</body></html>"
    )
    resp = _mock_response(html)

    with patch("app.parsers.web_parser.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await parse_url("https://example.com")

    assert "var x" not in result
    assert ".foo" not in result
    assert "Real content here." in result


@pytest.mark.asyncio
async def test_parse_url_strips_nav_and_footer():
    html = (
        "<html><body>"
        "<nav>Home | About | Contact</nav>"
        "<main><p>Article text.</p></main>"
        "<footer>Copyright 2025</footer>"
        "</body></html>"
    )
    resp = _mock_response(html)

    with patch("app.parsers.web_parser.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await parse_url("https://example.com")

    assert "Article text." in result
    # nav / footer content should be removed
    assert "Home | About" not in result
    assert "Copyright 2025" not in result


@pytest.mark.asyncio
async def test_parse_url_collapses_blank_lines():
    html = "<html><body><p>Line 1</p><p>Line 2</p></body></html>"
    resp = _mock_response(html)

    with patch("app.parsers.web_parser.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await parse_url("https://example.com")

    assert "\n\n\n" not in result


@pytest.mark.asyncio
async def test_parse_url_raises_on_http_error():
    resp = _mock_response("", status=404)

    with patch("app.parsers.web_parser.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(Exception):
            await parse_url("https://example.com/missing")
