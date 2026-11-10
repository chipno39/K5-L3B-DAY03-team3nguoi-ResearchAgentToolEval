
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _normalize_url(url: str) -> str:
    url = url.strip()

    if not url:
        return ""

    try:
        parsed = urlsplit(url)

        if not parsed.scheme or not parsed.netloc:
            return url

        return urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            parsed.query,
            "",
        ))
    except ValueError:
        return url


def deduplicate_results(
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    try:
        if items is None:
            items = []

        if not isinstance(items, list):
            return {
                "error": "TypeError",
                "message": "items must be a list",
            }

        unique_items = []
        seen_urls = set()

        for item in items:
            if not isinstance(item, dict):
                return {
                    "error": "TypeError",
                    "message": "Each item must be a dictionary",
                }

            url = item.get("url")

            if url is None or url == "":
                unique_items.append(item)
                continue

            if not isinstance(url, str):
                return {
                    "error": "TypeError",
                    "message": "item url must be a string",
                }

            normalized_url = _normalize_url(url)

            if not normalized_url:
                unique_items.append(item)
                continue

            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_items.append(item)

        return {
            "tool": "research_deduplicate",
            "items": unique_items,
            "original_count": len(items),
            "unique_count": len(unique_items),
            "removed_count": len(items) - len(unique_items),
        }

    except (TypeError, ValueError) as exc:
        return {
            "error": type(exc).__name__,
            "message": str(exc),
        }
