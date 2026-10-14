"""Centralised validation rules (Engineer A).

Every rule lives here once, so create / assign / status / notes / storage all
agree. Validators return the cleaned value or raise ValidationError.
"""

import re

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")
STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")  # queue order

TICKET_ID_RE = re.compile(r"^T\d{3,}$")
NOTE_ID_RE = re.compile(r"^N\d{3,}$")
NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300
NOTE_ALLOWED_STATUSES = ("open", "in_progress")


class ValidationError(ValueError):
    """Raised when input is invalid. The message is user-friendly."""


def _clean_text(value):
    return str(value).strip() if value is not None else ""


def normalize_category(value):
    text = _clean_text(value).lower()
    for category in CATEGORIES:
        if category.lower() == text:
            return category
    raise ValidationError(
        f"Invalid category '{value}'. Choose one of: {', '.join(CATEGORIES)}.")


def normalize_urgency(value):
    text = _clean_text(value).lower()
    if text in URGENCIES:
        return text
    raise ValidationError(
        f"Invalid urgency '{value}'. Choose one of: {', '.join(URGENCIES)}.")


def normalize_status(value):
    text = _clean_text(value).lower().replace(" ", "_").replace("-", "_")
    if text in STATUSES:
        return text
    raise ValidationError(
        f"Invalid status '{value}'. Choose one of: {', '.join(STATUSES)}.")


def normalize_priority(value):
    text = _clean_text(value).lower()
    if text in PRIORITIES:
        return text
    raise ValidationError(
        f"Invalid priority '{value}'. Choose one of: {', '.join(PRIORITIES)}.")


def validate_title(value):
    title = _clean_text(value)
    if not title:
        raise ValidationError("Title cannot be empty.")
    return title


def validate_affected_users(value):
    """Strictly a positive int. bool, float and str are all rejected.

    bool must be checked first because isinstance(True, int) is True in Python.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("Affected users must be a positive whole number.")
    if value < 1:
        raise ValidationError("Affected users must be at least 1.")
    return value


def validate_staff_name(value, label="Staff name"):
    name = _clean_text(value)
    if not name:
        raise ValidationError(f"{label} cannot be empty.")
    return name


def validate_ticket_id_format(value):
    text = _clean_text(value).upper()
    if not TICKET_ID_RE.match(text):
        raise ValidationError(f"'{value}' is not a valid ticket ID (example: T001).")
    return text


def validate_note(author, message):
    author = validate_staff_name(author, "Author")
    message = _clean_text(message)
    if not NOTE_MIN_LENGTH <= len(message) <= NOTE_MAX_LENGTH:
        raise ValidationError(
            f"Note message must be {NOTE_MIN_LENGTH}-{NOTE_MAX_LENGTH} characters "
            f"(got {len(message)}).")
    return author, message
