from move import ChessPosition

class Display:
    def display(self):
        raise NotImplementedError

    def print_line(self, string):
        raise NotImplementedError

class ConsoleDisplay(Display):
    # displays board on the console.
    def display(self, pieces):
        for y in reversed(range(0, 8)):
            self._draw_board_line(y, pieces)
        self._draw_bottom_line()

    # draws a row of the board on the console.
    def _draw_board_line(self, line_number, pieces):
        white_square = " "
        black_square = "_"

        string = "{} ".format(line_number + 1)
        for x in range(0, 8):
            if (x+line_number)%2==0:
                square = black_square
            else:
                square = white_square
            curr_position = ChessPosition(x, line_number)
            for piece in pieces:
                if curr_position == piece.position:
                    square = piece.symbol()
            string += square
        print(string)

    # draws a key of files
    def _draw_bottom_line(self):
        string = "  abcdefgh"
        print(string)

    # prints a string to the console.
    def print_line(self, string):
        print(string)
