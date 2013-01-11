import game_of_life

#SIZE_X, SIZE_Y = 41, 165

SIZE_X, SIZE_Y = 30, 30

#world = {(3,3): 1, (3,4): 1, (4,3) : 1, (4,4) : 1}

def main():
    """ Main function """
    run = True
    game = game_of_life.Game(start="random",
                             mode="curses",
                             size_x=SIZE_X,
                             size_y=SIZE_Y)
    #game.world.world = world
    game.initialize_screen()
    game.print_world()
    while True:
        game.prompt()
        game.print_world()

if __name__ == "__main__":
    main()
