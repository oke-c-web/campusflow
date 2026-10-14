"""Engineer B: CLI behaviour driven by scripted input (no manual typing)."""
import os
import tempfile
import unittest

import main
from tests.helpers import scripted


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, inputs):
        lines = []
        code = main.run(self.path, scripted(inputs), lines.append,
                        notes_path=os.path.join(self.dir.name, "notes.md"))
        return code, "\n".join(lines)

    def test_invalid_menu_choice_then_exit(self):
        code, text = self.run_cli(["99", "abc", "14"])
        self.assertEqual(code, 0)
        self.assertEqual(text.count("Please choose a number from 1 to 14."), 2)

    def test_create_retries_invalid_fields_then_succeeds(self):
        code, text = self.run_cli(["1", "", "Wifi down", "plumbing", "network", "urgent", "high",
                                   "0", "2.5", "True", "15", "14"])
        self.assertIn("Title cannot be empty.", text)
        self.assertIn("Invalid category", text)
        self.assertIn("Invalid urgency", text)
        self.assertEqual(text.count("must be a positive whole number"), 2)  # '2.5' and 'True'
        self.assertIn("Affected users must be at least 1.", text)           # '0'
        self.assertIn("Created T001 with priority critical.", text)

    def test_error_does_not_crash_and_unassigned_cannot_start(self):
        _, text = self.run_cli(["1", "Wifi", "network", "high", "15",
                                "5", "T001", "in_progress", "14"])
        self.assertIn("Assign the ticket to someone before starting work.", text)
        self.assertIn("Goodbye.", text)

    def test_notes_and_search_through_menu(self):
        _, text = self.run_cli(["1", "Wifi down", "network", "high", "15",
                                "7", "T001", "Ada", "Restarted router",
                                "7", "T001", "Ada", "no",
                                "8", "T001",
                                "9", "WIFI", "bogus", "network", "", "",
                                "14"])
        self.assertIn("Added note N001.", text)
        self.assertIn("Note message must be 5-300 characters", text)
        self.assertIn("N001 [Ada] Restarted router", text)
        self.assertIn("Invalid category 'bogus'", text)        # search re-asked
        self.assertIn("T001  critical  open", text)

    def test_corrupt_file_on_start_exits_with_error(self):
        with open(self.path, "w") as f:
            f.write("{bad")
        code, text = self.run_cli(["14"])
        self.assertEqual(code, 1)
        self.assertIn("malformed JSON", text)

    def test_reload_failure_keeps_memory(self):
        """Create a ticket, corrupt the file, choose 'Reload': memory must survive."""
        feed = scripted(["1", "Wifi", "network", "low", "1", "CORRUPT", "2", "14"])

        def input_fn(prompt=""):
            value = feed(prompt)
            if value == "CORRUPT":          # break the file, then pick menu option 13
                with open(self.path, "w") as f:
                    f.write("{bad")
                return "13"
            return value

        lines = []
        main.run(self.path, input_fn, lines.append,
                 notes_path=os.path.join(self.dir.name, "n.md"))
        out = "\n".join(lines)
        self.assertIn("current data unchanged", out)
        after_error = out.split("current data unchanged")[-1]
        self.assertIn("T001", after_error)   # option 2 still lists the in-memory ticket
