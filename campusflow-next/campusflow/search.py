"""Read-only search and filtering (Engineer B)."""

from tickets import priority_sort_key, ticket_number
from validation import (normalize_category, normalize_priority, normalize_status)


def _blank(value):
    return value is None or str(value).strip() == ""


def search_tickets(tickets, text="", category=None, status=None, priority=None):
    """Return matching tickets (ID order). Every supplied filter must match (AND).

    A blank filter means 'not applied'. Invalid filter values raise
    ValidationError before anything is searched. Never modifies `tickets`.
    """
    needle = "" if _blank(text) else str(text).strip().lower()
    cat = None if _blank(category) else normalize_category(category)
    stat = None if _blank(status) else normalize_status(status)
    prio = None if _blank(priority) else normalize_priority(priority)

    results = []
    for t in tickets:
        if needle and needle not in t["title"].lower():
            continue
        if cat and t["category"] != cat:
            continue
        if stat and t["status"] != stat:
            continue
        if prio and t["priority"] != prio:
            continue
        results.append(t)
    return sorted(results, key=lambda t: ticket_number(t["id"]))


def sort_by_priority(results):
    """Optional view: priority first, then numeric ID. Returns a new list."""
    return sorted(results, key=priority_sort_key)
