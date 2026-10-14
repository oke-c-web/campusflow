"""Engineer B: reports."""
import unittest

from reports import build_report, format_report
from tests.helpers import make_tickets
from workflow import assign_ticket, change_status


class ReportTests(unittest.TestCase):
    def test_empty_report_is_zero_percent_no_crash(self):
        r = build_report([])
        self.assertEqual((r["total"], r["unresolved"], r["resolved"], r["resolution_percentage"]),
                         (0, 0, 0, 0.0))
        self.assertIn("Resolution: 0%", format_report(r))

    def test_counts_by_status_priority_category(self):
        r = build_report(make_tickets())
        self.assertEqual(r["by_priority"], {"critical": 1, "high": 1, "medium": 0, "low": 1})
        self.assertEqual(r["by_category"], {"Network": 1, "Hardware": 1, "Software": 1, "Other": 0})
        self.assertEqual(sum(r["by_status"].values()), r["total"])

    def test_resolve_and_reopen_totals_follow_current_status(self):
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Ada")
        assign_ticket(tickets, "T002", "Ada")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T002", "in_progress")
        change_status(tickets, "T001", "resolved")
        r = build_report(tickets)
        self.assertEqual((r["resolved"], r["unresolved"]), (1, 2))   # in-progress is unresolved
        self.assertEqual(r["resolution_percentage"], 33.3)
        change_status(tickets, "T001", "open")
        r = build_report(tickets)
        self.assertEqual((r["resolved"], r["unresolved"], r["resolution_percentage"]), (0, 3, 0.0))

    def test_all_resolved_is_100(self):
        tickets = make_tickets()[:1]
        assign_ticket(tickets, "T001", "Ada")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        self.assertEqual(build_report(tickets)["resolution_percentage"], 100.0)
