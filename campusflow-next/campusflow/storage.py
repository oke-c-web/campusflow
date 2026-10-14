"""Safe JSON storage (Engineer A).

load_tickets() validates the WHOLE collection and returns a brand-new list, so a
bad file can never half-replace the data already in memory.
Old files without a "notes" field still load (notes default to []).
"""

import json
import os

from tickets import calculate_priority
from validation import (CATEGORIES, NOTE_ID_RE, STATUSES, TICKET_ID_RE, URGENCIES,
                        ValidationError, validate_affected_users, validate_note)

DEFAULT_PATH = "tickets.json"
REQUIRED_FIELDS = ("id", "title", "category", "urgency", "affected_users",
                   "priority", "status", "assigned_to")


class StorageError(Exception):
    """Raised when data cannot be loaded or saved safely."""


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _validate_notes(raw_notes, where):
    if not isinstance(raw_notes, list):
        raise StorageError(f"{where}: 'notes' must be a list.")
    seen, clean = set(), []
    for n, note in enumerate(raw_notes, start=1):
        label = f"{where}, note #{n}"
        if not isinstance(note, dict) or not all(k in note for k in ("note_id", "author", "message")):
            raise StorageError(f"{label}: needs note_id, author and message.")
        nid = note["note_id"]
        if not isinstance(nid, str) or not NOTE_ID_RE.match(nid):
            raise StorageError(f"{label}: invalid note_id '{nid}'.")
        if nid in seen:
            raise StorageError(f"{where}: duplicate note_id '{nid}'.")
        seen.add(nid)
        try:
            author, message = validate_note(note["author"], note["message"])
        except ValidationError as exc:
            raise StorageError(f"{label}: {exc}") from exc
        clean.append({"note_id": nid, "author": author, "message": message})
    return clean


def validate_collection(data):
    """Check every ticket. Return a clean copy or raise StorageError."""
    if not isinstance(data, list):
        raise StorageError("Data must be a list of tickets.")
    seen_ids, clean = set(), []
    for index, raw in enumerate(data, start=1):
        where = f"Ticket #{index}"
        if not isinstance(raw, dict):
            raise StorageError(f"{where}: must be an object.")
        missing = [f for f in REQUIRED_FIELDS if f not in raw]
        if missing:
            raise StorageError(f"{where}: missing field(s): {', '.join(missing)}.")
        tid = raw["id"]
        if not isinstance(tid, str) or not TICKET_ID_RE.match(tid):
            raise StorageError(f"{where}: invalid id '{tid}'.")
        if tid in seen_ids:
            raise StorageError(f"Duplicate ticket ID '{tid}'.")
        seen_ids.add(tid)
        where = f"Ticket {tid}"
        if not _is_text(raw["title"]):
            raise StorageError(f"{where}: title cannot be empty.")
        if raw["category"] not in CATEGORIES:
            raise StorageError(f"{where}: invalid category '{raw['category']}'.")
        if raw["urgency"] not in URGENCIES:
            raise StorageError(f"{where}: invalid urgency '{raw['urgency']}'.")
        try:
            validate_affected_users(raw["affected_users"])
        except ValidationError as exc:
            raise StorageError(f"{where}: {exc}") from exc
        if raw["status"] not in STATUSES:
            raise StorageError(f"{where}: invalid status '{raw['status']}'.")
        expected = calculate_priority(raw["urgency"], raw["affected_users"])
        if raw["priority"] != expected:
            raise StorageError(f"{where}: priority '{raw['priority']}' does not match "
                               f"urgency/affected users (expected '{expected}').")
        assigned = raw["assigned_to"]
        if assigned is not None and not _is_text(assigned):
            raise StorageError(f"{where}: assigned_to must be a name or null.")
        if raw["status"] == "in_progress" and assigned is None:
            raise StorageError(f"{where}: in-progress ticket must be assigned.")
        notes = _validate_notes(raw.get("notes", []), where)
        clean.append({
            "id": tid, "title": raw["title"].strip(), "category": raw["category"],
            "urgency": raw["urgency"], "affected_users": raw["affected_users"],
            "priority": raw["priority"], "status": raw["status"],
            "assigned_to": assigned.strip() if assigned else None, "notes": notes,
        })
    return clean


def load_tickets(path=DEFAULT_PATH):
    """Missing file -> []. Malformed or invalid file -> StorageError (file untouched)."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise StorageError(f"'{path}' contains malformed JSON ({exc}). "
                           "Fix or move the file; it was not changed.") from exc
    except OSError as exc:
        raise StorageError(f"Could not read '{path}': {exc}") from exc
    return validate_collection(data)


def save_tickets(tickets, path=DEFAULT_PATH):
    """Validate first so bad data is never written, then write atomically."""
    validate_collection(tickets)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
        os.replace(tmp, path)
    except OSError as exc:
        raise StorageError(f"Could not save to '{path}': {exc}") from exc
