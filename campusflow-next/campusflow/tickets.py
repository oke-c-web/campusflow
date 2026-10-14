"""Ticket creation and priority calculation (Engineer A)."""

from validation import (  # noqa: F401  (re-exported for other modules)
    CATEGORIES, PRIORITIES, STATUSES, URGENCIES, ValidationError,
    normalize_category, normalize_urgency, validate_affected_users, validate_title,
)


def calculate_priority(urgency, affected_users):
    """Rules are checked in order; the first match wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def ticket_number(ticket_id):
    """'T010' -> 10. Numeric, so T10 sorts after T2 (text sorting would not)."""
    return int(ticket_id[1:])


def priority_sort_key(ticket):
    return (PRIORITIES.index(ticket["priority"]), ticket_number(ticket["id"]))


def generate_id(tickets):
    highest = 0
    for ticket in tickets:
        try:
            highest = max(highest, ticket_number(ticket["id"]))
        except (KeyError, ValueError, IndexError, TypeError):
            continue
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate everything first, then append. Bad input leaves `tickets` untouched."""
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
        "notes": [],
    }
    tickets.append(ticket)
    return ticket
