#!/usr/bin/env python3
""" Executable for game of life """
import game_of_life

SIZE_X, SIZE_Y = 80, 30


def main():
    """ Main function """
    game = game_of_life.Game(mode="curses", size_x=SIZE_X, size_y=SIZE_Y,
                             max_size=True)
    game.print_world()
    while True:
        game.prompt()
        game.print_world()

if __name__ == "__main__":
    main()
