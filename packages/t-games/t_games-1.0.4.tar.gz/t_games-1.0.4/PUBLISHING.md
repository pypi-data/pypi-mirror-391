# Publishing to PyPI

Follow these steps to publish your package to PyPI:

## 1. Update Package Information

Edit `setup.py` and `pyproject.toml`:
- Change `author` to your name
- Change `author_email` to your email
- Change `url` to your GitHub repository URL
- Update other URLs in `project_urls`

## 2. Create PyPI Account

- Go to https://pypi.org/account/register/
- Create an account
- Verify your email

## 3. Install Build Tools

```bash
pip install --upgrade build twine
```

## 4. Build the Package

```bash
python -m build
```

This creates:
- `dist/terminal-games-collection-1.0.0.tar.gz` (source distribution)
- `dist/terminal_games_collection-1.0.0-py3-none-any.whl` (wheel distribution)

## 5. Test on TestPyPI (Recommended)

First, test your package on TestPyPI:

```bash
# Create TestPyPI account at https://test.pypi.org/account/register/

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ terminal-games-collection
```

## 6. Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## 7. Alternative: Using API Token (More Secure)

1. Go to https://pypi.org/manage/account/token/
2. Create an API token
3. Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-token-here
```

Then upload:
```bash
python -m twine upload dist/*
```

## 8. Install Your Package

After publishing, anyone can install with:

```bash
pip install terminal-games-collection
```

## 9. Run the Games

After installation, users can run:

```bash
# Main menu
terminal-games

# Or run individual games
tictactoe
chess-game
sudoku-game
adventure-game
```

## Updating the Package

1. Update version in `setup.py` and `pyproject.toml`
2. Rebuild: `python -m build`
3. Upload: `python -m twine upload dist/*`

## Package Structure

```
terminal-games-collection/
├── terminal_games/
│   ├── __init__.py
│   ├── main.py
│   ├── tictactoe.py
│   ├── chess.py
│   ├── sudoku.py
│   └── adventure.py
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
├── requirements.txt
└── .gitignore
```

## Command Line Entry Points

After installation, these commands will be available:

- `terminal-games` - Main menu to choose games
- `tictactoe` - Tic-Tac-Toe game
- `chess-game` - Chess game
- `sudoku-game` - Sudoku puzzle
- `adventure-game` - Text adventure game

## Notes

- Package name on PyPI: `terminal-games-collection`
- Import name in Python: `terminal_games`
- Ensure all files are included in `MANIFEST.in`
- Test thoroughly before publishing
- Version numbers should follow semantic versioning (MAJOR.MINOR.PATCH)
