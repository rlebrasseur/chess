from board import Board
from display import *
from move import MoveCommand
from enumerations import Colour, State, PieceType

class Game:
    def __init__(self, display: Display = None):
        self._finished = False
        self._board = Board()
        self._display = display
        self._state = State.WHITE_MOVE

    # runs a chess game.
    def run(self):
        self._display.display(self._board.pieces)

        while not self._finished:
            if self._state == State.WHITE_MOVE:
                self._display.print_line("White to move:")
            elif self._state == State.BLACK_MOVE:
                self._display.print_line("Black to move:")
            elif self._state == State.WHITE_IN_CHECK:
                self._display.print_line("Check. White to move:")
            elif self._state == State.BLACK_IN_CHECK:
                self._display.print_line("Check. Black to move:")
            command = self._parse_command()

            if command is None and self._display is not None:
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            src_piece = self._board.get_piece(command.src)
            if src_piece is None:
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure moving right colour piece
            if (self._state == State.WHITE_MOVE and src_piece.colour == Colour.BLACK) or \
                    (self._state == State.BLACK_MOVE and src_piece.colour == Colour.WHITE):
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure it is to a movable/attackable position
            if command.dst not in src_piece.valid_moves(self._board) and \
                    command.dst not in src_piece.valid_attacks(self._board):
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure it does not result in self check
            if self._board.self_check(command):
                self._display.print_line("Results in self check. Please enter a valid command.") # colons to periods
                continue

            self._board.execute_move(command)
            if self._board._promote is not None:
                self._display.print_line("Pawn to be promoted. Please enter a valid piece (Q, B, K, R):")
                promotion = self._parse_promote()
                while promotion is None:
                    self._display.print_line("Invalid piece entered. Please enter a valid piece (Q, B, K, R):")
                    promotion = self._parse_promote()
                self._board.promote(promotion)
            self.update_state()
            self._display.display(self._board.pieces)

        if self._state == State.WHITE_CHECKMATE:
            self._display.print_line("White wins by checkmate.")
        elif self._state == State.BLACK_CHECKMATE:
            self._display.print_line("Black wins by checkmate.")
        elif self._state == State.STALEMATE:
            self._display.print_line("Stalemate. The game ends in a draw.")

    def run_test(self):
        self._display.display(self._board.pieces)
        commands = self._parse_commands_from_file()

        for command in commands:
            if self._state == State.WHITE_MOVE:
                self._display.print_line("White to move:")
            elif self._state == State.BLACK_MOVE:
                self._display.print_line("Black to move:")
            elif self._state == State.WHITE_IN_CHECK:
                self._display.print_line("Check. White to move:")
            elif self._state == State.BLACK_IN_CHECK:
                self._display.print_line("Check. Black to move:")

            print("{} {}".format(command.src, command.dst))

            if command is None and self._display is not None:
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            src_piece = self._board.get_piece(command.src)
            if src_piece is None:
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure moving right colour piece #TODO include check states
            if (self._state == State.WHITE_MOVE and src_piece.colour == Colour.BLACK) or \
                    (self._state == State.BLACK_MOVE and src_piece.colour == Colour.WHITE) or \
                    (self._state == State.WHITE_IN_CHECK and src_piece.colour == Colour.BLACK) or \
                    (self._state == State.BLACK_IN_CHECK and src_piece.colour == Colour.WHITE):
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure it is to a movable/attackable position
            if command.dst not in src_piece.valid_moves(self._board) and \
                    command.dst not in src_piece.valid_attacks(self._board):
                self._display.print_line("Invalid command. Please enter a valid command.")
                continue
            # make sure it does not result in self check
            if self._board.self_check(command):
                self._display.print_line("Results in self check. Please enter a valid command.")
                continue

            self._board.execute_move(command)
            if self._board._promote is not None:
                self._display.print_line("Pawn to be promoted. Please enter a valid piece (Q, B, N, R):")
                promotion = self._parse_promote()
                while promotion is None:
                    self._display.print_line("Invalid piece entered. Please enter a valid piece (Q, B, N, R):")
                    promotion = self._parse_promote()
                self._board.promote(promotion)
            self.update_state()
            self._display.display(self._board.pieces)

            if self._finished:
                break

        if self._state == State.WHITE_CHECKMATE:
            self._display.print_line("White wins by checkmate.")
        elif self._state == State.BLACK_CHECKMATE:
            self._display.print_line("Black wins by checkmate.")
        elif self._state == State.STALEMATE:
            self._display.print_line("Stalemate. The game ends in a draw.")

    # checks the state of the board and updates state accordingly.
    def update_state(self):
        if self._state == State.WHITE_MOVE or self._state == State.WHITE_IN_CHECK:
            check = self._board.check(Colour.WHITE)
            no_moves = self._board.no_moves(Colour.BLACK)
            if check:
                if no_moves:
                    self._state = State.WHITE_CHECKMATE
                    self._finished = True
                else:
                    self._state = State.BLACK_IN_CHECK
            elif not check:
                if no_moves:
                    self._state = State.STALEMATE
                    self._finished = True
                else:
                    self._state = State.BLACK_MOVE

        elif self._state == State.BLACK_MOVE or self._state == State.BLACK_IN_CHECK:
            check = self._board.check(Colour.BLACK)
            no_moves = self._board.no_moves(Colour.WHITE)
            if check:
                if no_moves:
                    self._state = State.BLACK_CHECKMATE
                    self._finished = True
                else:
                    self._state = State.WHITE_IN_CHECK
            elif not check:
                if no_moves:
                    self._state = State.STALEMATE
                    self._finished = True
                else:
                    self._state = State.WHITE_MOVE

    # retrieves move command from stdin and returns a move command.
    def _parse_command(self):
        input_ = input()
        return MoveCommand.from_string(input_)

    def _parse_commands_from_file(self):
        with open('enpassantpromotion.txt') as test:
            lines = test.readlines()
        for i, line in enumerate(lines):
            lines[i] = MoveCommand.from_string(line)
        return lines

    # for promotion, retrieves a string representing a piece from stdin, and returns a PieceType.
    def _parse_promote(self):
        input_ = input()
        if input_ == 'Q':
            return PieceType.QUEEN
        elif input_ == 'B':
            return PieceType.BISHOP
        elif input_ == 'N':
            return PieceType.KNIGHT
        elif input_ == 'R':
            return PieceType.ROOK
        else:
            return None
