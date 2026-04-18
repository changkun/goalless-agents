#!/usr/bin/env python3
"""Terminal-based Snake game using curses."""

import curses
import random
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass
class GameState:
    snake: deque
    direction: Direction
    food: Tuple[int, int]
    score: int
    game_over: bool
    high_score: int


def create_food(height: int, width: int, snake: deque) -> Tuple[int, int]:
    while True:
        food = (random.randint(1, height - 2), random.randint(1, width - 2))
        if food not in snake:
            return food


def init_game(height: int, width: int, high_score: int = 0) -> GameState:
    start_y, start_x = height // 2, width // 2
    snake = deque([(start_y, start_x), (start_y, start_x + 1), (start_y, start_x + 2)])
    food = create_food(height, width, snake)
    return GameState(
        snake=snake,
        direction=Direction.LEFT,
        food=food,
        score=0,
        game_over=False,
        high_score=high_score,
    )


def move_snake(state: GameState, height: int, width: int) -> None:
    head_y, head_x = state.snake[0]
    dy, dx = state.direction.value
    new_head = (head_y + dy, head_x + dx)

    if (
        new_head[0] <= 0
        or new_head[0] >= height - 1
        or new_head[1] <= 0
        or new_head[1] >= width - 1
        or new_head in state.snake
    ):
        state.game_over = True
        return

    state.snake.appendleft(new_head)

    if new_head == state.food:
        state.score += 10
        if state.score > state.high_score:
            state.high_score = state.score
        state.food = create_food(height, width, state.snake)
    else:
        state.snake.pop()


def handle_input(state: GameState, key: int) -> bool:
    key_map = {
        curses.KEY_UP: Direction.UP,
        curses.KEY_DOWN: Direction.DOWN,
        curses.KEY_LEFT: Direction.LEFT,
        curses.KEY_RIGHT: Direction.RIGHT,
        ord("w"): Direction.UP,
        ord("s"): Direction.DOWN,
        ord("a"): Direction.LEFT,
        ord("d"): Direction.RIGHT,
    }

    if key == ord("q"):
        return False

    if key in key_map:
        new_dir = key_map[key]
        dy, dx = state.direction.value
        new_dy, new_dx = new_dir.value
        if (dy + new_dy, dx + new_dx) != (0, 0):
            state.direction = new_dir

    return True


def draw(win, state: GameState, height: int, width: int) -> None:
    win.clear()
    win.border()

    title = " SNAKE "
    win.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

    score_str = f" Score: {state.score} | High: {state.high_score} "
    win.addstr(height - 1, (width - len(score_str)) // 2, score_str)

    for i, (y, x) in enumerate(state.snake):
        char = "@" if i == 0 else "o"
        try:
            win.addch(y, x, char, curses.A_BOLD if i == 0 else 0)
        except curses.error:
            pass

    try:
        win.addch(state.food[0], state.food[1], "*", curses.A_BOLD)
    except curses.error:
        pass

    win.refresh()


def draw_game_over(win, state: GameState, height: int, width: int) -> None:
    msg1 = "GAME OVER!"
    msg2 = f"Final Score: {state.score}"
    msg3 = "Press 'r' to restart or 'q' to quit"

    center_y = height // 2
    win.addstr(center_y - 1, (width - len(msg1)) // 2, msg1, curses.A_BOLD)
    win.addstr(center_y, (width - len(msg2)) // 2, msg2)
    win.addstr(center_y + 1, (width - len(msg3)) // 2, msg3)
    win.refresh()


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    height, width = stdscr.getmaxyx()
    if height < 10 or width < 20:
        stdscr.addstr(0, 0, "Terminal too small! Need at least 20x10.")
        stdscr.refresh()
        stdscr.getch()
        return

    high_score = 0
    state = init_game(height, width, high_score)

    while True:
        if not state.game_over:
            draw(stdscr, state, height, width)
            key = stdscr.getch()

            if not handle_input(state, key):
                break

            move_snake(state, height, width)
        else:
            draw(stdscr, state, height, width)
            draw_game_over(stdscr, state, height, width)

            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == ord("r"):
                high_score = state.high_score
                state = init_game(height, width, high_score)


if __name__ == "__main__":
    print("Use arrow keys or WASD to move. Press 'q' to quit.")
    print("Starting in 1 second...")
    import time
    time.sleep(1)
    curses.wrapper(main)
