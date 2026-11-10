from __future__ import annotations

import statistics
from typing import Any

from tools._shared import err


def calculate_metrics(numbers: list[float] | None = None, operation: str = "summary") -> dict[str, Any]:
    try:
        raw_list = numbers or []
        parsed: list[float] = []
        for x in raw_list:
            try:
                parsed.append(float(x))
            except (ValueError, TypeError):
                continue
                
        if not parsed:
            return {
                "tool": "calculate_metrics",
                "operation": operation,
                "count": 0,
                "result": None,
                "message": "No valid numeric data provided",
            }
            
        op = (operation or "summary").lower()
        if op == "sum":
            res = round(sum(parsed), 4)
        elif op == "mean":
            res = round(statistics.mean(parsed), 4)
        elif op == "min":
            res = min(parsed)
        elif op == "max":
            res = max(parsed)
        elif op == "change":
            if len(parsed) < 2:
                res = 0.0
            else:
                first, last = parsed[0], parsed[-1]
                res = round(((last - first) / first) * 100, 2) if first != 0 else 0.0
        else:
            res = {
                "count": len(parsed),
                "sum": round(sum(parsed), 4),
                "mean": round(statistics.mean(parsed), 4),
                "min": min(parsed),
                "max": max(parsed),
            }
            
        return {
            "tool": "calculate_metrics",
            "operation": op,
            "count": len(parsed),
            "result": res,
        }
    except Exception as exc:
        return err("calculate_metrics", exc)
