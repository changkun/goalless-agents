#!/usr/bin/env python3
import curses
import time
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
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

        self.height, self.width = self.stdscr.getmaxyx()
        self.height -= 2
        self.width -= 2

        self.reset_game()

    def reset_game(self):
        self.direction = Direction.RIGHT
        self.snake = deque([(self.height // 2, self.width // 2)])
        self.score = 0
        self.spawn_food()
        self.game_over = False

    def spawn_food(self):
        while True:
            self.food = (
                random.randint(1, self.height - 1),
                random.randint(1, self.width - 1)
            )
            if self.food not in self.snake:
                break

    def handle_input(self):
        try:
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif key == curses.KEY_DOWN and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif key == curses.KEY_LEFT and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif key == curses.KEY_RIGHT and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT
            elif key == ord('q'):
                return False
            elif key == ord('r') and self.game_over:
                self.reset_game()
        except:
            pass
        return True

    def update(self):
        if self.game_over:
            return

        head_y, head_x = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head_y + dy, head_x + dx)

        if (new_head[0] <= 0 or new_head[0] >= self.height or
            new_head[1] <= 0 or new_head[1] >= self.width or
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.appendleft(new_head)

        if new_head == self.food:
            self.score += 10
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.stdscr.clear()

        for y in range(self.height + 1):
            self.stdscr.addstr(y, 0, '│')
            self.stdscr.addstr(y, self.width + 1, '│')
        for x in range(self.width + 2):
            self.stdscr.addstr(0, x, '─')
            self.stdscr.addstr(self.height + 1, x, '─')
        self.stdscr.addstr(0, 0, '┌')
        self.stdscr.addstr(0, self.width + 1, '┐')
        self.stdscr.addstr(self.height + 1, 0, '└')
        self.stdscr.addstr(self.height + 1, self.width + 1, '┘')

        for i, (y, x) in enumerate(self.snake):
            char = '●' if i == 0 else '○'
            self.stdscr.addstr(y, x, char)

        self.stdscr.addstr(self.food[0], self.food[1], '◆')

        status = f" Score: {self.score} "
        self.stdscr.addstr(0, (self.width - len(status)) // 2, status)

        if self.game_over:
            msg = " GAME OVER! Press 'r' to restart or 'q' to quit "
            msg_y = self.height // 2
            msg_x = (self.width - len(msg)) // 2
            self.stdscr.addstr(msg_y, msg_x, msg, curses.A_REVERSE)

        self.stdscr.refresh()

    def run(self):
        while self.handle_input():
            self.update()
            self.draw()
            time.sleep(0.1)

def main(stdscr):
    game = SnakeGame(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)
