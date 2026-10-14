"""Engineer A: assignment, status safety, open-only work queue."""
import unittest

from tickets import ValidationError, create_ticket
from tests.helpers import make_tickets, snapshot
from workflow import assign_ticket, change_status, get_work_queue


def resolve(tickets, tid):
    assign_ticket(tickets, tid, "Ada")
    change_status(tickets, tid, "in_progress")
    change_status(tickets, tid, "resolved")


class WorkflowTests(unittest.TestCase):
    def test_unassigned_cannot_start_and_data_unchanged(self):
        tickets = make_tickets()
        before = snapshot(tickets)
        with self.assertRaises(ValidationError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets, before)

    def test_full_workflow_and_reopen(self):
        tickets = make_tickets()
        resolve(tickets, "T001")
        self.assertEqual(tickets[0]["status"], "resolved")
        change_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "open")

    def test_resolved_cannot_be_reassigned_state_unchanged(self):
        tickets = make_tickets()
        resolve(tickets, "T001")
        before = snapshot(tickets)
        with self.assertRaises(ValidationError):
            assign_ticket(tickets, "T001", "Bola")
        self.assertEqual(tickets, before)

    def test_invalid_operations_leave_collection_identical(self):
        tickets = make_tickets()
        before = snapshot(tickets)
        for call in (lambda: assign_ticket(tickets, "T999", "Ada"),
                     lambda: assign_ticket(tickets, "T001", "   "),
                     lambda: change_status(tickets, "T001", "resolved"),
                     lambda: change_status(tickets, "T001", "finished")):
            with self.assertRaises(ValidationError):
                call()
        self.assertEqual(tickets, before)

    def test_work_queue_only_open_ordered(self):
        tickets = []
        for urgency, users in (("low", 1), ("high", 12), ("high", 2), ("high", 20), ("medium", 1)):
            create_ticket(tickets, "issue", "Other", urgency, users)  # T001..T005
        assign_ticket(tickets, "T002", "Ada")
        change_status(tickets, "T002", "in_progress")        # not open -> excluded
        resolve(tickets, "T003")                              # resolved -> excluded
        order = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(order, ["T004", "T005", "T001"])
