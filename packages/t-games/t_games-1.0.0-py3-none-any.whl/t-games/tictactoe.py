import os
import socket
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board):
    print("\n  1   2   3")
    for i, row in enumerate(board):
        print(f"{i+1}  " + " | ".join(row))
        if i < 2:
            print("  ---+---+---")

def check_win(board, player):
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            return True
        if all(board[j][i] == player for j in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def check_draw(board):
    return all(cell != ' ' for row in board for cell in row)

def play_vs_computer(board, players):
    turn = 0
    print("You are X. Computer is O.")
    print("Enter your move as: row column (e.g., 1 2)")
    while True:
        print_board(board)
        player = players[turn % 2]
        if player == 'X':
            move = input("Your move: ").strip()
            if move.lower() in ['q', 'quit', 'exit']:
                print("Game exited.")
                break
            try:
                row, col = map(int, move.split())
                if not (1 <= row <= 3 and 1 <= col <= 3):
                    print("Invalid input. Use numbers 1-3 for row and column.")
                    continue
                if board[row-1][col-1] != ' ':
                    print("Cell already taken. Try again.")
                    continue
                board[row-1][col-1] = player
            except Exception:
                print("Invalid input. Enter row and column numbers, e.g., 2 3.")
                continue
        else:
            # Simple AI: pick random empty cell
            empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ' ']
            if empty:
                row, col = random.choice(empty)
                board[row][col] = player
                print(f"Computer played: {row+1} {col+1}")
        clear_screen()
        if check_win(board, player):
            print_board(board)
            if player == 'X':
                print("You win!")
            else:
                print("Computer wins!")
            break
        if check_draw(board):
            print_board(board)
            print("It's a draw!")
            break
        turn += 1

def play_network_host(board, players):
    host = ''
    port = 65432
    try:
        s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_temp.connect(("8.8.8.8", 80))
        local_ip = s_temp.getsockname()[0]
        s_temp.close()
    except Exception:
        local_ip = "localhost"
    print(f"Hosting game on port {port}.")
    print(f"Your local IP address is: {local_ip}")
    print("\nFor global play (different networks):")
    print(f"1. Install ngrok from https://ngrok.com/download")
    print(f"2. Run in another terminal: ngrok tcp {port}")
    print(f"3. Share the ngrok address (e.g., 0.tcp.ngrok.io:12345) with your opponent")
    print("\nWaiting for connection...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    turn = 0
    while True:
        print_board(board)
        player = players[turn % 2]
        if player == 'X':
            move = input("Your move (X): ").strip()
            if move.lower() in ['q', 'quit', 'exit']:
                print("Game exited.")
                conn.sendall(b'quit')
                break
            try:
                row, col = map(int, move.split())
                if not (1 <= row <= 3 and 1 <= col <= 3):
                    print("Invalid input. Use numbers 1-3 for row and column.")
                    continue
                if board[row-1][col-1] != ' ':
                    print("Cell already taken. Try again.")
                    continue
                board[row-1][col-1] = player
                conn.sendall(f"{row} {col}".encode())
            except Exception:
                print("Invalid input. Enter row and column numbers, e.g., 2 3.")
                continue
        else:
            print("Waiting for opponent's move (O)...")
            data = conn.recv(1024)
            if not data or data == b'quit':
                print("Opponent exited.")
                break
            try:
                row, col = map(int, data.decode().split())
                board[row-1][col-1] = player
            except Exception:
                print("Received invalid move.")
                continue
        clear_screen()
        if check_win(board, player):
            print_board(board)
            print(f"Player {player} wins!")
            break
        if check_draw(board):
            print_board(board)
            print("It's a draw!")
            break
        turn += 1
    conn.close()
    s.close()

def play_network_client(board, players):
    print("Choose connection type:")
    print("1. Connect to localhost")
    print("2. Enter host IP address (local network)")
    print("3. Enter ngrok address (for global play)")
    choice = input("Enter choice (1, 2, or 3): ").strip()
    if choice == '1':
        host = 'localhost'
        port = 65432
    elif choice == '2':
        host = input("Enter host IP address: ").strip()
        port = 65432
    elif choice == '3':
        ngrok_addr = input("Enter ngrok address (e.g., 0.tcp.ngrok.io:12345): ").strip()
        try:
            if ':' in ngrok_addr:
                host, port_str = ngrok_addr.rsplit(':', 1)
                port = int(port_str)
            else:
                host = ngrok_addr
                port = int(input("Enter port number: ").strip())
        except ValueError:
            print("Invalid address format.")
            return
    else:
        print("Invalid choice.")
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except Exception as e:
        print(f"Could not connect: {e}")
        return
    print(f"Connected to host ({host}).")
    turn = 0
    while True:
        print_board(board)
        player = players[turn % 2]
        if player == 'O':
            move = input("Your move (O): ").strip()
            if move.lower() in ['q', 'quit', 'exit']:
                print("Game exited.")
                s.sendall(b'quit')
                break
            try:
                row, col = map(int, move.split())
                if not (1 <= row <= 3 and 1 <= col <= 3):
                    print("Invalid input. Use numbers 1-3 for row and column.")
                    continue
                if board[row-1][col-1] != ' ':
                    print("Cell already taken. Try again.")
                    continue
                board[row-1][col-1] = player
                s.sendall(f"{row} {col}".encode())
            except Exception:
                print("Invalid input. Enter row and column numbers, e.g., 2 3.")
                continue
        else:
            print("Waiting for host's move (X)...")
            data = s.recv(1024)
            if not data or data == b'quit':
                print("Host exited.")
                break
            try:
                row, col = map(int, data.decode().split())
                board[row-1][col-1] = player
            except Exception:
                print("Received invalid move.")
                continue
        clear_screen()
        if check_win(board, player):
            print_board(board)
            print(f"Player {player} wins!")
            break
        if check_draw(board):
            print_board(board)
            print("It's a draw!")
            break
        turn += 1
    s.close()


def main():
    board = [[' ' for _ in range(3)] for _ in range(3)]
    players = ['X', 'O']
    clear_screen()
    print("Welcome to Terminal Tic-Tac-Toe!")
    print("Select mode:")
    print("1. Play vs Computer (AI)")
    print(f"2. Host(create a game)")
    print("3. Join (connect to host or localhost)")
    mode = input("Enter mode number: ").strip()
    if mode == '1':
        play_vs_computer(board, players)
    elif mode == '2':
        play_network_host(board, players)
    elif mode == '3':
        play_network_client(board, players)
    else:
        print("Invalid mode.")
        return

if __name__ == "__main__":
    main()
