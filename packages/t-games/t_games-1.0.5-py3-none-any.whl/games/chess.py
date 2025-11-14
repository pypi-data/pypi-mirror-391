import chess
import random

def print_board(board):
    piece_symbols = {
        'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
        'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
        '.': '·', ' ': '·'
    }

    board_str = str(board).split('\n')
    print()
    print("  a b c d e f g h")
    for i, line in enumerate(board_str):
        rank = 8 - i
        pieces = line.split(' ')
        display_line = ' '.join(piece_symbols.get(p, p) for p in pieces)
        print(f"{rank} {display_line} {rank}")
    print("  a b c d e f g h\n")


def get_human_move(board):
    while True:
        move_input = input("Your move (e.g., e2e4 or exit): ").strip()
        if move_input.lower() == 'exit':
            return None
        try:
            move = chess.Move.from_uci(move_input)
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except:
            print("Invalid input. Try again.")


def get_ai_move(board):
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)


def main():
    print("Welcome to Terminal Chess!")
    print("You are playing as White (uppercase pieces). AI is Black.")
    print("Enter moves in UCI format like e2e4. Type 'exit' to quit.\n")

    board = chess.Board()

    while not board.is_game_over():
        print_board(board)

        if board.turn == chess.WHITE:
            move = get_human_move(board)
            if move is None:
                print("Game exited.")
                break
        else:
            move = get_ai_move(board)
            print(f"AI plays: {move.uci()}")

        board.push(move)

    print_board(board)
    if board.is_game_over():
        print("Game Over:", board.result())
        if board.is_checkmate():
            print("Checkmate!")
        elif board.is_stalemate():
            print("Stalemate.")
        elif board.is_insufficient_material():
            print("Draw by insufficient material.")


if __name__ == "__main__":
    main()