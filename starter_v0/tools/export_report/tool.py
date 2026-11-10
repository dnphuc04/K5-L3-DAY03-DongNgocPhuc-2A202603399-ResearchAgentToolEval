from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err

REPORTS_DIR = ROOT / "reports"


def export_research_report(filename: str = "", content: str = "", format_type: str = "markdown") -> dict[str, Any]:
    try:
        if not filename or not content:
            return {
                "tool": "export_research_report",
                "status": "error",
                "error": "Both filename and content are required",
            }
        
        # Sanitize filename to avoid path traversal
        clean_name = re.sub(r"[^\w\-.]", "_", Path(filename).name)
        if not clean_name:
            clean_name = "research_report"
            
        fmt = (format_type or "markdown").lower()
        if fmt == "json":
            if not clean_name.endswith(".json"):
                clean_name += ".json"
            data_to_write = json.dumps({"report": content}, ensure_ascii=False, indent=2)
        else:
            if not clean_name.endswith(".md") and not clean_name.endswith(".txt"):
                clean_name += ".md"
            data_to_write = content

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        target_path = REPORTS_DIR / clean_name
        target_path.write_text(data_to_write, encoding="utf-8")
        
        try:
            rel_path = str(target_path.relative_to(ROOT))
        except ValueError:
            rel_path = str(target_path)
            
        return {
            "tool": "export_research_report",
            "status": "saved",
            "filename": clean_name,
            "filepath": rel_path,
            "bytes_written": len(data_to_write.encode("utf-8")),
        }
    except Exception as exc:
        return err("export_research_report", exc)
