"""Engineer A: priority and validation."""
import unittest

from tickets import ValidationError, calculate_priority, create_ticket, ticket_number
from tests.helpers import snapshot


class PriorityTests(unittest.TestCase):
    def test_original_four_examples(self):
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 2), "high")
        self.assertEqual(calculate_priority("low", 4), "medium")
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_rule_order_and_boundaries(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 2), "low")


class ValidationTests(unittest.TestCase):
    def test_bad_affected_users_rejected_and_nothing_stored(self):
        for bad in (0, -1, 2.5, True, False, "12", None):
            tickets = []
            with self.assertRaises(ValidationError, msg=repr(bad)):
                create_ticket(tickets, "x", "Other", "low", bad)
            self.assertEqual(tickets, [])

    def test_blank_title_bad_category_bad_urgency(self):
        before = []
        for args in (("  ", "Network", "low", 1), ("x", "Plumbing", "low", 1),
                     ("x", "Network", "urgent", 1)):
            with self.assertRaises(ValidationError):
                create_ticket(before, *args)
        self.assertEqual(before, [])

    def test_case_and_whitespace_normalised(self):
        t = create_ticket([], "  Lab PC  ", "hARDware", "HIGH", 12)
        self.assertEqual((t["title"], t["category"], t["urgency"], t["priority"]),
                         ("Lab PC", "Hardware", "high", "critical"))

    def test_new_ticket_starts_with_empty_notes_and_open(self):
        t = create_ticket([], "x", "Other", "low", 1)
        self.assertEqual((t["notes"], t["status"], t["assigned_to"]), ([], "open", None))

    def test_ids_unique_and_numeric_ordering(self):
        tickets = []
        for _ in range(11):
            create_ticket(tickets, "x", "Other", "low", 1)
        self.assertEqual(tickets[-1]["id"], "T011")
        self.assertLess(ticket_number("T2"), ticket_number("T10"))
        self.assertGreater("T2", "T10")  # why text sorting would be wrong
