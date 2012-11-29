import game_of_life

SIZE_X, SIZE_Y = 80, 40


def main():
    """ Main function """
    run = True
    world = game_of_life.World(start="random",
                               mode="curses",
                               size_x=SIZE_X,
                               size_y=SIZE_Y)
    #world.load("gliders.gol")
    world.initialize_screen()
    world.animate(10, 0.1)
    run = world.again()
    while run:
        # TODO, fix int(run)
        world.animate(int(run), 0.0)
        run = world.again()
    world.kill_screen()


if __name__ == "__main__":
    main()
