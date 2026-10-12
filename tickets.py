"""Ticket creation, validation and priority calculation (Engineer A)."""

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")
STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")  # queue order


class ValidationError(ValueError):
    """Raised when user input is invalid. The message is user-friendly."""


def normalize_category(value):
    text = str(value).strip().lower()
    for category in CATEGORIES:
        if category.lower() == text:
            return category
    raise ValidationError(
        f"Invalid category '{value}'. Choose one of: {', '.join(CATEGORIES)}."
    )


def normalize_urgency(value):
    text = str(value).strip().lower()
    if text in URGENCIES:
        return text
    raise ValidationError(
        f"Invalid urgency '{value}'. Choose one of: {', '.join(URGENCIES)}."
    )


def validate_title(value):
    title = str(value).strip() if value is not None else ""
    if not title:
        raise ValidationError("Title cannot be empty.")
    return title


def validate_affected_users(value):
    if isinstance(value, bool):
        raise ValidationError("Affected users must be a positive whole number.")
    if isinstance(value, int):
        number = value
    else:
        text = str(value).strip()
        if not text.isdigit():
            raise ValidationError("Affected users must be a positive whole number.")
        number = int(text)
    if number < 1:
        raise ValidationError("Affected users must be at least 1.")
    return number


def calculate_priority(urgency, affected_users):
    """Rules are checked in order; the first match wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def generate_id(tickets):
    """Next ID based on the highest existing number, so IDs never repeat."""
    highest = 0
    for ticket in tickets:
        try:
            highest = max(highest, int(ticket["id"][1:]))
        except (KeyError, ValueError, IndexError, TypeError):
            continue
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate input, build a ticket, append it to `tickets`, and return it.

    Raises ValidationError (and leaves `tickets` untouched) on bad input.
    """
    title = validate_title(title)
    category = normalize_category(category)
    urgency = normalize_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket = {
        "id": generate_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket