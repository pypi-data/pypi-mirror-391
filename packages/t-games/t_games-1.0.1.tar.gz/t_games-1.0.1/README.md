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

### 4. Battleship 🚢
- Classic naval combat game
- Place your ships strategically
- Sink all enemy ships to win
- Side-by-side board display

### 5. Text Adventure 🗡️
- Interactive fiction game
- Explore a fantasy world
- Solve puzzles and defeat enemies
- Fight a dragon and find legendary treasure
- Multiple locations, items, and paths

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone or download this repository:
```bash
cd t-games
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Games

#### Option 1: Main Menu (Recommended)
Launch the main menu to choose any game:
```bash
python main.py
```

#### Option 2: Direct Game Launch
Run individual games directly:
```bash
python tictactoe.py
python chess.py
python sudoku.py
python battleship.py
python adventure.py
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

### Battleship
- Place your ships on the grid
- Enter coordinates to fire at enemy ships
- First to sink all enemy ships wins

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

- **Python Standard Library**: `os`, `sys`, `random`, `copy`, `socket`, `time`
- **External Package**: `python-chess>=1.9.0` (for Chess game only)

All dependencies are listed in `requirements.txt`

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
├── main.py           # Main launcher with game menu
├── tictactoe.py      # Tic-Tac-Toe game
├── chess.py          # Chess game
├── sudoku.py         # Sudoku puzzle game
├── battleship.py     # Battleship game
├── adventure.py      # Text adventure game
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## 🤝 Contributing

Feel free to fork this project and add your own games or improvements!

## 📜 License

This project is open source and available for educational and personal use.

## 🎉 Have Fun!

Enjoy playing these classic games in your terminal. Whether you're challenging the AI, playing with friends locally, or connecting globally via ngrok, there's something for everyone!

---

**Made with ❤️ using Python**
