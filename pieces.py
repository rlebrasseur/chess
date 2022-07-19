from enumerations import Colour, PieceType
from move import ChessPosition
from copy import copy

class Piece:
    def __init__(self, position: ChessPosition, colour: Colour):
        self._position = position
        self._colour = colour

    @property
    def position(self):
        return self._position

    @property
    def colour(self):
        return self._colour

    def move(self, destination: ChessPosition):
        self._position = destination

class PieceFactory:
    @staticmethod
    def create(piece_type: PieceType, position: ChessPosition, colour: Colour):
        if piece_type == PieceType.KING:
            return King(position, colour)

        if piece_type == PieceType.QUEEN:
            return Queen(position, colour)

        if piece_type == PieceType.KNIGHT:
            return Knight(position, colour)

        if piece_type == PieceType.ROOK:
            return Rook(position, colour)

        if piece_type == PieceType.BISHOP:
            return Bishop(position, colour)

        if piece_type == PieceType.PAWN:
            return Pawn(position, colour)

class King(Piece):
    def __init__(self, position: ChessPosition, colour: Colour):
        super().__init__(position, colour)
        self._moved = False
        self._board_handle = None

    @property
    def moved(self):
        return copy(self._moved)

    # To facilitate castling mechanics, and setting king position on board.
    def set_board_handle(self, board):
        self._board_handle = board
        self._board_handle.register_king_position(self.position, self.colour)

    # returns an array of all movable positions.
    def valid_moves(self, board):
        standard_squares = ((1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0))
        castling_directions = ((-1, 0), (1,0))
        positions = []
        for square in standard_squares:
            positions.append(board.square_search(self.position, self.colour, square[0], square[1]))
        for dir in castling_directions:
            positions.append(board.castle_search(self.position, self.colour, dir[0], dir[1]))
        positions = [position for position in positions if position is not None]
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        standard_squares = ((1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0))
        positions = []
        for square in standard_squares:
            positions.append(board.square_search(self.position, self.colour, square[0], square[1]))
        positions = [position for position in positions if position is not None]
        return positions

    # updates pieces position to destination, updates moved parameter, and registers king position.
    # If the move is a castling move, castles rook.
    def move(self, destination: ChessPosition):
        x_magnitude = abs(self.position.x_coord-destination.x_coord)
        self._position = destination
        self._board_handle.register_king_position(destination, self.colour)
        self._moved = True
        if x_magnitude == 2:
            self._board_handle.castle_rook(self.colour)

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "K"
        else:
            return "k"

class Queen(Piece):

    # returns an array of all movable positions.
    def valid_moves(self, board):
        directions = ((1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0))
        positions = []
        for dir in directions:
            positions += board.direction_search(self.position, self.colour, dir[0], dir[1])
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        return self.valid_moves(board)

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "Q"
        else:
            return "q"

class Bishop(Piece):

    # returns an array of all movable positions.
    def valid_moves(self, board):
        directions = ((1,1), (-1,1), (-1,-1), (1,-1))
        positions = []
        for dir in directions:
            positions += board.direction_search(self.position, self.colour, dir[0], dir[1])
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        return self.valid_moves(board)

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "B"
        else:
            return "b"

class Knight(Piece):

    # returns an array of all movable positions.
    def valid_moves(self, board):
        standard_squares = ((1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1), (2,1))
        positions = []
        for square in standard_squares:
            positions.append(board.square_search(self.position, self.colour, square[0], square[1]))
        positions = [position for position in positions if position is not None]
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        return self.valid_moves(board)

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "N"
        else:
            return "n"

class Rook(Piece):
    def __init__(self, position: ChessPosition, colour: Colour):
        super().__init__(position, colour)
        self._moved = False

    @property
    def moved(self):
        return copy(self._moved)

    # returns an array of all movable positions.
    def valid_moves(self, board):
        directions = ((0,1), (-1,0), (0,-1), (1,0))
        positions = []
        for dir in directions:
            positions += board.direction_search(self.position, self.colour, dir[0], dir[1])
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        return self.valid_moves(board)

    # updates pieces position to destination, and updates moved parameter.
    def move(self, destination: ChessPosition):
        self._position = destination
        self._moved = True

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "R"
        else:
            return "r"

class Pawn(Piece):
    def __init__(self, position: ChessPosition, colour: Colour):
        super().__init__(position, colour)
        self._moved = False
        self._board_handle = None

    @property
    def moved(self):
        return copy(self._moved)

    # To facilitate en passant and promotion mechanics.
    def set_board_handle(self, board):
        self._board_handle = board

    # returns an array of all movable positions.
    def valid_moves(self, board):
        standard_square = (0,1)
        first_move_square = (0,2)
        attacking_squares = ((-1,1), (1,1))
        positions = []
        positions.append(board.square_search(self._position, self._colour, standard_square[0], standard_square[1] if self._colour==Colour.WHITE else -1 * standard_square[1], passive=True))
        if positions[0] is not None and self._moved == False:
            positions.append(board.square_search(self._position, self._colour, first_move_square[0], first_move_square[1] if self._colour==Colour.WHITE else -1 * first_move_square[1], passive=True))
        for square in attacking_squares:
            positions.append(board.square_search(self._position, self._colour, square[0], square[1] if self._colour==Colour.WHITE else -1 * square[1], pawn_take=True))
        positions = [position for position in positions if position is not None]
        return positions

    # returns an array of all attackable positions.
    def valid_attacks(self, board):
        attacking_squares = ((-1,1), (1,1))
        positions = []
        for square in attacking_squares:
            positions.append(board.square_search(self._position, self._colour, square[0], square[1] if self._colour==Colour.WHITE else -1 * square[1], pawn_take=True))
        positions = [position for position in positions if position is not None]
        return positions

    # updates pieces position to destination, and updates moved parameter.
    # If the move is by 2 squares, updates enpassant parameter on the board.
    # If the move is to the last rank, updates promote parameter on the board.
    def move(self, destination: ChessPosition):
        y_magnitude = abs(self.position.y_coord-destination.y_coord)
        self._position = destination
        if y_magnitude == 2: #if first move by two squares, log enpassant
            self._board_handle.register_enpassant(destination)
        rank = destination.y_coord if self._colour==Colour.WHITE else 8-destination.y_coord-1
        if rank == 7: #if pawn is on the last rank, register that it needs to be promoted
            self._board_handle.register_promote(destination)
        self._moved = True

    # returns a character representing the piece.
    def symbol(self):
        if self.colour == Colour.WHITE:
            return "P"
        else:
            return "p"
