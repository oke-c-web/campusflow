"""Engineer A: safe JSON storage."""
import json
import os
import tempfile
import unittest

from notes import add_note
from storage import StorageError, load_tickets, save_tickets, validate_collection
from tickets import create_ticket
from tests.helpers import make_tickets, snapshot


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, data):
        with open(self.path, "w") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def test_missing_file_starts_empty(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_reload_preserves_notes_and_next_ids(self):
        tickets = make_tickets()
        add_note(tickets, "T001", "Ada", "Restarted the router")
        save_tickets(tickets, self.path)
        reloaded = load_tickets(self.path)
        self.assertEqual(reloaded, tickets)
        self.assertEqual(create_ticket(reloaded, "new", "Other", "low", 1)["id"], "T004")
        self.assertEqual(add_note(reloaded, "T001", "Bola", "Second note here")["note_id"], "N002")

    def test_corrupted_json_rejected_file_untouched(self):
        self.write_raw("{not json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path) as f:
            self.assertEqual(f.read(), "{not json")

    def test_duplicate_ids_rejected(self):
        tickets = make_tickets()
        tickets[1]["id"] = "T001"
        self.write_raw(tickets)
        with self.assertRaises(StorageError) as ctx:
            load_tickets(self.path)
        self.assertIn("Duplicate", str(ctx.exception))

    def test_one_bad_record_rejects_whole_load(self):
        data = snapshot(make_tickets())
        data[2]["priority"] = "low"            # inconsistent with high urgency
        for bad in (lambda d: d[0].update(affected_users=True),
                    lambda d: d[0].update(status="done"),
                    lambda d: d[0].update(category="Plumbing"),
                    lambda d: d[0].update(notes=[{"note_id": "N001", "author": "A", "message": "hi"}]),
                    lambda d: d[0].pop("title")):
            candidate = snapshot(make_tickets())
            bad(candidate)
            with self.assertRaises(StorageError):
                validate_collection(candidate)
        with self.assertRaises(StorageError):
            validate_collection(data)

    def test_failed_load_leaves_memory_unchanged(self):
        in_memory = make_tickets()
        before = snapshot(in_memory)
        self.write_raw([{"id": "T001"}])
        try:
            in_memory[:] = load_tickets(self.path)   # same pattern the CLI uses
        except StorageError:
            pass
        self.assertEqual(in_memory, before)

    def test_old_format_without_notes_still_loads(self):
        old = snapshot(make_tickets())
        for t in old:
            del t["notes"]
        self.write_raw(old)
        self.assertTrue(all(t["notes"] == [] for t in load_tickets(self.path)))

    def test_save_refuses_invalid_data(self):
        bad = make_tickets()
        bad[0]["status"] = "weird"
        with self.assertRaises(StorageError):
            save_tickets(bad, self.path)
        self.assertFalse(os.path.exists(self.path))
