from __future__ import annotations

import logging
import re
from typing import Tuple

from app.services.openrouter import get_llm

logger = logging.getLogger(__name__)


# --- Regex-based fast path ------------------------------------------------

# Email: conservative but catches obfuscations like "john (at) example dot com"
_EMAIL_RE = re.compile(
    r"""
    (?:
        [\w.+-]+                                   # local part
        \s*(?:@|\(at\)|\[at\]|\sat\s)\s*           # @ or obfuscated
        [\w-]+
        (?:\s*(?:\.|\(dot\)|\[dot\]|\sdot\s)\s*[\w-]+)+   # domain parts
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Phone numbers: 7+ digits, optionally with +, spaces, dashes, parens
_PHONE_RE = re.compile(
    r"(?:(?:\+|00)\d{1,3}[\s\-.]*)?(?:\(?\d{2,4}\)?[\s\-.]*){2,}\d{3,4}"
)

# Social handles / URLs
_SOCIAL_RE = re.compile(
    r"""
    (?:
        https?://\S+
        | (?:wa\.me|t\.me|telegram\.me|join\.skype\.com|discord\.gg|linkedin\.com|facebook\.com|instagram\.com|twitter\.com|x\.com|github\.com)[^\s]*
        | @[A-Za-z0-9_.]{3,}                   # @handle
        | \bskype\s*(?:id|:)\s*[\w.\-]+
        | \bwhatsapp\s*(?:number|:)?\s*\+?\d
        | \btelegram\s*(?:@|:)?\s*\w
        | \bdiscord\s*(?::|\#|id)\s*\S+
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Explicit "contact me outside the platform" intent
_OFF_PLATFORM_RE = re.compile(
    r"""
    (?:
        contact\s+me\s+(?:outside|off)\s+(?:the\s+)?(?:platform|site|openwork)
        | take\s+(?:this|it)\s+off[- ]?platform
        | skip\s+(?:the\s+)?platform
        | bypass\s+(?:the\s+)?platform
        | email\s+me\s+(?:at|on|directly)
        | text\s+me\s+(?:at|on)
        | call\s+me\s+(?:at|on)
        | reach\s+me\s+(?:at|on|directly)
        | dm\s+me\s+(?:on|at)
        | message\s+me\s+on\s+(?:whatsapp|telegram|skype|signal|discord|instagram|facebook|linkedin)
        | pay\s+me\s+(?:via|through)\s+(?:paypal|venmo|cashapp|wise|zelle|bank\s+transfer)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Words that frequently appear alongside contact sharing
_CONTACT_HINT_RE = re.compile(
    r"\b(whatsapp|wa number|telegram|skype|signal app|discord|gmail|hotmail|outlook|yahoo|proton ?mail|imessage|viber)\b",
    re.IGNORECASE,
)


# Allow-list: we treat the hosting platform itself as safe context.
_PLATFORM_ALLOWLIST = {"openwork"}


def _regex_verdict(message: str) -> Tuple[str | None, str]:
    """
    Returns (verdict, reason). Verdict is "UNSAFE" if we're confident; None means
    the regex layer is undecided and we should ask the LLM.
    """
    text = message or ""
    stripped = text.strip()
    if not stripped:
        return "SAFE", "empty message"

    # Obvious off-platform contact intent
    if _OFF_PLATFORM_RE.search(text):
        return "UNSAFE", "explicit request to contact off-platform"

    if _EMAIL_RE.search(text):
        return "UNSAFE", "email address detected"

    # Social/messaging URL or handle
    social_match = _SOCIAL_RE.search(text)
    if social_match:
        matched = social_match.group(0).lower()
        if not any(allow in matched for allow in _PLATFORM_ALLOWLIST):
            return "UNSAFE", "social/messaging handle or external link detected"

    # Phone number: only flag if >= 7 digits total (avoid flagging "I have 5 years of experience")
    phone_match = _PHONE_RE.search(text)
    if phone_match:
        digits = re.sub(r"\D", "", phone_match.group(0))
        if len(digits) >= 7:
            return "UNSAFE", "phone number detected"

    # Contact hint word alone is suspicious but not conclusive -> ask LLM
    if _CONTACT_HINT_RE.search(text):
        return None, "contact-platform keyword present; escalating to LLM"

    # Nothing suspicious at all -> safe short-circuit
    return "SAFE", "no contact indicators detected"


_SYSTEM_PROMPT = (
    "You are a strict message-safety classifier for a freelance marketplace called OpenWork. "
    "Output EXACTLY one token, uppercase, no punctuation, no explanation: SAFE or UNSAFE.\n"
    "UNSAFE if the message:\n"
    "  - shares or requests contact details (email, phone, WhatsApp, Telegram, Skype, Discord, "
    "Signal, iMessage, social handles), OR\n"
    "  - asks or suggests communicating, paying, or working outside OpenWork, OR\n"
    "  - contains links to external messaging/payment services.\n"
    "SAFE otherwise. Mentioning OpenWork itself is always SAFE."
)


def classify_message(message: str) -> Tuple[str, str]:
    """
    Returns a tuple (verdict, reason) where verdict is "SAFE" or "UNSAFE".
    Regex layer runs first and short-circuits; the LLM is only consulted when
    the regex is undecided. If the LLM call fails we fall back to SAFE with a
    note, because the regex already caught the high-confidence UNSAFE cases.
    """
    verdict, reason = _regex_verdict(message)
    if verdict is not None:
        return verdict, reason

    llm = get_llm()
    raw = llm.chat(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        fallback="SAFE",
        temperature=0.0,
        max_tokens=4,
    )
    normalized = raw.strip().upper()
    # Keep only letters to handle stray quotes/punctuation
    normalized = re.sub(r"[^A-Z]", "", normalized)
    if normalized.startswith("UNSAFE"):
        return "UNSAFE", "LLM classified as unsafe"
    if normalized.startswith("SAFE"):
        return "SAFE", reason or "LLM classified as safe"
    logger.warning("Unrecognized moderation output: %r — defaulting to SAFE", raw)
    return "SAFE", "model output unclear; defaulted to SAFE"
