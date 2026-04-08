# Terminal Snake Game

A classic Snake game implementation for the terminal using Python's curses library.

## Features

- **Smooth Controls**: Use WASD or arrow keys to control the snake
- **Dynamic Difficulty**: Game speed increases as you eat more food
- **Score Tracking**: Earn 10 points for each food item
- **Collision Detection**: Game ends if you hit walls or yourself
- **Clean UI**: Beautiful box-drawing characters for borders and snake

## How to Play

1. Run the game:
   ```bash
   python3 snake.py
   ```

2. Control the snake:
   - **W** or **↑**: Move up
   - **A** or **←**: Move left
   - **S** or **↓**: Move down
   - **D** or **→**: Move right
   - **Q**: Quit game

3. Objective:
   - Eat the food (★) to grow longer and increase your score
   - Avoid hitting the walls or your own body
   - Try to beat your high score!

## Requirements

- Python 3.x
- curses library (included in standard Python on Linux/Mac)

## Game Elements

- **●**: Snake head
- **○**: Snake body
- **★**: Food
- **│─┌┐└┘**: Game borders
