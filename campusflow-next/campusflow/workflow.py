"""Assignment, status workflow and the original Open Work Queue (Engineer A)."""

from tickets import ValidationError, priority_sort_key
from validation import normalize_status, validate_staff_name

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved", "open"},
    "resolved": {"open"},  # explicit reopen only
}


def find_ticket(tickets, ticket_id):
    wanted = str(ticket_id).strip().upper()
    for ticket in tickets:
        if ticket["id"].upper() == wanted:
            return ticket
    raise ValidationError(f"Ticket '{ticket_id}' does not exist.")


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = find_ticket(tickets, ticket_id)
    name = validate_staff_name(staff_name)
    if ticket["status"] == "resolved":
        raise ValidationError("Resolved tickets cannot be reassigned. Reopen it first.")
    ticket["assigned_to"] = name
    return ticket


def change_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)
    new_status = normalize_status(new_status)
    current = ticket["status"]
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise ValidationError(f"Cannot change status from '{current}' to '{new_status}'.")
    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise ValidationError("Assign the ticket to someone before starting work.")
    ticket["status"] = new_status  # only changed after every check passed
    return ticket


def get_work_queue(tickets):
    """Original Open Work Queue: ONLY tickets whose status is 'open'.

    Order: critical > high > medium > low, then smaller numeric ID first.
    """
    return sorted((t for t in tickets if t["status"] == "open"), key=priority_sort_key)
