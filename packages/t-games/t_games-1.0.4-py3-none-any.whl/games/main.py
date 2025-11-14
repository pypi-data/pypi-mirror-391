import os
import sys
from . import tictactoe
from . import chess as chess_module
from . import sudoku
from . import adventure


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("\n" + "="*60)
    print("TERMINAL GAMES COLLECTION".center(60))
    print("="*60)
    print("\nChoose a game to play:\n")
    print("  1. Tic-Tac-Toe")
    print("     - Play vs Computer (AI)")
    print("     - Multiplayer (Local Network or Global via ngrok)")
    print()
    print("  2. Chess")
    print("     - Play against AI")
    print("     - Classic chess with Unicode pieces")
    print()
    print("  3. Sudoku")
    print("     - Number puzzle game")
    print("     - Multiple difficulty levels")
    print()
    print("  4. Battleship")
    print("     - Classic naval combat game")
    print("     - Sink all enemy ships")
    print()
    print("  5. Text Adventure")
    print("     - Interactive fiction game")
    print("     - Explore, solve puzzles, fight dragon")
    print()
    print("  0. Exit")
    print("\n" + "="*60)

def launch_game(choice):
    clear_screen()
    
    if choice == '1':
        print("Launching Tic-Tac-Toe...\n")
        try:
            tictactoe.main()
        except ImportError:
            print("Error: tictactoe.py not found!")
        except Exception as e:
            print(f"Error launching Tic-Tac-Toe: {e}")
    
    elif choice == '2':
        print("Launching Chess...\n")
        try:
            chess_module.main()
        except Exception as e:
            print(f"Error launching Chess: {e}")
    
    elif choice == '3':
        print("Launching Sudoku...\n")
        try:
            sudoku.main()
        except ImportError:
            print("Error: sudoku.py not found!")
        except Exception as e:
            print(f"Error launching Sudoku: {e}")
    
    elif choice == '4':
        print("Launching Text Adventure...\n")
        try:
            adventure.main()
        except ImportError:
            print("Error: adventure.py not found!")
        except Exception as e:
            print(f"Error launching Text Adventure: {e}")
    
    elif choice == '0':
        clear_screen()
        print("\nThanks for playing! Goodbye!")
        sys.exit(0)
    
    else:
        print("Invalid choice. Please select a valid option.")
        input("\nPress Enter to continue...")

def main():
    while True:
        print_menu()
        choice = input("Enter your choice (0-5): ").strip()
        launch_game(choice)
        
        if choice in ['1', '2', '3', '4', '5']:
            input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)
