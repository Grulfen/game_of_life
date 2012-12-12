import game_of_life

SIZE_X, SIZE_Y = 20, 20


def main():
    """ Main function """
    run = True
    game = game_of_life.Game(start="random",
                             mode="curses",
                             size_x=SIZE_X,
                             size_y=SIZE_Y)
    game.initialize_screen()
    game.print_world()
    run = game.again()
    while run:
        game.animate(int(run), 0.5)
        run = game.again()
    game.kill_screen()


if __name__ == "__main__":
    main()
