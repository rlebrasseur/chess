from display import ConsoleDisplay
from game import Game

def main():
    display = ConsoleDisplay()
    game = Game(display)
    #game.run()
    game.run_test()

if __name__ == "__main__":
    main()
