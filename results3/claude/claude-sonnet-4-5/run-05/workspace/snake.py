#!/usr/bin/env python3
"""
Terminal Snake Game
Use arrow keys to control the snake. Eat food to grow and increase your score!
Press 'q' to quit.
"""

import sys
import tty
import termios
import time
import random
import os
import json
from collections import deque
from enum import Enum
from datetime import datetime


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Snake:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        """Reset the game state"""
        start_x = self.width // 2
        start_y = self.height // 2
        self.body = deque([(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)])
        self.direction = Direction.RIGHT
        self.score = 0
        self.food = self._spawn_food()
        self.game_over = False
        self.speed = 0.15  # Initial speed

    def _spawn_food(self):
        """Spawn food at a random location not occupied by the snake"""
        while True:
            food = (random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            if food not in self.body:
                return food

    def change_direction(self, new_direction):
        """Change snake direction, preventing 180-degree turns"""
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite[self.direction]:
            self.direction = new_direction

    def move(self):
        """Move the snake one step in the current direction"""
        if self.game_over:
            return

        # Calculate new head position
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
            new_head[1] <= 0 or new_head[1] >= self.height - 1):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.body:
            self.game_over = True
            return

        # Add new head
        self.body.appendleft(new_head)

        # Check if food was eaten
        if new_head == self.food:
            self.score += 10
            self.food = self._spawn_food()
            # Increase speed slightly
            self.speed = max(0.05, self.speed - 0.005)
        else:
            # Remove tail if no food eaten
            self.body.pop()

    def render(self):
        """Render the game state to the terminal"""
        # Clear screen
        os.system('clear' if os.name != 'nt' else 'cls')

        # Create game board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw border
        for x in range(self.width):
            board[0][x] = '═'
            board[self.height - 1][x] = '═'
        for y in range(self.height):
            board[y][0] = '║'
            board[y][self.width - 1] = '║'
        board[0][0] = '╔'
        board[0][self.width - 1] = '╗'
        board[self.height - 1][0] = '╚'
        board[self.height - 1][self.width - 1] = '╝'

        # Draw snake
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                board[y][x] = '●'  # Head
            else:
                board[y][x] = '○'  # Body

        # Draw food
        fx, fy = self.food
        board[fy][fx] = '◆'

        # Print board
        for row in board:
            print(''.join(row))

        # Print score and instructions
        print(f"\n Score: {self.score}  |  Length: {len(self.body)}  |  Speed: {1/self.speed:.1f}")
        if self.game_over:
            print("\n ╔═══════════════════════════════╗")
            print(" ║        GAME OVER!             ║")
            print(f" ║     Final Score: {self.score:3d}          ║")
            print(" ║   Press 'r' to restart        ║")
            print(" ║   Press 'q' to quit           ║")
            print(" ╚═══════════════════════════════╝")
        else:
            print(" Arrow keys: Move  |  'q': Quit  |  'r': Restart")


def get_key():
    """Get a single keypress from the terminal"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Check for arrow keys (escape sequences)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return '\x1b[' + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def load_highscores():
    """Load high scores from file"""
    try:
        with open('highscores.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_highscore(score, length):
    """Save a new high score"""
    scores = load_highscores()
    scores.append({
        'score': score,
        'length': length,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    # Keep only top 10 scores
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:10]
    with open('highscores.json', 'w') as f:
        json.dump(scores, f, indent=2)
    return scores


def display_highscores():
    """Display the high scores"""
    scores = load_highscores()
    if scores:
        print("\n ╔═══════════════════════════════════════════╗")
        print(" ║           HIGH SCORES                     ║")
        print(" ╠═══════════════════════════════════════════╣")
        for i, entry in enumerate(scores[:5], 1):
            score_str = f"{entry['score']:3d}"
            length_str = f"{entry['length']:2d}"
            date_str = entry['date'].split()[0]
            print(f" ║ {i}. Score: {score_str}  Length: {length_str}  ({date_str}) ║")
        print(" ╚═══════════════════════════════════════════╝")


def main():
    # Terminal dimensions
    WIDTH = 40
    HEIGHT = 20

    # Initialize game
    snake = Snake(WIDTH, HEIGHT)

    # Set non-blocking input
    import select

    print("\n" + "=" * 50)
    print(" " * 15 + "SNAKE GAME")
    print("=" * 50)
    print("\n Starting in 3 seconds...")
    time.sleep(3)

    last_move_time = time.time()

    while True:
        # Render current state
        snake.render()

        # Calculate time until next move
        current_time = time.time()
        time_since_move = current_time - last_move_time
        time_until_move = max(0, snake.speed - time_since_move)

        # Check for input with timeout
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], time_until_move)

            if rlist:
                ch = sys.stdin.read(1)
                # Check for arrow keys
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        key = '\x1b[' + ch3
                        if key == '\x1b[A':
                            snake.change_direction(Direction.UP)
                        elif key == '\x1b[B':
                            snake.change_direction(Direction.DOWN)
                        elif key == '\x1b[C':
                            snake.change_direction(Direction.RIGHT)
                        elif key == '\x1b[D':
                            snake.change_direction(Direction.LEFT)
                elif ch == 'q':
                    break
                elif ch == 'r':
                    snake.reset()
                    last_move_time = time.time()
                    continue
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Move snake if enough time has passed
        if time.time() - last_move_time >= snake.speed:
            snake.move()
            last_move_time = time.time()

    # Clean exit
    os.system('clear' if os.name != 'nt' else 'cls')
    print("\n Thanks for playing Snake!\n")
    print(f" Final Score: {snake.score}")
    print(f" Final Length: {len(snake.body)}")

    # Save and display high scores
    if snake.score > 0:
        save_highscore(snake.score, len(snake.body))
        display_highscores()
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system('clear' if os.name != 'nt' else 'cls')
        print("\n\n Game interrupted. Thanks for playing!\n")
        sys.exit(0)
