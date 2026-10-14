"""Follow-up notes (Engineer A owns these functions; Engineer B's CLI calls them)."""

from validation import NOTE_ALLOWED_STATUSES, ValidationError, validate_note
from workflow import find_ticket


def note_number(note_id):
    return int(note_id[1:])


def next_note_id(ticket):
    """Highest existing number + 1. A rejected note never reaches this line,
    so it cannot consume an ID."""
    highest = max((note_number(n["note_id"]) for n in ticket.get("notes", [])), default=0)
    return f"N{highest + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a note to an open / in-progress ticket and return the new note.

    Contract: raises ValidationError and changes nothing if the ticket is
    unknown or resolved, the author is blank, or the message is not 5-300
    characters after trimming.
    """
    ticket = find_ticket(tickets, ticket_id)
    if ticket["status"] not in NOTE_ALLOWED_STATUSES:
        raise ValidationError("Notes can only be added to open or in-progress tickets. "
                              "Reopen the ticket first.")
    author, message = validate_note(author, message)
    note = {"note_id": next_note_id(ticket), "author": author, "message": message}
    ticket["notes"].append(note)
    return note


def get_notes(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)
    return sorted(ticket.get("notes", []), key=lambda n: note_number(n["note_id"]))
