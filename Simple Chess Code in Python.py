import random

# Chess board and initial setup
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],  # 1st rank (black)
    ["p", "p", "p", "p", "p", "p", "p", "p"],  # 2nd rank (black pawns)
    [".", ".", ".", ".", ".", ".", ".", "."],  # 3rd rank
    [".", ".", ".", ".", ".", ".", ".", "."],  # 4th rank
    [".", ".", ".", ".", ".", ".", ".", "."],  # 5th rank
    [".", ".", ".", ".", ".", ".", ".", "."],  # 6th rank
    ["P", "P", "P", "P", "P", "P", "P", "P"],  # 7th rank (white pawns)
    ["R", "N", "B", "Q", "K", "B", "N", "R"]   # 8th rank (white)
]

castling_rights = {"K": True, "Q": True, "k": True, "q": True}  # Castling rights
en_passant_target = None  # En passant target square
promotion_choices = ["q", "r", "b", "n"]  # Possible pieces for pawn promotion

def print_board(board):
    print("  a b c d e f g h")
    for i, row in enumerate(board):
        print(f"{8 - i} {' '.join(row)}")
    print()

def is_king_in_check(board, color):
    king = "K" if color == "white" else "k"
    king_pos = None
    for x in range(8):
        for y in range(8):
            if board[x][y] == king:
                king_pos = (x, y)
                break
    if not king_pos:
        return False  # King not found on the board

    opponent_color = "black" if color == "white" else "white"
    moves = generate_valid_moves(board, opponent_color, include_checks=True)
    return any(move[1] == king_pos for move in moves)

def is_valid_move(board, start_pos, end_pos, color):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    piece = board[start_x][start_y]

    if piece == "." or (color == "white" and piece.islower()) or (color == "black" and piece.isupper()):
        return False  # Empty square or not own piece

    # Piece movement logic
    if piece.lower() == "p":  # Pawn
        direction = -1 if piece.isupper() else 1
        start_rank = 6 if piece.isupper() else 1
        if start_y == end_y and board[end_x][end_y] == ".":
            if (end_x - start_x) == direction:
                return True
            if (start_x == start_rank and (end_x - start_x) == 2 * direction and board[start_x + direction][end_y] == "."):
                return True
        if abs(start_y - end_y) == 1 and (end_x - start_x) == direction:
            if board[end_x][end_y] != "." or (end_pos == en_passant_target):
                return True
    elif piece.lower() == "r":  # Rook
        if start_x == end_x or start_y == end_y:
            return is_path_clear(board, start_pos, end_pos)
    elif piece.lower() == "n":  # Knight
        if (abs(start_x - end_x), abs(start_y - end_y)) in [(2, 1), (1, 2)]:
            return True
    elif piece.lower() == "b":  # Bishop
        if abs(start_x - end_x) == abs(start_y - end_y):
            return is_path_clear(board, start_pos, end_pos)
    elif piece.lower() == "q":  # Queen
        if start_x == end_x or start_y == end_y or abs(start_x - end_x) == abs(start_y - end_y):
            return is_path_clear(board, start_pos, end_pos)
    elif piece.lower() == "k":  # King
        if max(abs(start_x - end_x), abs(start_y - end_y)) == 1:
            return True
        if abs(start_y - end_y) == 2 and start_x == end_x:  # Castling
            return is_castling_valid(board, start_pos, end_pos, color)
    return False

def is_path_clear(board, start_pos, end_pos):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = (x2 - x1) and (1 if x2 > x1 else -1)
    dy = (y2 - y1) and (1 if y2 > y1 else -1)
    x, y = x1 + dx, y1 + dy
    while (x, y) != (x2, y2):
        if board[x][y] != ".":
            return False
        x, y = x + dx, y + dy
    return True

def is_castling_valid(board, start_pos, end_pos, color):
    king_start_y = 4
    rook_start_y = 0 if end_pos[1] < start_pos[1] else 7
    rook_end_y = king_start_y - 1 if rook_start_y == 0 else king_start_y + 1

    king_row = 7 if color == "white" else 0
    if start_pos != (king_row, king_start_y) or board[king_row][rook_start_y].lower() != "r":
        return False
    if any(board[king_row][min(start_pos[1], rook_start_y) + 1:max(start_pos[1], rook_start_y)]):
        return False
    return True

def generate_valid_moves(board, color, include_checks=False):
    moves = []
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if (color == "white" and piece.isupper()) or (color == "black" and piece.islower()):
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < 8 and 0 <= new_y < 8:
                            if is_valid_move(board, (x, y), (new_x, new_y), color):
                                moves.append(((x, y), (new_x, new_y)))
    return moves

def evaluate_board(board):
    piece_values = {
        'p': 1, 'r': 5, 'n': 3, 'b': 3, 'q': 9, 'k': 0,
        'P': -1, 'R': -5, 'N': -3, 'B': -3, 'Q': -9, 'K': 0
    }
    value = 0
    for row in board:
        for piece in row:
            value += piece_values.get(piece, 0)
    return value

def bot_move(board, color):
    best_move = None
    best_value = -float('inf') if color == "black" else float('inf')
    moves = generate_valid_moves(board, color)

    for move in moves:
        start_pos, end_pos = move
        original_piece = board[end_pos[0]][end_pos[1]]
        move_piece(board, start_pos, end_pos)
        current_value = evaluate_board(board)
        if (color == "black" and current_value > best_value) or (color == "white" and current_value < best_value):
            best_value = current_value
            best_move = move
        undo_move(board, start_pos, end_pos, original_piece)

    if best_move:
        move_piece(board, best_move[0], best_move[1])

def move_piece(board, start_pos, end_pos):
    global en_passant_target
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    piece = board[start_x][start_y]
    board[end_x][end_y] = piece
    board[start_x][start_y] = "."
    if piece.lower() == "p" and abs(start_x - end_x) == 2:
        en_passant_target = (start_x + (end_x - start_x) // 2, start_y)
    else:
        en_passant_target = None

def undo_move(board, start_pos, end_pos, captured_piece):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    board[start_x][start_y] = board[end_x][end_y]
    board[end_x][end_y] = captured_piece

def play_chess():
    print("Welcome to Chess!")
    print_board(board)

    player_color = "white"
    bot_color = "black"

    while True:
        # Player's move
        move = input("Enter your move (e.g., e2 e4) or 'exit' to quit: ").strip()
        if move.lower() == "exit":
            print("Game over.")
            break

        try:
            start, end = move.split()
            start_pos = (8 - int(start[1]), ord(start[0]) - ord('a'))
            end_pos = (8 - int(end[1]), ord(end[0]) - ord('a'))

            if is_valid_move(board, start_pos, end_pos, player_color):
                move_piece(board, start_pos, end_pos)
                print_board(board)
            else:
                print("Invalid move, try again.")
                continue
        except Exception as e:
            print(f"Error: {e}. Use the format 'e2 e4'.")
            continue

        # Bot's move
        print("Bot's move:")
        bot_move(board, bot_color)
        print_board(board)

play_chess()