"""Engineer A: follow-up notes."""
import unittest

from notes import add_note, get_notes
from tickets import ValidationError
from tests.helpers import make_tickets, snapshot
from workflow import assign_ticket, change_status


class NoteTests(unittest.TestCase):
    def test_valid_notes_get_sequential_ids(self):
        tickets = make_tickets()
        a = add_note(tickets, "T001", "Ada", "Restarted the router")
        b = add_note(tickets, "t001", " Bola ", "  Checking the network switches  ")
        self.assertEqual((a["note_id"], b["note_id"]), ("N001", "N002"))
        self.assertEqual(b["message"], "Checking the network switches")
        self.assertEqual([n["note_id"] for n in get_notes(tickets, "T001")], ["N001", "N002"])

    def test_rejected_note_does_not_consume_id_or_change_data(self):
        tickets = make_tickets()
        before = snapshot(tickets)
        for author, message in (("Ada", ""), ("Ada", "abcd"), ("Ada", "x" * 301), ("  ", "valid message")):
            with self.assertRaises(ValidationError):
                add_note(tickets, "T001", author, message)
        self.assertEqual(tickets, before)
        self.assertEqual(add_note(tickets, "T001", "Ada", "valid message")["note_id"], "N001")

    def test_length_boundaries(self):
        tickets = make_tickets()
        add_note(tickets, "T001", "Ada", "12345")
        add_note(tickets, "T001", "Ada", "x" * 300)
        self.assertEqual(len(get_notes(tickets, "T001")), 2)

    def test_resolved_rejected_reopen_accepted_notes_kept(self):
        tickets = make_tickets()
        add_note(tickets, "T001", "Ada", "First update here")
        assign_ticket(tickets, "T001", "Ada")
        change_status(tickets, "T001", "in_progress")
        add_note(tickets, "T001", "Ada", "Second update here")   # in progress is allowed
        change_status(tickets, "T001", "resolved")
        with self.assertRaises(ValidationError):
            add_note(tickets, "T001", "Ada", "Too late for this")
        change_status(tickets, "T001", "open")
        self.assertEqual(add_note(tickets, "T001", "Ada", "Back again now")["note_id"], "N003")
        self.assertEqual(len(get_notes(tickets, "T001")), 3)

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(make_tickets(), "T999", "Ada", "Hello there")
