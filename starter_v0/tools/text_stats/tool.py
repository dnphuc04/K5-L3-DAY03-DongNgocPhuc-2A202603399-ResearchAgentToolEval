from __future__ import annotations

import re
from collections import Counter
from typing import Any

from tools._shared import err


def analyze_text_stats(text: str = "") -> dict[str, Any]:
    try:
        raw = (text or "").strip()
        if not raw:
            return {
                "tool": "analyze_text_stats",
                "word_count": 0,
                "char_count": 0,
                "sentence_count": 0,
                "reading_time_min": 0.0,
                "top_words": [],
            }
        words = re.findall(r"\b\w+\b", raw.lower())
        sentences = [s.strip() for s in re.split(r"[.!?]+", raw) if s.strip()]
        
        # Filter common stop words
        stopwords = {"the", "a", "an", "in", "on", "at", "and", "or", "of", "to", "for", "is", "are", "was", "were", "it", "this", "that", "và", "là", "của", "các", "có", "được", "trong", "cho", "với", "những"}
        filtered_words = [w for w in words if len(w) > 2 and w not in stopwords]
        counts = Counter(filtered_words).most_common(5)
        top_words = [{"word": word, "count": count} for word, count in counts]
        
        word_count = len(words)
        char_count = len(raw)
        sentence_count = len(sentences)
        # Average reading speed ~ 200 words per minute
        reading_time = round(word_count / 200.0, 2)
        
        return {
            "tool": "analyze_text_stats",
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "reading_time_min": reading_time,
            "top_words": top_words,
        }
    except Exception as exc:
        return err("analyze_text_stats", exc)
