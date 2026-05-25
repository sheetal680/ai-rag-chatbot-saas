import re

import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RAGBot/1.0; +https://github.com/anthropics/claude-code)"
    )
}

_NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]


async def parse_url(url: str) -> str:
    """Fetch *url* and return its visible text content, stripped of boilerplate.

    Raises httpx.HTTPStatusError on 4xx/5xx responses.
    """
    async with httpx.AsyncClient(timeout=30, headers=_HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Remove non-content elements
    for tag in soup(_NOISE_TAGS):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse runs of blank lines to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
