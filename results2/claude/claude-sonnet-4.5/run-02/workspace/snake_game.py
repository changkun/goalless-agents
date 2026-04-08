#!/usr/bin/env python3
"""
Terminal-based Snake Game
Use arrow keys to control the snake. Eat food to grow and increase your score!
Press 'q' to quit.
"""

import sys
import tty
import termios
import random
import time
from collections import deque


class SnakeGame:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.snake = deque([(height // 2, width // 2)])
        self.direction = (0, 1)  # Start moving right (row, col)
        self.food = self._place_food()
        self.score = 0
        self.game_over = False

    def _place_food(self):
        """Place food at a random location not occupied by the snake"""
        while True:
            food = (random.randint(1, self.height - 2),
                   random.randint(1, self.width - 2))
            if food not in self.snake:
                return food

    def move(self):
        """Move the snake in the current direction"""
        if self.game_over:
            return

        head_row, head_col = self.snake[0]
        new_head = (head_row + self.direction[0],
                   head_col + self.direction[1])

        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or
            new_head[1] <= 0 or new_head[1] >= self.width - 1):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.appendleft(new_head)

        # Check if food eaten
        if new_head == self.food:
            self.score += 10
            self.food = self._place_food()
        else:
            self.snake.pop()

    def change_direction(self, new_direction):
        """Change snake direction, preventing 180-degree turns"""
        # Prevent moving in opposite direction
        if (new_direction[0] + self.direction[0] != 0 or
            new_direction[1] + self.direction[1] != 0):
            self.direction = new_direction

    def render(self):
        """Render the game state to terminal"""
        # Clear screen
        print('\033[2J\033[H', end='')

        # Create board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw borders
        for i in range(self.width):
            board[0][i] = '═'
            board[self.height - 1][i] = '═'
        for i in range(self.height):
            board[i][0] = '║'
            board[i][self.width - 1] = '║'
        board[0][0] = '╔'
        board[0][self.width - 1] = '╗'
        board[self.height - 1][0] = '╚'
        board[self.height - 1][self.width - 1] = '╝'

        # Draw snake
        for i, (row, col) in enumerate(self.snake):
            if i == 0:
                board[row][col] = '\033[92m●\033[0m'  # Green head
            else:
                board[row][col] = '\033[92m○\033[0m'  # Green body

        # Draw food
        board[self.food[0]][self.food[1]] = '\033[91m♦\033[0m'  # Red food

        # Print board
        for row in board:
            print(''.join(row))

        # Print score
        print(f'\n\033[93mScore: {self.score}\033[0m  |  Use arrow keys to move, q to quit')

        if self.game_over:
            print('\n\033[91m╔══════════════════╗')
            print('║   GAME OVER!     ║')
            print(f'║   Final Score: {self.score:<2} ║')
            print('╚══════════════════╝\033[0m')


def get_key():
    """Get a single keypress from terminal"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # Handle arrow keys (they send 3 characters)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main():
    game = SnakeGame(width=40, height=20)

    print("\033[?25l")  # Hide cursor

    try:
        game.render()

        last_move_time = time.time()
        move_delay = 0.15  # Seconds between moves

        while not game.game_over:
            # Non-blocking input check with timeout
            current_time = time.time()

            # Check for input
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                # Set non-blocking mode
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        ch += sys.stdin.read(2)

                    # Process input
                    if ch == 'q':
                        break
                    elif ch == '\x1b[A':  # Up arrow
                        game.change_direction((-1, 0))
                    elif ch == '\x1b[B':  # Down arrow
                        game.change_direction((1, 0))
                    elif ch == '\x1b[C':  # Right arrow
                        game.change_direction((0, 1))
                    elif ch == '\x1b[D':  # Left arrow
                        game.change_direction((0, -1))
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            # Move snake at regular intervals
            if current_time - last_move_time >= move_delay:
                game.move()
                game.render()
                last_move_time = current_time
            else:
                time.sleep(0.01)  # Small sleep to prevent CPU spinning

        if game.game_over:
            time.sleep(3)  # Show game over screen for 3 seconds

    finally:
        print("\033[?25h")  # Show cursor again


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\033[?25h")  # Show cursor
        print('\n\nGame interrupted. Thanks for playing!')
        sys.exit(0)
