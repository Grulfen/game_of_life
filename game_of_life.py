# game_of_life.py
# Conway's game of life
import curses
import time

SIZE_X, SIZE_Y = 80, 40
START = [[0] * SIZE_X] * SIZE_Y
#START[3][10] = 1
#START[4][11] = 1
#START[5][9] = 1
#START[5][10] = 1
#START[5][12] = 1

def calculate_neighbours(world, position):
    """Return the number of neighbours of the cell in position position"""
    x, y = position
    cnt = 0
    if x == 0 and y == 0:
        for v in range(0, 2):
            for u in range(0, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif x == SIZE_X - 1 and y == 0:
        for v in range(0, 2):
            for u in range(-1, 1):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif x == 0 and y == SIZE_Y - 1:
        for v in range(-1, 1):
            for u in range(0, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif x == SIZE_X - 1  and y == SIZE_Y - 1:
        for v in range(-1, 1):
            for u in range(-1, 1):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif x == 0:
        for v in range(-1, 2):
            for u in range(0, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif y == 0:
        for v in range(0, 2):
            for u in range(-1, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif x == SIZE_X - 1:
        for v in range(-1, 2):
            for u in range(-1, 1):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    elif y == SIZE_Y - 1:
        for v in range(-1, 1):
            for u in range(-1, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    else:
        for v in range(-1, 2):
            for u in range(-1, 2):
                if u != 0 or v != 0:
                    cnt += world[y+v][x+u]
    return cnt


def new_cell(cell, neighbours):
    """Returns the new cell based on how many alive neighbours there is"""
    if cell == 1:
        if neighbours < 2:
            return 0
        elif neighbours < 4:
            return 1
        else:
            return 0
    if cell == 0:
        if neighbours == 3:
            return 1
        else:
            return 0


def new_world(current):
    """Return the new world based on the current one"""
    new_gen = []
    for y, line in enumerate(current):
        new_line = []
        for x, cell in enumerate(line):
            neighbours = calculate_neighbours(current, (x,y))
            new_line.append(new_cell(cell, neighbours))
        new_gen.append(new_line)
    return new_gen


def print_to_screen(world):
    """Print world to screen"""
    for line in world:
        for x in line:
            if x == 1:
                print("#", end="")
            else:
                print("_", end="")
        print()


def print_curses(world, window, offset_x=10, offset_y=2):
    """Print the world using ncurses"""
    for y, line in enumerate(world):
        for x, cell in enumerate(line):
            if cell == 1:
                window.addch(y+offset_y,x+offset_x,"#")
            else:
                window.addch(y+offset_y,x+offset_x," ")
    window.refresh()

def main():
    """ Main function """
    myscreen = curses.initscr()
    myscreen.border(0)
    world = START
    while True:
        print_curses(world, myscreen)
        world = new_world(world)
        time.sleep(0.1)
    myscreen.endwin()

if __name__ == "__main__":
    main()
