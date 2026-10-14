"""Engineer B: search and filtering."""
import unittest

from search import search_tickets, sort_by_priority
from tickets import ValidationError
from tests.helpers import make_tickets, snapshot


class SearchTests(unittest.TestCase):
    def test_case_insensitive_substring(self):
        ids = [t["id"] for t in search_tickets(make_tickets(), "WIFI")]
        self.assertEqual(ids, ["T001", "T003"])
        self.assertEqual([t["id"] for t in search_tickets(make_tickets(), "  brOKen ")], ["T002"])

    def test_combined_filters_use_and(self):
        tickets = make_tickets()
        ids = [t["id"] for t in search_tickets(tickets, "wifi", category="network", status="open")]
        self.assertEqual(ids, ["T001"])            # T003 matches title but not category
        self.assertEqual(search_tickets(tickets, "wifi", priority="low"), [])

    def test_blank_filters_not_applied(self):
        self.assertEqual(len(search_tickets(make_tickets(), "", "", " ", None)), 3)

    def test_invalid_filter_rejected(self):
        for kwargs in ({"category": "Plumbing"}, {"status": "done"}, {"priority": "urgent"}):
            with self.assertRaises(ValidationError):
                search_tickets(make_tickets(), **kwargs)

    def test_search_is_read_only(self):
        tickets = make_tickets()
        before = snapshot(tickets)
        sort_by_priority(search_tickets(tickets, "wifi"))
        self.assertEqual(tickets, before)

    def test_sorted_view_priority_then_numeric_id(self):
        tickets = make_tickets()                    # T001 critical, T002 low, T003 high
        order = [t["id"] for t in sort_by_priority(search_tickets(tickets))]
        self.assertEqual(order, ["T001", "T003", "T002"])
