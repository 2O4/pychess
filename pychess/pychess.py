import sys

FIRST_PLAYER = 1  # 1 = white, 2 = black
ENABLE_COLORS = True


class termcolors:
    BOLD = "\033[1m"
    ENDC = "\033[0m"
    BG_WHITE = "\033[48;5;246m"
    BG_BLACK = "\033[48;5;241m"
    FG_WHITE = "\033[38;5;254m"
    FG_BLACK = "\033[38;5;233m"


class IllegalMoveException(Exception):
    pass


class Piece:
    PIECES = [" ", "♔", "♕", "♖", "♗", "♘", "♙", "♚", "♛", "♜", "♝", "♞", "♟"]

    def __init__(self, piece_number: int = 0, x: int = None, y: int = None):
        self.piece_number = piece_number

    def __str__(self):
        return self.PIECES[self.piece_number]

    def black_str(self):
        """Same has __str__ but return only the black pieces."""
        if self.color == "black":
            return self.__str__()
        return self.PIECES[self.piece_number + 6]

    @property
    def player(self):
        if self.piece_number > 0 and self.piece_number < 7:
            return 1
        elif self.piece_number > 6 and self.piece_number < 13:
            return 2
        return 0

    @property
    def color(self):
        if self.player == 1:
            return "white"
        elif self.player == 2:
            return "black"
        return None

    @property
    def is_white(self):
        return self.color == "white"

    @property
    def is_black(self):
        return self.color == "black"

    @property
    def is_king(self):
        return self.piece_number in [1, 7]

    @property
    def is_queen(self):
        return self.piece_number in [2, 8]

    @property
    def is_rook(self):
        return self.piece_number in [3, 9]

    @property
    def is_bishop(self):
        return self.piece_number in [4, 10]

    @property
    def is_knight(self):
        return self.piece_number in [5, 11]

    @property
    def is_pawn(self):
        return self.piece_number in [6, 12]

    def is_player_piece(self, player):
        return self.player == player


class Board:
    BOARD_SIZE = 8
    ENABLE_COLORS = ENABLE_COLORS

    def __init__(self):
        self.board = [
            [None for y in range(self.BOARD_SIZE)] for x in range(self.BOARD_SIZE)
        ]

        # black pieces
        for tile in range(self.BOARD_SIZE):
            self.board[1][tile] = Piece(12)

        self.board[0][0] = Piece(9)
        self.board[0][7] = Piece(9)
        self.board[0][1] = Piece(11)
        self.board[0][6] = Piece(11)
        self.board[0][2] = Piece(10)
        self.board[0][5] = Piece(10)
        self.board[0][4] = Piece(7)
        self.board[0][3] = Piece(8)

        # white pieces
        for tile in range(self.BOARD_SIZE):
            self.board[6][tile] = Piece(6)

        self.board[7][0] = Piece(3)
        self.board[7][7] = Piece(3)
        self.board[7][1] = Piece(5)
        self.board[7][6] = Piece(5)
        self.board[7][2] = Piece(4)
        self.board[7][5] = Piece(4)
        self.board[7][4] = Piece(1)
        self.board[7][3] = Piece(2)

    def __str__(self):
        string = ""
        for row_index, row in enumerate(self.board):
            str_row = str(self.BOARD_SIZE - row_index) + " "
            for piece_index, piece in enumerate(row):
                str_piece = " "
                if self.ENABLE_COLORS:
                    if piece:
                        str_piece = piece.black_str()

                    if (row_index + piece_index) % 2 == 0:
                        bg_color = termcolors.BG_WHITE
                    else:
                        bg_color = termcolors.BG_BLACK

                    if piece and piece.color == "white":
                        fg_color = termcolors.FG_WHITE
                    else:
                        fg_color = termcolors.FG_BLACK

                    str_row += f"{bg_color}{fg_color}{str_piece} {termcolors.ENDC}"
                else:
                    if piece:
                        str_piece = str(piece)
                    str_row += f"{str_piece} "
            string += "\n" + str_row
        string += "\n  a b c d e f g h"
        return string

    def check_mate(self):
        return False

    def move(self, move):
        self.board[move[1][0]][move[1][1]] = self.board[move[0][0]][move[0][1]]
        self.board[move[0][0]][move[0][1]] = None

    def is_move_valid(self, raw_move, player):
        try:
            move = convert_raw_user_move(raw_move)
        except IllegalMoveException:
            return False

        piece = self.board[move[0][0]][move[0][1]]
        destination_piece = self.board[move[1][0]][move[1][1]]

        if piece and self.check_move(
            piece=piece,
            destination_piece=destination_piece,
            move=move,
            player=player,
        ):
            return True
        return False

    def check_move(self, piece, destination_piece, move, player):
        """Check possible movements."""
        if self.check_general_rules(piece, destination_piece, player):
            if piece.is_king:
                return self.check_king_rules(piece, destination_piece, move)
            elif piece.is_queen:
                return self.check_queen_rules(piece, destination_piece, move)
            elif piece.is_rook:
                return self.check_rook_rules(piece, destination_piece, move)
            elif piece.is_bishop:
                return self.check_bishop_rules(piece, destination_piece, move)
            elif piece.is_knight:
                return self.check_knight_rules(piece, destination_piece, move)
            elif piece.is_pawn:
                return self.check_pawn_rules(piece, destination_piece, move)
        return False

    def check_general_rules(self, piece, destination_piece, player):
        if not piece.is_player_piece(player):
            return False
        if destination_piece:
            if destination_piece.player == piece.player:
                return False
            # TODO check that it doesn't leave the current user in check
        return True

    def check_king_rules(self, piece, destination_piece, move):
        py, px, dy, dx = [*move[0], *move[1]]
        return px - 1 <= dx <= px + 1 and py - 1 <= dy <= py + 1

    def check_queen_rules(self, piece, destination_piece, move):
        rook_rule = self.rook_rule(piece, destination_piece, move)
        bishop_rule = self.bishop_rule(piece, destination_piece, move)
        return rook_rule or bishop_rule

    def check_rook_rules(self, piece, destination_piece, move):
        py, px, dy, dx = [*move[0], *move[1]]
        if px == dx or py == dy:
            if px == dx:
                axis = [self.board[y][px] for y in range(min(dy, py), max(dy, py))]
            else:
                axis = [self.board[py][x] for x in range(min(dx, px), max(dx, px))]
            # check for no obstacles
            if (len(axis) - axis.count(None)) == 0:
                return True
        return False

    def check_bishop_rules(self, piece, destination_piece, move):
        py, px, dy, dx = [*move[0], *move[1]]
        return abs(px - dx) == abs(py - dy)

    def check_knight_rules(self, piece, destination_piece, move):
        py, px, dy, dx = [*move[0], *move[1]]
        move_x = abs(px - dx)
        move_y = abs(py - dy)
        return (move_x == 1 and move_y == 2) or (move_x == 2 and move_y == 1)

    def check_pawn_rules(self, piece, destination_piece, move):
        py, px, dy, dx = [*move[0], *move[1]]
        move_x = abs(px - dx)
        move_y = abs(py - dy)
        # move in only one direction based on color
        if (piece.is_white and py > dy) or (piece.is_black and py < dy):
            # only move on y axis if no destination piece
            if destination_piece is None and move_x == 0:
                if move_y == 1:
                    return True
                # if pawn is in starting position and move 2 on the y axis
                elif move_y == 2 and (
                    (piece.is_white and py == 6) or (piece.is_black and py == 1)
                ):
                    return True
            # move 1 in x axis and 1 in y axis if taking a piece
            elif destination_piece and move_x == 1 and move_y == 1:
                return True
        return False


def convert_raw_user_move(raw_move: str):
    if raw_move:
        raw_move = list(raw_move.replace(" ", ""))
        if raw_move[1].isdigit() and raw_move[3].isdigit():
            # piece
            px = 8 - int(raw_move[1])
            py = ord(raw_move[0].lower()) - 97

            # move
            pmx = 8 - int(raw_move[3])
            pmy = ord(raw_move[2].lower()) - 97

            if (
                px >= 0
                and px < 8
                and py >= 0
                and py < 8
                and pmx >= 0
                and pmx < 8
                and pmy >= 0
                and pmy < 8
            ):
                return [[px, py], [pmx, pmy]]
    raise IllegalMoveException


def get_user_move(board, player):
    raw_move = None
    while not board.is_move_valid(raw_move, player):
        try:
            raw_move = input("move: ")
        except KeyboardInterrupt:
            sys.exit(1)
        try:
            move = convert_raw_user_move(raw_move)
        except IllegalMoveException:
            move = None
            print("Invalid move, format: *selection* *destination*. ex: a2 a4")
    return move


def game_loop():
    board = Board()
    # change between 1 and 2
    player = FIRST_PLAYER
    print(board)
    while not board.check_mate():
        player_str = "white" if player == 1 else "black"
        if ENABLE_COLORS:
            player_str = f"{termcolors.BOLD}{player_str}{termcolors.ENDC}"
        print(f"\nplayer {player_str}")
        move = get_user_move(board, player)
        board.move(move)
        print(board)
        player = player % 2 + 1


def main():
    game_loop()
