#!/usr/bin/env python3
"""
Terminal-based Snake Game
Use arrow keys or WASD to control the snake. Eat food to grow and increase score.
Don't hit the walls or yourself!
"""

import curses
import random
from collections import deque
from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.game_height = self.height - 3
        self.game_width = self.width - 2

        # Initialize snake in the center
        start_y = self.game_height // 2
        start_x = self.game_width // 2
        self.snake = deque([(start_y, start_x)])
        self.direction = Direction.RIGHT

        # Game state
        self.score = 0
        self.game_over = False
        self.food = self._spawn_food()

        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(100)  # Refresh rate (ms)

    def _spawn_food(self):
        """Spawn food at a random position not occupied by snake"""
        while True:
            food = (
                random.randint(1, self.game_height - 1),
                random.randint(1, self.game_width - 1)
            )
            if food not in self.snake:
                return food

    def _draw_border(self):
        """Draw game border"""
        for y in range(self.game_height + 1):
            self.stdscr.addch(y, 0, '│')
            self.stdscr.addch(y, self.game_width + 1, '│')

        for x in range(self.game_width + 2):
            self.stdscr.addch(0, x, '─')
            self.stdscr.addch(self.game_height, x, '─')

        self.stdscr.addch(0, 0, '┌')
        self.stdscr.addch(0, self.game_width + 1, '┐')
        self.stdscr.addch(self.game_height, 0, '└')
        self.stdscr.addch(self.game_height, self.game_width + 1, '┘')

    def _draw_snake(self):
        """Draw the snake"""
        for i, (y, x) in enumerate(self.snake):
            if i == 0:  # Head
                self.stdscr.addch(y, x, '●', curses.A_BOLD)
            else:
                self.stdscr.addch(y, x, '○')

    def _draw_food(self):
        """Draw the food"""
        y, x = self.food
        self.stdscr.addch(y, x, '★', curses.A_BOLD)

    def _draw_score(self):
        """Draw score and instructions"""
        score_text = f" Score: {self.score} "
        info_text = " Use WASD or Arrow Keys | Q to quit "

        self.stdscr.addstr(self.game_height + 1, 1, score_text, curses.A_BOLD)
        self.stdscr.addstr(self.game_height + 2, 1, info_text)

    def _handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()
        except:
            return

        # Map keys to directions
        key_map = {
            curses.KEY_UP: Direction.UP,
            ord('w'): Direction.UP,
            ord('W'): Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            ord('s'): Direction.DOWN,
            ord('S'): Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            ord('a'): Direction.LEFT,
            ord('A'): Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
            ord('d'): Direction.RIGHT,
            ord('D'): Direction.RIGHT,
        }

        if key in [ord('q'), ord('Q')]:
            self.game_over = True
            return

        if key in key_map:
            new_direction = key_map[key]
            # Prevent reversing into itself
            opposite = {
                Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT,
            }
            if new_direction != opposite[self.direction]:
                self.direction = new_direction

    def _update(self):
        """Update game state"""
        # Calculate new head position
        head_y, head_x = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head_y + dy, head_x + dx)

        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.game_height or
            new_head[1] <= 0 or new_head[1] >= self.game_width):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Move snake
        self.snake.appendleft(new_head)

        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.food = self._spawn_food()
            # Speed up slightly
            current_delay = self.stdscr.gettimeout()
            new_delay = max(50, current_delay - 2)
            self.stdscr.timeout(new_delay)
        else:
            # Remove tail if not eating
            self.snake.pop()

    def _draw(self):
        """Draw everything"""
        self.stdscr.clear()
        self._draw_border()
        self._draw_snake()
        self._draw_food()
        self._draw_score()
        self.stdscr.refresh()

    def _show_game_over(self):
        """Show game over screen"""
        self.stdscr.clear()

        messages = [
            "┌─────────────────────────┐",
            "│      GAME OVER!         │",
            "├─────────────────────────┤",
            f"│   Final Score: {self.score:<8} │",
            "├─────────────────────────┤",
            "│  Press any key to exit  │",
            "└─────────────────────────┘",
        ]

        start_y = self.height // 2 - len(messages) // 2
        start_x = self.width // 2 - len(messages[0]) // 2

        for i, msg in enumerate(messages):
            self.stdscr.addstr(start_y + i, start_x, msg, curses.A_BOLD)

        self.stdscr.refresh()
        self.stdscr.nodelay(False)
        self.stdscr.getch()

    def run(self):
        """Main game loop"""
        while not self.game_over:
            self._handle_input()
            self._update()
            self._draw()

        self._show_game_over()


def main(stdscr):
    game = SnakeGame(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)
