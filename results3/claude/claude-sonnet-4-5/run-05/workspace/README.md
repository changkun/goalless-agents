# 🐍 Terminal Snake Game

A classic Snake game implementation for the terminal, built with Python 3.

## Features

- **Smooth gameplay** with arrow key controls
- **Dynamic difficulty** - speed increases as you grow
- **Score tracking** - earn 10 points per food item
- **High score system** - automatically saves your top 10 scores
- **Visual borders** - clean Unicode box drawing characters
- **Restart option** - press 'r' to play again

## How to Play

```bash
python3 snake.py
```

### Controls

- **Arrow Keys** - Move the snake (up, down, left, right)
- **Q** - Quit the game
- **R** - Restart the game

### Rules

1. Control the snake to eat the food (◆)
2. Each food item makes you grow longer and increases your score
3. Avoid hitting the walls (║ ═)
4. Don't run into yourself!
5. The game speeds up as you get longer - how high can you score?

## Requirements

- Python 3.x
- Unix-like terminal (Linux, macOS) or Windows with proper terminal support
- Terminal size of at least 40x25 for optimal display

## Game Elements

- `●` - Snake head
- `○` - Snake body
- `◆` - Food
- `║ ═ ╔ ╗ ╚ ╝` - Walls

Enjoy! 🎮
