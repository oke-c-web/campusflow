"""CampusFlow Next - command-line menu (Engineer B)."""

import sys

from cli_input import ask_valid, optional, parse_affected_users
from notes import add_note, get_notes
from quiz import EXPLANATIONS_FILE, run_quiz
from reports import build_report, format_report
from search import search_tickets, sort_by_priority
from storage import DEFAULT_PATH, StorageError, load_tickets, save_tickets
from tickets import ValidationError, create_ticket
from validation import (normalize_category, normalize_priority, normalize_status,
                        normalize_urgency, validate_title)
from workflow import assign_ticket, change_status, find_ticket, get_work_queue

MENU = """
=== CampusFlow Next ===
 1. Create ticket
 2. List tickets
 3. View ticket
 4. Assign ticket
 5. Change status
 6. Open work queue
 7. Add follow-up note
 8. View ticket notes
 9. Search tickets
10. Search tickets (sorted by priority)
11. Reports
12. Understanding check (quiz)
13. Reload from file
14. Exit
"""


def show_row(t, out):
    who = t["assigned_to"] or "-"
    out(f"{t['id']}  {t['priority']:<9} {t['status']:<12} {t['category']:<9} "
        f"{who:<12} {t['title']}")


def show_ticket(t, out):
    for key in ("id", "title", "category", "urgency", "affected_users",
                "priority", "status", "assigned_to"):
        out(f"  {key:<15}: {t[key]}")
    out(f"  {'notes':<15}: {len(t['notes'])}")


def show_rows(rows, out, empty):
    if not rows:
        out(empty)
    for t in rows:
        show_row(t, out)


def _search(tickets, ask, out, sort):
    text = ask("Title contains (blank = any): ", lambda s: s)
    category = ask("Category (blank = any): ", optional(normalize_category))
    status = ask("Status (blank = any): ", optional(normalize_status))
    priority = ask("Priority (blank = any): ", optional(normalize_priority))
    results = search_tickets(tickets, text, category, status, priority)
    if sort:
        results = sort_by_priority(results)
    show_rows(results, out, "No tickets match.")


def run(path=DEFAULT_PATH, input_fn=input, output_fn=print, notes_path=EXPLANATIONS_FILE):
    out = output_fn
    try:
        tickets = load_tickets(path)
    except StorageError as err:
        out(f"ERROR: {err}")
        return 1

    def ask(prompt, parser):
        return ask_valid(input_fn, out, prompt, parser)

    while True:
        out(MENU)
        try:
            choice = input_fn("Choose an option: ").strip()
            if choice == "1":
                t = create_ticket(
                    tickets,
                    ask("Title: ", validate_title),
                    ask("Category (Network/Hardware/Software/Other): ", normalize_category),
                    ask("Urgency (low/medium/high): ", normalize_urgency),
                    ask("Affected users: ", parse_affected_users))
                save_tickets(tickets, path)
                out(f"Created {t['id']} with priority {t['priority']}.")
            elif choice == "2":
                show_rows(tickets, out, "No tickets yet.")
            elif choice == "3":
                show_ticket(find_ticket(tickets, input_fn("Ticket ID: ")), out)
            elif choice == "4":
                t = assign_ticket(tickets, input_fn("Ticket ID: "), input_fn("Staff name: "))
                save_tickets(tickets, path)
                out(f"{t['id']} assigned to {t['assigned_to']}.")
            elif choice == "5":
                t = change_status(tickets, input_fn("Ticket ID: "),
                                  input_fn("New status (open/in_progress/resolved): "))
                save_tickets(tickets, path)
                out(f"{t['id']} is now {t['status']}.")
            elif choice == "6":
                show_rows(get_work_queue(tickets), out, "Work queue is empty.")
            elif choice == "7":
                n = add_note(tickets, input_fn("Ticket ID: "),
                             input_fn("Author: "), input_fn("Message (5-300 chars): "))
                save_tickets(tickets, path)
                out(f"Added note {n['note_id']}.")
            elif choice == "8":
                notes = get_notes(tickets, input_fn("Ticket ID: "))
                if not notes:
                    out("No notes on this ticket.")
                for n in notes:
                    out(f"  {n['note_id']} [{n['author']}] {n['message']}")
            elif choice == "9":
                _search(tickets, ask, out, sort=False)
            elif choice == "10":
                _search(tickets, ask, out, sort=True)
            elif choice == "11":
                out(format_report(build_report(tickets)))
            elif choice == "12":
                run_quiz(input_fn=input_fn, output_fn=out, notes_path=notes_path)
            elif choice == "13":
                fresh = load_tickets(path)   # raises before anything changes
                tickets[:] = fresh
                out(f"Reloaded {len(tickets)} ticket(s) from {path}.")
            elif choice == "14":
                out("Goodbye.")
                return 0
            else:
                out("Please choose a number from 1 to 14.")
        except ValidationError as err:
            out(f"Error: {err}")
        except StorageError as err:
            out(f"Storage error: {err} (current data unchanged)")
        except (EOFError, KeyboardInterrupt):
            out("\nGoodbye.")
            return 0


if __name__ == "__main__":
    sys.exit(run())
