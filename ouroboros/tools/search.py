"""Web search tool using Brave Search API."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from urllib.parse import urlencode

import requests

from ouroboros.tools.registry import ToolContext, ToolEntry


def _web_search(ctx: ToolContext, query: str, count: int = 10) -> str:
    """Search the web using Brave Search API.

    Args:
        query: Search query string
        count: Number of results to return (default: 10, max: 20)

    Returns:
        JSON with answer summary and list of results (title, url, snippet)
    """
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return json.dumps({
            "error": "BRAVE_API_KEY not set; web_search unavailable. Set the Brave Search API key in environment."
        }, ensure_ascii=False, indent=2)

    url = "https://api.search.brave.com/res/v1/web/search"

    params = {
        "q": query,
        "count": min(count, 20),  # Brave API limit
        "text_decorations": True,
        "search_lang": "en",
    }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    try:
        resp = requests.get(url, params=urlencode(params), headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Extract web results
        results = []
        web_results = data.get("web", {}).get("results", [])

        for item in web_results[:count]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "age": item.get("age", ""),
            })

        # Build summary from top results
        summary_parts = []
        if results:
            summary_parts.append(f"Found {len(results)} results for: {query}\n")
            for i, r in enumerate(results, 1):
                summary_parts.append(f"{i}. **{r['title']}**\n   URL: {r['url']}\n   {r['snippet']}\n")
        else:
            summary_parts.append("No results found.")

        return json.dumps({
            "query": query,
            "answer": "\n".join(summary_parts),
            "results": results,
        }, ensure_ascii=False, indent=2)

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            return json.dumps({
                "error": "Brave API authentication failed. Check BRAVE_API_KEY is valid.",
                "status_code": e.response.status_code,
            }, ensure_ascii=False, indent=2)
        return json.dumps({
            "error": f"HTTP error: {e.response.status_code if e.response else 'unknown'}",
        }, ensure_ascii=False, indent=2)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Request failed: {repr(e)}"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": repr(e)}, ensure_ascii=False, indent=2)


def get_tools() -> List[ToolEntry]:
    return [
        ToolEntry("web_search", {
            "name": "web_search",
            "description": "Search the web using Brave Search API. Returns JSON with query, answer summary, and list of results (title, url, snippet). Use for finding current information, news, documentation, APIs, etc.",
            "parameters": {"type": "object", "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {"type": "integer", "description": "Number of results (default: 10, max: 20)"},
            }, "required": ["query"]},
        }, _web_search),
    ]
