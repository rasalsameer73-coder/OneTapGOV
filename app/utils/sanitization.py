import re
import unicodedata

CONTROL_CHARACTERS = re.compile(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    # Treat NUL as a line-break (often used as separator in input streams)
    normalized = normalized.replace("\x00", "\n")
    # Remove other control chars but keep legitimate newlines and tabs
    cleaned = CONTROL_CHARACTERS.sub("", normalized)
    # Collapse multiple consecutive newlines to a single newline
    cleaned = re.sub(r"\n+", "\n", cleaned)
    # If a newline is immediately followed by spaces, convert that sequence to a single space
    # This preserves explicit newlines but turns embedded NUL->newline sequences that sit next
    # to whitespace into a natural space between tokens.
    cleaned = re.sub(r"\n\s+", " ", cleaned)
    # Strip surrounding whitespace (spaces/tabs/newlines)
    return cleaned.strip()


def normalize_email(value: str) -> str:
    return sanitize_text(value).casefold()

