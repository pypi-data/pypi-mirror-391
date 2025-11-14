from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt if it exists"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get requirements from requirements.txt, fallback to hardcoded list
install_requires = read_requirements() or ["python-chess>=1.9.0"]

setup(
    name="t-games",
    version="1.0.1",
    author="pavansai-tanguturi",
    author_email="pavansaitanguturi@gmail.com",
    description="A collection of classic games playable in your terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pavansai-tanguturi/t-games",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "games=games.main:main",
            "tictactoe=games.tictactoe:main",
            "chess-game=games.chess:main",
            "sudoku-game=games.sudoku:main",
            "adventure-game=games.adventure:main",
        ],
    },
    keywords="games terminal console multiplayer chess sudoku tictactoe battleship adventure",
    project_urls={
        "Bug Reports": "https://github.com/pavansai-tanguturi/t-games/issues",
        "Source": "https://github.com/pavansai-tanguturi/t-games",
    },
)
