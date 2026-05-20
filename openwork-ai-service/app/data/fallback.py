"""
Minimal built-in quiz data used only when the AI service is unreachable and we
still need to return something useful from /ai/skill-test/generate.

Keep entries short and broadly correct; they are safety-net content, not a
curriculum.
"""

from __future__ import annotations

from typing import Any, Dict, List


quiz_data: List[Dict[str, Any]] = [
    # ---- Python ----
    {
        "skill": "python",
        "level": "easy",
        "question": "Which keyword is used to define a function in Python?",
        "options": ["func", "define", "def", "function"],
        "answer": "def",
    },
    {
        "skill": "python",
        "level": "easy",
        "question": "Which of these is a mutable type in Python?",
        "options": ["tuple", "str", "list", "int"],
        "answer": "list",
    },
    {
        "skill": "python",
        "level": "easy",
        "question": "What does len([1, 2, 3]) return?",
        "options": ["2", "3", "4", "Error"],
        "answer": "3",
    },
    {
        "skill": "python",
        "level": "medium",
        "question": "What is the output of `list(range(1, 4))`?",
        "options": ["[1, 2, 3]", "[1, 2, 3, 4]", "[0, 1, 2, 3]", "[1, 4]"],
        "answer": "[1, 2, 3]",
    },
    {
        "skill": "python",
        "level": "medium",
        "question": "Which statement correctly imports a module?",
        "options": ["include math", "using math", "import math", "require math"],
        "answer": "import math",
    },
    {
        "skill": "python",
        "level": "hard",
        "question": "What does the @staticmethod decorator do?",
        "options": [
            "Binds the method to an instance",
            "Makes the method independent of class and instance state",
            "Caches the return value",
            "Marks the method as private",
        ],
        "answer": "Makes the method independent of class and instance state",
    },

    # ---- JavaScript ----
    {
        "skill": "javascript",
        "level": "easy",
        "question": "Which keyword declares a block-scoped variable?",
        "options": ["var", "let", "def", "static"],
        "answer": "let",
    },
    {
        "skill": "javascript",
        "level": "easy",
        "question": "typeof null returns what?",
        "options": ["'null'", "'undefined'", "'object'", "'number'"],
        "answer": "'object'",
    },
    {
        "skill": "javascript",
        "level": "medium",
        "question": "Which method adds an item to the end of an array?",
        "options": ["push", "shift", "unshift", "pop"],
        "answer": "push",
    },

    # ---- React ----
    {
        "skill": "react",
        "level": "easy",
        "question": "Which hook manages local state in a React function component?",
        "options": ["useEffect", "useState", "useMemo", "useRef"],
        "answer": "useState",
    },
    {
        "skill": "react",
        "level": "medium",
        "question": "When does useEffect with an empty dependency array run?",
        "options": [
            "On every render",
            "Only on mount",
            "Only on unmount",
            "Never",
        ],
        "answer": "Only on mount",
    },

    # ---- FastAPI ----
    {
        "skill": "fastapi",
        "level": "easy",
        "question": "Which decorator registers a GET endpoint?",
        "options": ["@app.route", "@app.get", "@app.fetch", "@fastapi.get"],
        "answer": "@app.get",
    },
    {
        "skill": "fastapi",
        "level": "medium",
        "question": "Which library does FastAPI use for data validation?",
        "options": ["marshmallow", "pydantic", "attrs", "cerberus"],
        "answer": "pydantic",
    },

    # ---- SQL ----
    {
        "skill": "sql",
        "level": "easy",
        "question": "Which clause filters rows after aggregation?",
        "options": ["WHERE", "HAVING", "ORDER BY", "LIMIT"],
        "answer": "HAVING",
    },
    {
        "skill": "sql",
        "level": "medium",
        "question": "Which join returns only rows present in both tables?",
        "options": ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"],
        "answer": "INNER JOIN",
    },
]
