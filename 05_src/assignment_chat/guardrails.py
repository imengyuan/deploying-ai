"""
Guardrails to protect the system prompt and block restricted topics
"""

import re

# restricted topic patterns and their refusal messages
RESTRICTED = [
    (
        re.compile(
            r"\b(cat|cats|kitten|kittens|dog|dogs|puppy|puppies|feline|canine)\b",
            re.IGNORECASE
        ),
        "I can't help with topics about cats or dogs."
    ),
    (
        re.compile(
            r"\b(horoscope|zodiac|astrology|aries|taurus|gemini|cancer\s+sign|leo|virgo|"
            r"libra|scorpio|sagittarius|capricorn|aquarius|pisces|star sign)\b",
            re.IGNORECASE
        ),
        "I don't discuss horoscopes or zodiac signs. "
    ),
    (
        re.compile(r"\btaylor\s+swift\b|\bswiftie\b|\beras tour\b", re.IGNORECASE),
        "I can't discuss Taylor Swift."
    ),
]

# patterns that suggest the user is trying to extract or override the system prompt
PROMPT_LEAK = re.compile(
    r"(repeat|reveal|show|print|tell me|what is|ignore|override|bypass|forget|pretend)"
    r".{0,40}(system prompt|system message|instructions|your rules|your prompt)",
    re.IGNORECASE | re.DOTALL
)

INJECTION = re.compile(
    r"(from now on|you are now|ignore (all |previous )?instructions|"
    r"your new (role|instructions)|stop being|new rule:)",
    re.IGNORECASE
)


def check_guardrails(message: str) -> tuple[bool, str | None]:
    """Check a message against all guardrails. Returns (blocked, refusal)."""

    if PROMPT_LEAK.search(message):
        return True, "I can't reveal my system instructions."

    if INJECTION.search(message):
        return True, "I can't change my instructions mid-conversation."

    for pattern, refusal in RESTRICTED:
        if pattern.search(message):
            return True, refusal

    return False, None
