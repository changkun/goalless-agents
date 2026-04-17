#!/usr/bin/env python3
"""typist — a terminal typing speed test with real-time feedback."""

import curses
import random
import time
import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

WORDS_EASY = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "any", "these", "give", "day", "most", "us", "great", "find", "here",
]

WORDS_MEDIUM = [
    "about", "again", "along", "always", "around", "before", "began",
    "better", "between", "change", "children", "close", "country",
    "different", "earth", "enough", "every", "example", "family",
    "follow", "found", "group", "happen", "important", "interest",
    "large", "later", "learn", "letter", "light", "might", "money",
    "mother", "mountain", "never", "number", "often", "paper", "people",
    "picture", "place", "plant", "point", "problem", "question", "quite",
    "really", "river", "school", "second", "should", "something", "sound",
    "special", "start", "still", "story", "study", "system", "thought",
    "through", "together", "toward", "under", "until", "water", "without",
    "wonder", "world", "write", "young", "already", "another", "answer",
    "become", "behind", "believe", "brought", "building", "cannot",
    "certain", "complete", "consider", "contain", "continue", "corner",
    "develop", "during", "early", "enough", "evening", "finally",
    "general", "government", "himself", "however", "hundred", "include",
    "inside", "instead", "itself", "language", "leaving", "perhaps",
]

WORDS_HARD = [
    "acknowledge", "acquisition", "administrative", "approximately",
    "architecture", "bibliography", "bureaucratic", "catastrophe",
    "circumstantial", "collaboration", "communication", "comprehensive",
    "consciousness", "consequently", "controversial", "correspondence",
    "determination", "differentiate", "disambiguation", "distinguished",
    "electromagnetic", "encyclopedia", "entrepreneurial", "environmental",
    "establishment", "extraordinary", "fundamentally", "heterogeneous",
    "implementation", "independently", "infrastructure", "institutional",
    "interpretation", "investigation", "jurisprudence", "knowledgeable",
    "manufacturing", "Mediterranean", "miscellaneous", "nevertheless",
    "opportunities", "organizational", "parliamentary", "pharmaceutical",
    "philosophical", "predominantly", "psychological", "questionnaire",
    "reconnaissance", "recommendation", "representative", "responsibility",
    "simultaneously", "sophisticated", "supplementary", "technological",
    "telecommunication", "transformation", "unconstitutional", "understanding",
    "unfortunately", "vulnerability", "accomplishment", "announcement",
    "characteristic", "configuration", "demonstration", "disadvantage",
    "effectiveness", "experimentation", "functionality", "inappropriate",
]

QUOTES = [
    "The only way to do great work is to love what you do.",
    "In the middle of difficulty lies opportunity.",
    "Code is like humor. When you have to explain it, it is bad.",
    "First solve the problem, then write the code.",
    "Any fool can write code that a computer can understand.",
    "Experience is the name everyone gives to their mistakes.",
    "The best error message is the one that never shows up.",
    "Simplicity is the soul of efficiency.",
    "Talk is cheap. Show me the code.",
    "Programming is not about typing, it is about thinking.",
    "The most dangerous phrase is we have always done it this way.",
    "A ship in harbor is safe, but that is not what ships are built for.",
    "Do not communicate by sharing memory, share memory by communicating.",
    "Perfection is achieved not when there is nothing more to add.",
    "It is not enough to do your best, you must know what to do.",
    "Make it work, make it right, make it fast.",
    "The function of good software is to make the complex appear simple.",
    "Walking on water and developing software are easy if both are frozen.",
    "Debugging is twice as hard as writing the code in the first place.",
    "Programs must be written for people to read and only incidentally for machines to execute.",
]


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    QUOTES = "quotes"


@dataclass
class TestResult:
    wpm: float
    raw_wpm: float
    accuracy: float
    correct_chars: int
    incorrect_chars: int
    total_chars: int
    elapsed_seconds: float
    difficulty: str


@dataclass
class TypingState:
    target_text: str
    typed: list = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    finished: bool = False
    cursor_pos: int = 0

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.finished else time.time()
        return end - self.start_time

    @property
    def correct_count(self) -> int:
        return sum(
            1 for i, ch in enumerate(self.typed)
            if i < len(self.target_text) and ch == self.target_text[i]
        )

    @property
    def incorrect_count(self) -> int:
        return len(self.typed) - self.correct_count

    @property
    def wpm(self) -> float:
        if self.elapsed == 0:
            return 0.0
        return (self.correct_count / 5) / (self.elapsed / 60)

    @property
    def raw_wpm(self) -> float:
        if self.elapsed == 0:
            return 0.0
        return (len(self.typed) / 5) / (self.elapsed / 60)

    @property
    def accuracy(self) -> float:
        if not self.typed:
            return 100.0
        return (self.correct_count / len(self.typed)) * 100


HISTORY_PATH = Path.home() / ".typist_history.json"


def load_history() -> list:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_result(result: TestResult):
    history = load_history()
    history.append({
        "wpm": round(result.wpm, 1),
        "raw_wpm": round(result.raw_wpm, 1),
        "accuracy": round(result.accuracy, 1),
        "correct": result.correct_chars,
        "incorrect": result.incorrect_chars,
        "total": result.total_chars,
        "elapsed": round(result.elapsed_seconds, 1),
        "difficulty": result.difficulty,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    try:
        HISTORY_PATH.write_text(json.dumps(history, indent=2))
    except OSError:
        pass


def generate_text(difficulty: Difficulty, length: int = 50) -> str:
    if difficulty == Difficulty.QUOTES:
        return random.choice(QUOTES)
    pool = {
        Difficulty.EASY: WORDS_EASY,
        Difficulty.MEDIUM: WORDS_MEDIUM,
        Difficulty.HARD: WORDS_HARD,
    }[difficulty]
    words = [random.choice(pool) for _ in range(length)]
    return " ".join(words)


def draw_header(win, y: int, width: int):
    title = " typist "
    left_bar = "─" * ((width - len(title)) // 2 - 1)
    right_bar = "─" * (width - len(title) - len(left_bar) - 2)
    header = f"╭{left_bar}{title}{right_bar}╮"
    try:
        win.addstr(y, 0, header[:width], curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass


def draw_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    while True:
        stdscr.clear()
        draw_header(stdscr, 0, width)

        menu_items = [
            ("1", "Easy", "Common short words"),
            ("2", "Medium", "Longer everyday words"),
            ("3", "Hard", "Complex vocabulary"),
            ("4", "Quotes", "Famous programming quotes"),
            ("5", "History", "View past results"),
            ("q", "Quit", "Exit typist"),
        ]

        y = 3
        try:
            stdscr.addstr(y, 2, "Choose a mode:", curses.color_pair(5) | curses.A_BOLD)
        except curses.error:
            pass
        y += 2

        for key, label, desc in menu_items:
            try:
                stdscr.addstr(y, 4, f"[", curses.color_pair(4))
                stdscr.addstr(key, curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr("]", curses.color_pair(4))
                stdscr.addstr(f" {label:10s}", curses.color_pair(5) | curses.A_BOLD)
                stdscr.addstr(f" {desc}", curses.color_pair(4))
            except curses.error:
                pass
            y += 1

        y += 2
        try:
            footer = "─" * (width - 2)
            stdscr.addstr(y, 1, footer, curses.color_pair(4))
            y += 1
            stdscr.addstr(y, 2, "Type the highlighted text as fast and accurately as you can!", curses.color_pair(4))
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('1'):
            return Difficulty.EASY
        elif key == ord('2'):
            return Difficulty.MEDIUM
        elif key == ord('3'):
            return Difficulty.HARD
        elif key == ord('4'):
            return Difficulty.QUOTES
        elif key == ord('5'):
            draw_history(stdscr)
        elif key == ord('q') or key == 27:
            return None


def draw_history(stdscr):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    history = load_history()

    draw_header(stdscr, 0, width)

    y = 2
    try:
        stdscr.addstr(y, 2, "Recent Results", curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass
    y += 2

    if not history:
        try:
            stdscr.addstr(y, 4, "No results yet. Complete a test first!", curses.color_pair(4))
        except curses.error:
            pass
    else:
        try:
            header_fmt = f"  {'Date':20s} {'Mode':8s} {'WPM':>7s} {'Accuracy':>9s} {'Time':>6s}"
            stdscr.addstr(y, 0, header_fmt[:width], curses.color_pair(5) | curses.A_BOLD)
            y += 1
            stdscr.addstr(y, 2, "─" * min(60, width - 4), curses.color_pair(4))
            y += 1
        except curses.error:
            pass

        for entry in reversed(history[-15:]):
            if y >= height - 2:
                break
            try:
                line = f"  {entry.get('timestamp', '?'):20s} {entry.get('difficulty', '?'):8s} {entry.get('wpm', 0):7.1f} {entry.get('accuracy', 0):8.1f}% {entry.get('elapsed', 0):5.1f}s"
                wpm = entry.get('wpm', 0)
                if wpm >= 80:
                    color = curses.color_pair(2)
                elif wpm >= 50:
                    color = curses.color_pair(3)
                else:
                    color = curses.color_pair(4)
                stdscr.addstr(y, 0, line[:width], color)
            except curses.error:
                pass
            y += 1

    y = min(y + 2, height - 1)
    try:
        stdscr.addstr(y, 2, "Press any key to return...", curses.color_pair(4))
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def wrap_text(text: str, width: int) -> list:
    lines = []
    words = text.split(" ")
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        if len(test) <= width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_test(stdscr, state: TypingState, difficulty: Difficulty):
    height, width = stdscr.getmaxyx()
    usable_width = width - 6
    left_margin = 3

    stdscr.clear()
    draw_header(stdscr, 0, width)

    y = 2
    try:
        mode_str = f"Mode: {difficulty.value}"
        elapsed_str = f"Time: {state.elapsed:.1f}s"
        wpm_str = f"WPM: {state.wpm:.0f}"
        acc_str = f"Acc: {state.accuracy:.0f}%"
        stats = f"  {mode_str}  │  {elapsed_str}  │  {wpm_str}  │  {acc_str}"
        stdscr.addstr(y, 0, stats[:width], curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass

    y = 3
    try:
        stdscr.addstr(y, 1, "─" * (width - 2), curses.color_pair(4))
    except curses.error:
        pass

    text_start_y = 5
    lines = wrap_text(state.target_text, usable_width)

    flat_to_screen = []
    char_idx = 0
    for line_num, line in enumerate(lines):
        for col, ch in enumerate(line):
            flat_to_screen.append((text_start_y + line_num, left_margin + col))
        if char_idx + len(line) < len(state.target_text):
            flat_to_screen.append((text_start_y + line_num, left_margin + len(line)))
        char_idx += len(line) + 1

    cursor_y, cursor_x = text_start_y, left_margin

    for i, ch in enumerate(state.target_text):
        if i >= len(flat_to_screen):
            break
        sy, sx = flat_to_screen[i]
        if sy >= height - 4:
            break

        if i < len(state.typed):
            if state.typed[i] == ch:
                color = curses.color_pair(2) | curses.A_BOLD
            else:
                color = curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE
        elif i == len(state.typed):
            color = curses.color_pair(6) | curses.A_UNDERLINE
            cursor_y, cursor_x = sy, sx
        else:
            color = curses.color_pair(4)

        display_ch = ch if ch != " " or i < len(state.typed) else " "
        try:
            stdscr.addstr(sy, sx, display_ch, color)
        except curses.error:
            pass

    if len(state.typed) >= len(state.target_text) and len(flat_to_screen) > 0:
        last_sy, last_sx = flat_to_screen[-1]
        cursor_y, cursor_x = last_sy, last_sx + 1

    progress_y = height - 3
    try:
        stdscr.addstr(progress_y, 1, "─" * (width - 2), curses.color_pair(4))
    except curses.error:
        pass

    progress_y += 1
    progress = len(state.typed) / len(state.target_text) if state.target_text else 0
    bar_width = min(40, width - 20)
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    pct = f"{progress * 100:.0f}%"
    try:
        stdscr.addstr(progress_y, 3, "Progress: ", curses.color_pair(5))
        stdscr.addstr(bar, curses.color_pair(2))
        stdscr.addstr(f" {pct}", curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass

    hint_y = height - 1
    try:
        stdscr.addstr(hint_y, 2, "ESC to quit  │  Backspace to correct", curses.color_pair(4))
    except curses.error:
        pass

    try:
        curses.curs_set(1)
        stdscr.move(cursor_y, cursor_x)
    except curses.error:
        pass

    stdscr.refresh()


def draw_results(stdscr, state: TypingState, difficulty: Difficulty):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    draw_header(stdscr, 0, width)

    y = 3
    try:
        stdscr.addstr(y, 2, "Test Complete!", curses.color_pair(2) | curses.A_BOLD)
    except curses.error:
        pass

    y = 5
    wpm = state.wpm
    if wpm >= 100:
        wpm_color = curses.color_pair(2)
        rank = "Blazing Fast!"
    elif wpm >= 80:
        wpm_color = curses.color_pair(2)
        rank = "Excellent"
    elif wpm >= 60:
        wpm_color = curses.color_pair(3)
        rank = "Great"
    elif wpm >= 40:
        wpm_color = curses.color_pair(5)
        rank = "Good"
    elif wpm >= 20:
        wpm_color = curses.color_pair(6)
        rank = "Keep Practicing"
    else:
        wpm_color = curses.color_pair(1)
        rank = "Beginner"

    big_wpm = f"{wpm:.0f} WPM"
    try:
        stdscr.addstr(y, 4, big_wpm, wpm_color | curses.A_BOLD)
        stdscr.addstr(f"  — {rank}", curses.color_pair(5))
    except curses.error:
        pass

    y += 2
    stats = [
        ("Raw WPM", f"{state.raw_wpm:.1f}"),
        ("Net WPM", f"{state.wpm:.1f}"),
        ("Accuracy", f"{state.accuracy:.1f}%"),
        ("Correct", f"{state.correct_count}"),
        ("Mistakes", f"{state.incorrect_count}"),
        ("Characters", f"{len(state.typed)}"),
        ("Time", f"{state.elapsed:.1f}s"),
        ("Difficulty", difficulty.value),
    ]

    for label, value in stats:
        try:
            stdscr.addstr(y, 6, f"{label:>12s}: ", curses.color_pair(4))
            stdscr.addstr(value, curses.color_pair(5) | curses.A_BOLD)
        except curses.error:
            pass
        y += 1

    y += 2
    bar_width = min(40, width - 10)
    acc = state.accuracy / 100
    filled_correct = int(bar_width * acc)
    filled_wrong = bar_width - filled_correct
    try:
        stdscr.addstr(y, 4, "Accuracy: ", curses.color_pair(5))
        stdscr.addstr("█" * filled_correct, curses.color_pair(2))
        stdscr.addstr("█" * filled_wrong, curses.color_pair(1))
        stdscr.addstr(f" {state.accuracy:.1f}%", curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass

    result = TestResult(
        wpm=state.wpm,
        raw_wpm=state.raw_wpm,
        accuracy=state.accuracy,
        correct_chars=state.correct_count,
        incorrect_chars=state.incorrect_count,
        total_chars=len(state.typed),
        elapsed_seconds=state.elapsed,
        difficulty=difficulty.value,
    )
    save_result(result)

    y += 3
    try:
        stdscr.addstr(y, 2, "[r] Retry  [m] Menu  [q] Quit", curses.color_pair(6) | curses.A_BOLD)
    except curses.error:
        pass

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('r'):
            return "retry"
        elif key == ord('m'):
            return "menu"
        elif key == ord('q') or key == 27:
            return "quit"


def run_test(stdscr, difficulty: Difficulty):
    while True:
        text = generate_text(difficulty)
        state = TypingState(target_text=text)

        stdscr.nodelay(True)
        stdscr.timeout(50)

        while not state.finished:
            draw_test(stdscr, state, difficulty)

            try:
                key = stdscr.getch()
            except curses.error:
                continue

            if key == -1:
                continue

            if key == 27:
                stdscr.nodelay(False)
                return "menu"

            if state.start_time == 0 and key not in (curses.KEY_BACKSPACE, 127, 263):
                state.start_time = time.time()

            if key in (curses.KEY_BACKSPACE, 127, 263):
                if state.typed:
                    state.typed.pop()
            elif 32 <= key <= 126:
                state.typed.append(chr(key))
                if len(state.typed) >= len(state.target_text):
                    state.finished = True
                    state.end_time = time.time()

        stdscr.nodelay(False)
        stdscr.timeout(-1)

        action = draw_results(stdscr, state, difficulty)
        if action == "retry":
            continue
        elif action == "menu":
            return "menu"
        else:
            return "quit"


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, 244, -1)  # dim gray
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)


def main(stdscr):
    init_colors()

    while True:
        difficulty = draw_menu(stdscr)
        if difficulty is None:
            break
        action = run_test(stdscr, difficulty)
        if action == "quit":
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("Thanks for using typist! Your results are saved in ~/.typist_history.json")
