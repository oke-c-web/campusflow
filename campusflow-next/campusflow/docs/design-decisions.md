# Design Decisions (CampusFlow Next)

## Modules and owners
| Module | Owner | Purpose |
|---|---|---|
| validation.py | A | every validation rule, written once |
| tickets.py | A | priority calculation, ID generation, create_ticket |
| workflow.py | A | assign, status transitions, Open Work Queue |
| notes.py | A | add_note, get_notes (B's CLI calls these) |
| storage.py | A | validate whole collection, load/save JSON |
| search.py | B | read-only search + priority-sorted view |
| reports.py | B | totals, breakdowns, resolution percentage |
| cli_input.py, main.py | B | input retry helpers and menu |
| quiz.py, quiz_data.py | B | scoring logic kept separate from question bank |

## Function contracts
- Mutating functions take `tickets` first, validate **everything before changing anything**, and return the changed object (ticket or note).
- Invalid input raises `ValidationError`; invalid files raise `StorageError`. After either, the ticket collection is unchanged (tests compare a deep copy before/after).
- Only `main.py`/`quiz.py` do input/output, and they accept `input_fn`/`output_fn` so tests can script them.
- `validate_affected_users` accepts only a real `int` (not bool, float or str). `cli_input.parse_affected_users` converts typed digits to `int` first.

## Data format (backward compatible)
- Ticket: id, title, category, urgency, affected_users, priority, status, assigned_to, **notes**.
- Note: note_id (N001...), author, message. Note IDs are per ticket.
- Files saved by the old version have no `notes`; they load with `notes = []`. No migration needed.

## Rules
- Priority: critical (high AND >=10) > high (high OR >=10) > medium (medium OR >=3) > low.
- Status: open -> in_progress -> resolved; in_progress -> open; resolved -> open (explicit reopen only). in_progress needs an assignee. Resolved tickets cannot be reassigned or receive notes.
- Open Work Queue: status == open ONLY; priority order then numeric ID.
- Notes: only open/in_progress; author not blank; message 5-300 chars after trimming; a rejected note does not use an ID.
- Search: case-insensitive substring on title; category/status/priority filters combined with AND; blank = not applied; read-only.
- Report: also category counts, unresolved (open + in_progress), resolved, resolution % (0 when no tickets).
- Load: validate the whole file (structure, unique IDs, enums, priority consistency, notes) and return a new list; the CLI replaces memory only after success.
