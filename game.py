import game_of_life

SIZE_X, SIZE_Y = 60, 60


def main():
    """ Main function """
    run = True
    game = game_of_life.Game(start="random",
                             mode="curses",
                             size_x=SIZE_X,
                             size_y=SIZE_Y)
    game.initialize_screen()
    game.print_world()
    while True:
        game.prompt()
        game.print_world()

if __name__ == "__main__":
    main()
