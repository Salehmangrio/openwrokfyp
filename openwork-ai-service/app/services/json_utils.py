from __future__ import annotations

import json
import re
from typing import Any


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def safe_json_extract(text: str) -> Any:
    """
    Best-effort JSON extraction from LLM output.

    Handles:
      * raw JSON
      * ```json ... ``` fenced blocks
      * JSON wrapped in leading/trailing prose
    Returns the parsed object, or None if nothing parseable is found.
    """
    if not text:
        return None

    candidate = text.strip()

    # 1. Direct parse
    try:
        return json.loads(candidate)
    except Exception:
        pass

    # 2. Fenced code block
    fence = _JSON_FENCE_RE.search(candidate)
    if fence:
        inner = fence.group(1).strip()
        try:
            return json.loads(inner)
        except Exception:
            candidate = inner  # fall through to balanced scan

    # 3. Find the first balanced JSON object/array
    for opener, closer in (("[", "]"), ("{", "}")):
        start = candidate.find(opener)
        if start == -1:
            continue
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(candidate)):
            ch = candidate[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    snippet = candidate[start : i + 1]
                    try:
                        return json.loads(snippet)
                    except Exception:
                        break
    return None
