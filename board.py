from pieces import Piece, PieceFactory, King, Queen, Bishop, Knight, Rook, Pawn
from move import ChessPosition, MoveCommand
from enumerations import Colour, PieceType, INITIAL_PIECE_SET_SINGLE
from copy import deepcopy
from collections import deque

class Board:
    def __init__(self):
        self._pieces = [] # array of pieces on the board
        self._move_stack = deque() # stack of moves played on the board.
        self._size = 8 # width and height of the board.
        self._white_king_position = None # position of white king.
        self._black_king_position = None # position of black king.
        self._enpassant = None # position of piece to be captured by enpassant, if there is one.
        self._promote = None # position of pawn to be promoted if there is one.
        self._initialize_pieces(INITIAL_PIECE_SET_SINGLE)

    # initializes pieces to represent a standard chess game.
    def _initialize_pieces(self, pieces_setup: list):
        for piece_tuple in pieces_setup:
            type = piece_tuple[0]
            x = piece_tuple[1]
            y = piece_tuple[2]

            piece_white = PieceFactory.create(type, ChessPosition(x, y), Colour.WHITE)
            if type == PieceType.KING:
                piece_white.set_board_handle(self)
            if type == PieceType.PAWN:
                piece_white.set_board_handle(self)
            self._pieces.append(piece_white)

            piece_black = PieceFactory.create(type, ChessPosition(x, self._size - y - 1), Colour.BLACK)
            if type == PieceType.KING:
                piece_black.set_board_handle(self)
            if type == PieceType.PAWN:
                piece_black.set_board_handle(self)
            self._pieces.append(piece_black)

    # returns piece at position if there is one. returns None otherwise.
    def get_piece(self, position: ChessPosition):
        for piece in self._pieces:
            if piece.position==position:
                return piece
        return None

    # executes the move command.
    # registers the move in the move stack if register is True.
    def execute_move(self, command: MoveCommand, register=True):
        src_piece = self.get_piece(command.src)
        for i, piece in enumerate(self._pieces):
            if piece.position == command.dst:
                del self._pieces[i]
                break
            if self._enpassant is not None and piece.position==self._enpassant and isinstance(src_piece, Pawn): # could this be done within Pawn?
                if self.get_piece(self._enpassant).colour == Colour.WHITE:
                    capture_destination = ChessPosition(self._enpassant.x_coord, self._enpassant.y_coord-1)
                else: capture_destination = ChessPosition(self._enpassant.x_coord, self._enpassant.y_coord+1)
                if command.dst == capture_destination:
                    del self._pieces[i]
                    break
        self._enpassant = None
        src_piece.move(command.dst)
        if register:
            self._move_stack.append(command)

    # castles rook.
    # requires: king has been moved to a valid castling square, and castling is available.
    def castle_rook(self, colour: Colour):
        if colour == Colour.WHITE:
            if self._white_king_position == ChessPosition(2,0): #castle queenside
                src = ChessPosition(0,0)
                dst = ChessPosition(3,0)
                move = MoveCommand(src, dst)
                self.execute_move(move, register=False)
            if self._white_king_position == ChessPosition(6,0): #castle kingside
                src = ChessPosition(7,0)
                dst = ChessPosition(5,0)
                move = MoveCommand(src, dst)
                self.execute_move(move, register=False)
        if colour == Colour.BLACK:
            if self._black_king_position == ChessPosition(2,7): #castle queenside
                src = ChessPosition(0,7)
                dst = ChessPosition(3,7)
                move = MoveCommand(src, dst)
                self.execute_move(move, register=False)
            if self._black_king_position == ChessPosition(6,7): #castle kingside
                src = ChessPosition(7,7)
                dst = ChessPosition(5,7)
                move = MoveCommand(src, dst)
                self.execute_move(move, register=False)

    # promotes pawn to be promted to type.
    # requires: self._promote is not None.
    def promote(self, type: PieceType):
        position = self._promote
        self._promote = None
        colour = self.get_piece(position).colour

        new_piece = PieceFactory.create(type, position, colour)

        for i, piece in enumerate(self._pieces):
            if piece.position == position:
                del self._pieces[i]
                break

        self._pieces.append(new_piece)

    # returns ChessPosition which is a result of a move from src by increment_x and increment_y
    # if this is a valid move given the current board state. Otherwise returns None.
    def square_search(self, src: ChessPosition, colour: Colour, increment_x, increment_y, passive=False, pawn_take=False):
        if abs(increment_x)+abs(increment_y)==0: return None

        end_x = src.x_coord + increment_x
        end_y = src.y_coord + increment_y

        if end_x >= self._size or end_y >= self._size or end_x < 0 or end_y < 0:
            return None

        end_position = ChessPosition(end_x, end_y)
        end_piece = self.get_piece(end_position)

        if end_piece is not None:
            if passive:
                return None
            return end_position if end_piece.colour != colour else None
        if pawn_take and self._enpassant is not None: #enpassant logic
            if self.get_piece(self._enpassant).colour == Colour.WHITE:
                capture_destination = ChessPosition(self._enpassant.x_coord, self._enpassant.y_coord-1)
            else:
                capture_destination = ChessPosition(self._enpassant.x_coord, self._enpassant.y_coord+1)
            if end_position == capture_destination:
                return end_position
        return end_position if not pawn_take else None

    # returns array of ChessPositions which are the result of a move from src in the direction
    # [increment_x, increment_y] if this is a valid move given the current board state.
    def direction_search(self, src: ChessPosition, colour: Colour, increment_x, increment_y):
        positions = []
        if abs(increment_x)+abs(increment_y)==0: return positions
        curr_x = src.x_coord
        curr_y = src.y_coord
        curr_x += increment_x
        curr_y += increment_y
        while curr_x >= 0 and curr_y >= 0 and curr_x < self._size and curr_y < self._size:
            curr_position = ChessPosition(curr_x, curr_y)
            curr_piece = self.get_piece(curr_position)
            if curr_piece is not None:
                if curr_piece.colour != colour:
                    positions.append(curr_position)
                break
            positions.append(curr_position)
            curr_x += increment_x
            curr_y += increment_y
        return positions

    # returns ChessPosition which is the result of a king move from src in the direction
    # [increment_x, increment_y] if it is a valid castling move given the current board state.
    def castle_search(self, src: ChessPosition, colour: Colour, increment_x, increment_y): # do you need a y direction?
        src_piece = self.get_piece(src)
        # checks if king not moved
        if src_piece.moved:
            return None

        curr_x = src.x_coord
        curr_y = src.y_coord
        curr_x += increment_x
        curr_y += increment_y
        while curr_x >= 0 and curr_y >= 0 and curr_x < self._size and curr_y < self._size: #checks if there are pieces between and rook not moved
            curr_position = ChessPosition(curr_x, curr_y)
            curr_piece = self.get_piece(curr_position)
            if isinstance(curr_piece, Rook) and src_piece.colour == curr_piece.colour:
                # checks if rook not moved
                if curr_piece.moved == False:
                     break
            if curr_piece is not None:
                return None
            curr_x += increment_x
            curr_y += increment_y

        #checks if king in check on any of moving squares
        if src_piece.colour == Colour.WHITE:
            opp_colour = Colour.BLACK
        else:
            opp_colour = Colour.WHITE
        if self.check(opp_colour):
            return None
        middle = ChessPosition(src.x_coord + increment_x, src.y_coord + increment_y)
        move_mid = MoveCommand(src, middle)
        if self.self_check(move_mid):
            return None
        end = ChessPosition(src.x_coord + 2*increment_x, src.y_coord + 2*increment_y)
        move_end = MoveCommand(src, end)
        if self.self_check(move_end):
            return None

        end_position = ChessPosition(src.x_coord + 2*increment_x, src.y_coord + 2*increment_y)
        return end_position

    # returns True if move results in putting your own king in check. False otherwise
    def self_check(self, move: MoveCommand):
        copy = deepcopy(self)
        colour = copy.get_piece(move.src).colour
        copy.execute_move(move, register=False) # do I need register field?
        for piece in copy.pieces:
            if colour == Colour.WHITE and copy._white_king_position in piece.valid_attacks(copy):
                return True
            elif colour == Colour.BLACK and copy._black_king_position in piece.valid_attacks(copy):
                return True
        return False


    # returns True if move results in a check on the king of opposite Colour to colour. False otherwise
    def check(self, colour: Colour):
        for piece in self.pieces:
            if colour == Colour.WHITE and self._black_king_position in piece.valid_attacks(self):
                return True
            elif colour == Colour.BLACK and self._white_king_position in piece.valid_attacks(self):
                return True
        return False

    # returns True if there are no valid moves for colour. False otherwise.
    # TODO needs to be reworked because valid moves and attacks dont check for self check.
    def no_moves(self, colour: Colour):
        moves = []
        for piece in self.pieces:
            if piece.colour == colour:
                for dst in piece.valid_moves(self) + piece.valid_attacks(self):
                    move = MoveCommand(piece.position, dst)
                    if not self.self_check(move):
                        moves.append(move)
        return len(moves) == 0

    # registers position of colour's King.
    def register_king_position(self, position: ChessPosition, colour: Colour):
        if colour == Colour.WHITE:
            self._white_king_position = position
        elif colour == Colour.BLACK:
            self._black_king_position = position
        else:
            raise RuntimeError("Unknown color of the king piece")

    # registers position in self._enpassant
    def register_enpassant(self, position: ChessPosition):
        self._enpassant = position

    # registers position in self._promote
    def register_promote(self, position: ChessPosition):
        self._promote = position

    # returns copy of self._pieces.
    @property
    def pieces(self):
        return deepcopy(self._pieces)
