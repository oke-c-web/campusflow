"""Engineering Understanding Check - logic only (Engineer B)."""

from quiz_data import QUESTIONS

LETTERS = ("A", "B", "C", "D")
MIN_EXPLANATION_CHARS = 10
EXPLANATIONS_FILE = "learning-notes.md"


def parse_choice(text):
    """Return 'A'-'D' (any case, surrounding spaces ok) or None."""
    choice = str(text).strip().upper()
    return choice if choice in LETTERS else None


def score_answers(questions, answers):
    """One point per answer that equals the question's key."""
    return sum(1 for q, a in zip(questions, answers) if a == q["answer"])


def _ask(input_fn, output_fn, prompt, parser, error):
    while True:
        value = parser(input_fn(prompt))
        if value is not None:
            return value
        output_fn(error)


def _parse_question_number(text, count, chosen):
    text = str(text).strip()
    if text.isdigit() and 1 <= int(text) <= count and int(text) not in chosen:
        return int(text)
    return None


def _parse_explanation(text):
    text = str(text).strip()
    return text if len(text) >= MIN_EXPLANATION_CHARS else None


def save_explanations(path, explanations):
    with open(path, "a", encoding="utf-8") as f:
        for number, text in explanations.items():
            f.write(f"- Question {number}: {text}\n")


def run_quiz(questions=QUESTIONS, input_fn=input, output_fn=print, notes_path=None):
    """Ask every question, score it, then collect two written explanations.

    Explanations are never auto-marked; they are saved for mentor discussion.
    Returns {"score", "total", "answers", "explanations"}.
    """
    answers = []
    for number, q in enumerate(questions, start=1):
        output_fn(f"\nQ{number}. {q['prompt']}")
        for letter in LETTERS:
            output_fn(f"  {letter}. {q['options'][letter]}")
        answers.append(_ask(input_fn, output_fn, "Your answer (A/B/C/D): ", parse_choice,
                            "Please answer A, B, C or D."))

    score = score_answers(questions, answers)
    output_fn(f"\nScore: {score}/{len(questions)}")
    for number, (q, a) in enumerate(zip(questions, answers), start=1):
        if a != q["answer"]:
            output_fn(f"  Q{number}: you chose {a}; review this one (correct: {q['answer']}).")

    output_fn("\nPick two questions and explain, in your own words, why the answer is right.")
    explanations = {}
    for _ in range(2):
        number = _ask(input_fn, output_fn, "Question number to explain: ",
                      lambda t: _parse_question_number(t, len(questions), explanations),
                      f"Enter a different question number from 1 to {len(questions)}.")
        explanations[number] = _ask(
            input_fn, output_fn, "Your explanation: ", _parse_explanation,
            f"Please write at least {MIN_EXPLANATION_CHARS} characters.")

    if notes_path:
        save_explanations(notes_path, explanations)
        output_fn(f"Explanations saved to {notes_path} for discussion with your mentor.")
    else:
        for number, text in explanations.items():
            output_fn(f"Q{number} explanation: {text}")
    return {"score": score, "total": len(questions), "answers": answers,
            "explanations": explanations}
