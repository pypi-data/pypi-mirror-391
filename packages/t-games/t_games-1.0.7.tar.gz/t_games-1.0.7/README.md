# Terminal Games Collection 🎮

A collection of classic games playable in your terminal, built with Python.

## 🎯 Games Included

### 1. Tic-Tac-Toe
- **Play vs Computer (AI)** - Challenge a simple AI opponent
- **Multiplayer (Local Network)** - Play with friends on the same WiFi
- **Multiplayer (Global)** - Play with anyone worldwide using ngrok

### 2. Chess ♟️
- Play against an AI opponent
- Classic chess with Unicode pieces
- Standard chess rules and moves

### 3. Sudoku 🔢
- Number puzzle game with three difficulty levels
- **Easy** - 40 cells removed
- **Medium** - 50 cells removed
- **Hard** - 60 cells removed
- Hints and solution viewer available

### 4. Text Adventure 🗡️
- Interactive fiction game
- Explore a fantasy world
- Solve puzzles and defeat enemies
- Fight a dragon and find legendary treasure
- Multiple locations, items, and paths

## 🚀 Getting Started

### Installation

Install the package using pip:
```bash
pip install t-games
```

To ensure you have the latest version:
```bash
pip install --upgrade t-games
```

That's it! All dependencies (including `python-chess` for the Chess game) will be installed automatically.

### Running the Games

#### Main Menu (Recommended)
Launch the main menu to choose any game:
```bash
games
```

#### Direct Game Launch
Run individual games directly:
```bash
tictactoe       # Launch Tic-Tac-Toe directly
chess-game      # Launch Chess directly
sudoku-game     # Launch Sudoku directly
adventure-game  # Launch Text Adventure directly
```

### Development Installation

If you want to contribute or run from source:

1. Clone the repository:
```bash
git clone https://github.com/pavansai-tanguturi/t-games.git
cd t-games
```

2. Install in development mode:
```bash
pip install -e .
```

## 🎮 Game Instructions

### Tic-Tac-Toe
1. Choose your game mode:
   - **1**: Play vs Computer
   - **2**: Host a game (wait for friend)
   - **3**: Join a game (connect to host)

2. **For Network Play:**
   - **Same WiFi**: Host shares their local IP address
   - **Different Networks**: Use ngrok for global play
     ```bash
     # In a separate terminal:
     ngrok tcp 65432
     ```
   - Share the ngrok address (e.g., `0.tcp.ngrok.io:12345`) with your friend

3. Enter moves as: `row column` (e.g., `1 2`)

### Chess
- Enter moves in UCI format: `e2e4`
- Type `exit` to quit
- You play as White (uppercase pieces)
- AI plays as Black

### Sudoku
**Commands:**
- `move <row> <col> <num>` - Place a number (e.g., `move 1 1 5`)
- `remove <row> <col>` - Remove a number
- `hint` - Get a hint for an empty cell
- `solution` - View the complete solution
- `new <difficulty>` - Start a new game (easy/medium/hard)
- `quit` - Exit game

### Text Adventure
**Common Commands:**
- `north`, `south`, `east`, `west` - Move in directions
- `take <item>` - Pick up items
- `talk to <character>` - Interact with NPCs
- `fight` - Engage in combat
- `use <item>` - Use items from inventory
- `inventory` or `i` - Check your items
- `hint` - Get location-specific hints
- `help` - View available commands
- `quit` - Exit game

**Tips:**
- Buy a torch early to explore the cave
- Talk to NPCs for valuable information
- Collect items and gold throughout your journey
- The enchanted sword is essential for combat

## 🌐 Network Multiplayer Setup

### Playing on Same Network (LAN)
1. **Host** starts the game and selects "Host"
2. Host shares their **local IP address** (displayed in-game)
3. **Client** selects "Join" and enters the host's local IP
4. Play together!

### Playing Globally (Different Networks)

#### Using ngrok:
1. **Download ngrok**: https://ngrok.com/download
2. **Host** starts the game and selects "Host"
3. In a separate terminal, run:
   ```bash
   ngrok tcp 65432
   ```
4. ngrok will display a forwarding address like:
   ```
   Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:65432
   ```
5. Share the ngrok address with your friend
6. **Client** selects "Join" → "Enter ngrok address" → enters `0.tcp.ngrok.io:12345`
7. Play together from anywhere in the world!

## 📋 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: Automatically installed with pip
  - `python-chess>=1.9.0` (for Chess game)

All dependencies are managed automatically when you install via pip.

## 🎨 Features

- **Terminal-based UI** - No GUI required, runs anywhere Python is installed
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Network multiplayer** - Play with friends locally or globally
- **Multiple difficulty levels** - Suitable for all skill levels
- **Interactive gameplay** - Rich text-based experiences
- **Save-free gaming** - Jump in and play instantly

## 🛠️ Technical Details

- **Language**: Python 3
- **Network Protocol**: TCP sockets for multiplayer
- **Architecture**: Modular design with separate game files
- **Input**: Text-based command interface

## 📝 Project Structure

```
t-games/
├── games/            # Main package directory
│   ├── __init__.py   # Package initializer
│   ├── main.py       # Main launcher with game menu
│   ├── tictactoe.py  # Tic-Tac-Toe game with AI and network multiplayer
│   ├── chess.py      # Chess game with AI
│   ├── sudoku.py     # Sudoku puzzle game
│   └── adventure.py  # Text adventure game
├── setup.py          # Package configuration
├── pyproject.toml    # Build configuration
├── requirements.txt  # Python dependencies
├── LICENSE           # MIT License
└── README.md         # This file
```

## 📦 PyPI Package

This project is published on PyPI: https://pypi.org/project/t-games/

Install with: `pip install t-games`

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-game`)
3. Commit your changes (`git commit -m 'Add amazing game'`)
4. Push to the branch (`git push origin feature/amazing-game`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI**: https://pypi.org/project/t-games/
- **GitHub**: https://github.com/pavansai-tanguturi/t-games
- **Issues**: https://github.com/pavansai-tanguturi/t-games/issues

## 👥 Authors

- **Pavan Sai Tanguturi** - [@pavansai-tanguturi](https://github.com/pavansai-tanguturi)
- **Siddartha Karumuri** - [@siddardha003](https://github.com/siddardha003)

## 🎉 Have Fun!

Enjoy playing these classic games in your terminal. Whether you're challenging the AI, playing with friends locally, or connecting globally via ngrok, there's something for everyone!

---

**Made with ❤️ using Python**
