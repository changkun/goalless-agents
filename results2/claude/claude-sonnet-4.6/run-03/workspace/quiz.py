#!/usr/bin/env python3
"""
Terminal trivia quiz game powered by Claude.
Usage: python quiz.py [topic] [--questions N]
"""

import anthropic
import argparse
import json
import sys
import textwrap


SYSTEM_PROMPT = """You are a trivia quiz master. Generate multiple-choice trivia questions.
Always respond with valid JSON only — no prose, no markdown fences.
"""

QUESTION_SCHEMA = """
{
  "questions": [
    {
      "question": "...",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "answer": "A",
      "explanation": "Brief explanation of why the answer is correct."
    }
  ]
}
"""


def generate_questions(client: anthropic.Anthropic, topic: str, count: int) -> list[dict]:
    prompt = (
        f"Generate exactly {count} multiple-choice trivia questions about: {topic}.\n"
        f"Mix difficulty levels. Each question must have exactly 4 options (A, B, C, D).\n"
        f"Respond with JSON matching this schema:\n{QUESTION_SCHEMA}"
    )

    print(f"\nGenerating {count} questions about \"{topic}\"", end="", flush=True)

    with client.messages.stream(
        model="claude-sonnet-4.6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        text = ""
        for chunk in stream.text_stream:
            text += chunk
            print(".", end="", flush=True)

    print(" done!\n")

    # Strip markdown fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]

    data = json.loads(text)
    return data["questions"]


def print_question(num: int, total: int, q: dict) -> None:
    width = min(80, 100)
    print(f"\n{'─' * width}")
    print(f"  Question {num}/{total}")
    print(f"{'─' * width}")
    # Wrap long questions
    for line in textwrap.wrap(q["question"], width - 2):
        print(f"  {line}")
    print()
    for letter, text in q["options"].items():
        for i, line in enumerate(textwrap.wrap(text, width - 8)):
            if i == 0:
                print(f"  [{letter}] {line}")
            else:
                print(f"       {line}")
    print()


def get_answer() -> str:
    while True:
        raw = input("Your answer (A/B/C/D): ").strip().upper()
        if raw in ("A", "B", "C", "D"):
            return raw
        print("  Please enter A, B, C, or D.")


def run_quiz(questions: list[dict]) -> None:
    total = len(questions)
    correct = 0
    wrong_answers = []

    for i, q in enumerate(questions, 1):
        print_question(i, total, q)
        user = get_answer()
        right = q["answer"].upper()

        if user == right:
            print(f"\n  ✓ Correct!\n")
            correct += 1
        else:
            print(f"\n  ✗ Wrong. The answer was [{right}] {q['options'][right]}\n")
            wrong_answers.append((i, q, user))

    # Final score
    width = min(80, 100)
    pct = correct / total * 100
    print(f"\n{'═' * width}")
    print(f"  FINAL SCORE: {correct}/{total}  ({pct:.0f}%)")

    if pct == 100:
        print("  Perfect score! Outstanding!")
    elif pct >= 80:
        print("  Great job!")
    elif pct >= 60:
        print("  Not bad — room to grow!")
    else:
        print("  Keep studying!")

    # Review wrong answers
    if wrong_answers:
        print(f"\n{'─' * width}")
        print("  REVIEW — What you missed:\n")
        for num, q, user_ans in wrong_answers:
            right = q["answer"].upper()
            print(f"  Q{num}: {q['question']}")
            print(f"  You answered:  [{user_ans}] {q['options'].get(user_ans, '?')}")
            print(f"  Correct answer:[{right}] {q['options'][right]}")
            for line in textwrap.wrap(q["explanation"], width - 4):
                print(f"    {line}")
            print()

    print(f"{'═' * width}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Terminal trivia quiz powered by Claude")
    parser.add_argument("topic", nargs="?", default="general knowledge",
                        help="Topic for the quiz (default: general knowledge)")
    parser.add_argument("--questions", "-n", type=int, default=5,
                        choices=range(3, 16), metavar="N",
                        help="Number of questions, 3–15 (default: 5)")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    try:
        questions = generate_questions(client, args.topic, args.questions)
    except json.JSONDecodeError as e:
        print(f"\nFailed to parse questions from Claude: {e}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"\nAPI error: {e}", file=sys.stderr)
        sys.exit(1)

    if not questions:
        print("No questions returned.", file=sys.stderr)
        sys.exit(1)

    run_quiz(questions)


if __name__ == "__main__":
    main()
