import unittest

from tickets import ValidationError, calculate_priority, create_ticket


class PriorityTests(unittest.TestCase):
    def test_high_12_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_2_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_low_4_is_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_1_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_boundaries(self):
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("medium", 1), "medium")


class CreateTicketTests(unittest.TestCase):
    def test_zero_users_rejected_and_nothing_stored(self):
        tickets = []
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "Wi-Fi down", "Network", "high", 0)
        self.assertEqual(tickets, [])

    def test_blank_title_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "   ", "Network", "low", 1)

    def test_invalid_urgency_and_category_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "x", "Network", "urgent", 1)
        with self.assertRaises(ValidationError):
            create_ticket([], "x", "Plumbing", "low", 1)

    def test_non_numeric_users_rejected(self):
        for bad in ("abc", "-3", "2.5", ""):
            with self.assertRaises(ValidationError):
                create_ticket([], "x", "Other", "low", bad)

    def test_case_insensitive_input_normalised(self):
        t = create_ticket([], " Lab PC ", "hARDware", "HIGH", "12")
        self.assertEqual((t["category"], t["urgency"], t["priority"]),
                         ("Hardware", "high", "critical"))

    def test_ids_unique_and_sequential(self):
        tickets = []
        a = create_ticket(tickets, "a", "Other", "low", 1)
        b = create_ticket(tickets, "b", "Other", "low", 1)
        self.assertEqual((a["id"], b["id"]), ("T001", "T002"))