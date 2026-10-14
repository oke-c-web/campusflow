"""Engineer B: understanding quiz."""
import os
import tempfile
import unittest

from quiz import parse_choice, run_quiz, score_answers
from quiz_data import QUESTIONS
from tests.helpers import scripted

KEY = [q["answer"] for q in QUESTIONS]


class QuizTests(unittest.TestCase):
    def test_bank_shape_and_answer_key(self):
        self.assertEqual(len(QUESTIONS), 6)
        self.assertEqual(KEY, ["B", "C", "B", "C", "C", "B"])
        for q in QUESTIONS:
            self.assertEqual(sorted(q["options"]), ["A", "B", "C", "D"])

    def test_scoring(self):
        self.assertEqual(score_answers(QUESTIONS, KEY), 6)
        self.assertEqual(score_answers(QUESTIONS, ["A"] * 6), 0)
        self.assertEqual(score_answers(QUESTIONS, ["B", "C", "A", "A", "A", "A"]), 2)

    def test_parse_choice(self):
        self.assertEqual(parse_choice(" b "), "B")
        for bad in ("", "E", "AB", "1"):
            self.assertIsNone(parse_choice(bad))

    def test_invalid_answers_re_asked_and_score_correct(self):
        lines = []
        # invalid inputs: "x" (Q1), "" (Q3), "Z" (Q5); valid answers equal the key
        answers = ["x", "B", "c", "", "b", "C", "Z", "C", "b"]
        # explanation step: question 2, then a duplicate "2" (re-asked), then question 1
        extra = ["2", "Zero tickets must not divide", "2", "1", "Rejecting keeps data safe"]
        result = run_quiz(QUESTIONS, scripted(answers + extra), lines.append)
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["explanations"],
                         {2: "Zero tickets must not divide", 1: "Rejecting keeps data safe"})
        out = "\n".join(lines)
        self.assertEqual(out.count("Please answer A, B, C or D."), 3)
        self.assertEqual(out.count("Enter a different question number"), 1)

    def test_explanations_saved_and_not_keyword_marked(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "notes.md")
            inputs = KEY + ["1", "short", "A long enough explanation", "3", "Another real explanation"]
            result = run_quiz(QUESTIONS, scripted(inputs), lambda *_: None, notes_path=path)
            with open(path) as f:
                saved = f.read()
        self.assertIn("Question 1: A long enough explanation", saved)
        self.assertIn("Question 3: Another real explanation", saved)
        self.assertEqual(result["score"], 6)   # score depends only on the A-D answers
