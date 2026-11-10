from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def search_wikipedia(query: str = "", limit: int = 3) -> dict[str, Any]:
    try:
        q = (query or "").strip()
        if not q:
            return {"tool": "search_wikipedia", "query": query, "items": []}
        
        limit_val = max(1, min(10, int(limit or 3)))
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": q,
                "srlimit": limit_val,
                "format": "json",
            },
            headers={"User-Agent": "ResearchAgentToolEval/1.0 (educational lab)"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        
        items = []
        for item in search_results:
            title = item.get("title", "")
            snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
            encoded_title = title.replace(" ", "_")
            items.append({
                "title": title,
                "summary": snippet,
                "url": f"https://en.wikipedia.org/wiki/{encoded_title}",
                "source": "wikipedia.org",
                "pageid": item.get("pageid"),
            })
            
        return {"tool": "search_wikipedia", "query": q, "items": items}
    except Exception as exc:
        return err("search_wikipedia", exc)
