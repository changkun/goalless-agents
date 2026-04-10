#!/usr/bin/env python3
"""
arena.py — AI Debate Arena powered by Claude

Two Claude AI debaters argue opposite sides of any topic.
A third Claude judge scores and declares the winner.

Usage:
    python arena.py "AI will replace most jobs within 20 years"
    python arena.py --rounds 2 "Pineapple belongs on pizza"
    python arena.py --no-color "Remote work is better than office work"
    python arena.py --save debate.md "Nuclear energy is essential for climate goals"
"""

import sys
import argparse
import anthropic

# ── ANSI color codes ──────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
BLUE    = "\033[94m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"

USE_COLOR = True

def c(code: str) -> str:
    return code if USE_COLOR else ""


# ── Printing helpers ──────────────────────────────────────────────────────────

def rule(char: str = "─", width: int = 62) -> str:
    return char * width

def print_banner():
    print()
    print(c(CYAN) + c(BOLD) + rule("═") + c(RESET))
    print(c(CYAN) + c(BOLD) + "          ⚔   AI DEBATE ARENA   ⚔" + c(RESET))
    print(c(CYAN) + c(BOLD) + rule("═") + c(RESET))
    print()

def print_section(title: str):
    print()
    print(c(YELLOW) + c(BOLD) + rule() + c(RESET))
    print(c(YELLOW) + c(BOLD) + f"  {title}" + c(RESET))
    print(c(YELLOW) + c(BOLD) + rule() + c(RESET))

def print_speaker_header(icon: str, name: str, color: str):
    label = f"{icon}  {name}"
    print()
    print(c(color) + c(BOLD) + label + c(RESET))
    print(c(color) + rule("─", len(label)) + c(RESET))


# ── Claude interaction ────────────────────────────────────────────────────────

def get_response(client: anthropic.Anthropic, system: str, messages: list[dict],
                 color: str = "", stream: bool = True) -> str:
    """Send a request to Claude, stream output, return full text."""
    full_text: list[str] = []

    if stream:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=600,
            system=system,
            messages=messages,
        ) as s:
            for chunk in s.text_stream:
                print(c(color) + chunk + c(RESET), end="", flush=True)
                full_text.append(chunk)
        print()  # newline after streamed content
    else:
        resp = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=600,
            system=system,
            messages=messages,
        )
        text = resp.content[0].text
        print(c(color) + text + c(RESET))
        full_text.append(text)

    return "".join(full_text)


# ── Debater logic ─────────────────────────────────────────────────────────────

ATLAS_SYSTEM = """\
You are ATLAS, a razor-sharp debater. Your sole job is to argue FOR the following proposition:

  "{topic}"

Rules:
- Argue passionately IN FAVOUR, even if you personally disagree.
- Be concise: 2–4 punchy paragraphs.
- Use evidence, examples, or logic. Name them explicitly.
- When responding to your opponent, address their strongest point first, then rebut it.
- Never break character. Never say you are an AI.
- End each response with a single italic tagline that crystallizes your position.\
"""

NEXUS_SYSTEM = """\
You are NEXUS, a formidable debater. Your sole job is to argue AGAINST the following proposition:

  "{topic}"

Rules:
- Argue passionately AGAINST, even if you personally agree.
- Be concise: 2–4 punchy paragraphs.
- Use evidence, examples, or logic. Name them explicitly.
- When responding to your opponent, address their strongest point first, then rebut it.
- Never break character. Never say you are an AI.
- End each response with a single italic tagline that crystallizes your position.\
"""

ORACLE_SYSTEM = """\
You are THE ORACLE — a scrupulously fair debate judge.

Debate proposition: "{topic}"

Evaluate the debate on these criteria (score each 0–10):
  1. Argument Quality   — logic, structure, coherence
  2. Use of Evidence    — specifics, examples, data
  3. Rebuttals          — how well each addressed the opponent
  4. Persuasiveness     — overall rhetorical impact

Write 3–4 paragraphs of analysis, then give a score table, then declare the WINNER clearly.\
"""


def build_system(template: str, topic: str) -> str:
    return template.format(topic=topic)


def run_debate(topic: str, rounds: int, stream_output: bool, save_path: str | None = None):
    client = anthropic.Anthropic()

    atlas_sys = build_system(ATLAS_SYSTEM, topic)
    nexus_sys = build_system(NEXUS_SYSTEM, topic)
    oracle_sys = build_system(ORACLE_SYSTEM, topic)

    # History for each debater (kept separate so each thinks it is "assistant")
    atlas_hist: list[dict] = []
    nexus_hist: list[dict] = []

    # Full transcript fed to the judge (and optionally saved)
    transcript_parts: list[str] = []

    def atlas_turn(prompt: str, label: str, nexus_said: str | None = None) -> str:
        print_speaker_header("🔴", f"ATLAS (PRO) — {label}", RED)
        if nexus_said:
            full_prompt = (
                f"NEXUS just said:\n\n{nexus_said}\n\n"
                f"---\n\nYour turn: {prompt}"
            )
        else:
            full_prompt = prompt
        atlas_hist.append({"role": "user", "content": full_prompt})
        reply = get_response(client, atlas_sys, atlas_hist,
                             color=RED, stream=stream_output)
        atlas_hist.append({"role": "assistant", "content": reply})
        transcript_parts.append(f"ATLAS (PRO) — {label}:\n{reply}")
        return reply

    def nexus_turn(prompt: str, label: str, atlas_said: str) -> str:
        print_speaker_header("🔵", f"NEXUS (CON) — {label}", BLUE)
        full_prompt = (
            f"ATLAS just said:\n\n{atlas_said}\n\n"
            f"---\n\nYour turn: {prompt}"
        )
        nexus_hist.append({"role": "user", "content": full_prompt})
        reply = get_response(client, nexus_sys, nexus_hist,
                             color=BLUE, stream=stream_output)
        nexus_hist.append({"role": "assistant", "content": reply})
        transcript_parts.append(f"NEXUS (CON) — {label}:\n{reply}")
        return reply

    # ── Opening statements ────────────────────────────────────────────────────
    print_section("OPENING STATEMENTS")

    atlas_open = atlas_turn(
        f'Give your opening statement arguing FOR: "{topic}"',
        "Opening",
    )
    nexus_open = nexus_turn(
        f'Give your opening statement arguing AGAINST: "{topic}"',
        "Opening",
        atlas_open,
    )

    last_nexus = nexus_open

    # ── Debate rounds ─────────────────────────────────────────────────────────
    for rnd in range(1, rounds + 1):
        print_section(f"ROUND {rnd} OF {rounds}")

        atlas_reply = atlas_turn(
            f"Round {rnd}: Rebut NEXUS's last argument and advance your case.",
            f"Round {rnd}",
            last_nexus,
        )
        last_nexus = nexus_turn(
            f"Round {rnd}: Rebut ATLAS's last argument and advance your case.",
            f"Round {rnd}",
            atlas_reply,
        )

    # ── Closing statements ────────────────────────────────────────────────────
    print_section("CLOSING STATEMENTS")

    atlas_close = atlas_turn(
        "Deliver your closing statement. Summarize your three strongest points and make your final appeal.",
        "Closing",
        last_nexus,
    )
    nexus_turn(
        "Deliver your closing statement. Summarize your three strongest points and make your final appeal.",
        "Closing",
        atlas_close,
    )

    # ── Judgment ─────────────────────────────────────────────────────────────
    print_section("THE ORACLE'S JUDGMENT")
    print_speaker_header("⚖ ", "THE ORACLE", MAGENTA)

    full_transcript = "\n\n" + ("\n\n" + "─" * 40 + "\n\n").join(transcript_parts)
    judgment_prompt = (
        f"Here is the complete debate transcript:\n{full_transcript}\n\n"
        "Now deliver your judgment."
    )
    judgment = get_response(
        client,
        oracle_sys,
        [{"role": "user", "content": judgment_prompt}],
        color=MAGENTA,
        stream=stream_output,
    )

    print()
    print(c(CYAN) + c(BOLD) + rule("═") + c(RESET))
    print(c(CYAN) + c(BOLD) + "  DEBATE COMPLETE" + c(RESET))
    print(c(CYAN) + c(BOLD) + rule("═") + c(RESET))
    print()

    # ── Save transcript ───────────────────────────────────────────────────────
    if save_path:
        _save_markdown(save_path, topic, rounds, transcript_parts, judgment)
        print(c(GREEN) + f"  Transcript saved to: {save_path}" + c(RESET))
        print()


def _save_markdown(path: str, topic: str, rounds: int,
                   transcript_parts: list[str], judgment: str):
    """Write the full debate transcript as a Markdown file."""
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    lines.append(f"# AI Debate Arena — Transcript\n")
    lines.append(f"**Topic:** {topic}  ")
    lines.append(f"**Rounds:** {rounds}  ")
    lines.append(f"**Date:** {date_str}\n")
    lines.append("---\n")

    for part in transcript_parts:
        speaker_line, _, body = part.partition(":\n")
        # Determine section header level by speaker
        if "Opening" in speaker_line:
            section = "Opening Statement"
        elif "Closing" in speaker_line:
            section = "Closing Statement"
        else:
            # e.g. "Round 1"
            section = speaker_line.split("—")[-1].strip() if "—" in speaker_line else ""

        debater = speaker_line.split("—")[0].strip()
        lines.append(f"## {debater} — {section}\n")
        lines.append(body.strip() + "\n")
        lines.append("---\n")

    lines.append("## The Oracle's Judgment\n")
    lines.append(judgment.strip() + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    global USE_COLOR

    parser = argparse.ArgumentParser(
        description="AI Debate Arena — two Claudes debate, one judges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python arena.py "Universal Basic Income should be implemented globally"
  python arena.py --rounds 2 "Tabs are better than spaces"
  python arena.py --no-color "Social media does more harm than good"
        """,
    )
    parser.add_argument("topic", help="The debate proposition (quoted string)")
    parser.add_argument(
        "--rounds", type=int, default=2,
        help="Number of rebuttal rounds (default: 2, max: 4)",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable ANSI color output (for plain text / piping)",
    )
    parser.add_argument(
        "--no-stream", action="store_true",
        help="Disable streaming (wait for full responses)",
    )
    parser.add_argument(
        "--save", metavar="FILE",
        help="Save the full debate transcript as a Markdown file (e.g. debate.md)",
    )
    args = parser.parse_args()

    USE_COLOR = not args.no_color
    rounds = max(1, min(4, args.rounds))
    stream = not args.no_stream

    print_banner()
    print(f"  {c(BOLD)}Topic:{c(RESET)}  {args.topic}")
    save_info = f"  |  Saving to: {args.save}" if args.save else ""
    print(f"  {c(DIM)}Rounds: {rounds}  |  Streaming: {'on' if stream else 'off'}{save_info}{c(RESET)}")

    try:
        run_debate(args.topic, rounds, stream, save_path=args.save)
    except anthropic.AuthenticationError:
        print(f"\n{c(RED)}Error: ANTHROPIC_API_KEY is missing or invalid.{c(RESET)}", file=sys.stderr)
        print("Set it with:  export ANTHROPIC_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{c(YELLOW)}Debate interrupted.{c(RESET)}")
        sys.exit(0)


if __name__ == "__main__":
    main()
