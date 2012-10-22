# game_of_life.py
# Conway's game of life
import curses
import time
import random
import sys

SIZE_X, SIZE_Y = 80, 40


class World:
    def __init__(self, start=False, mode="screen", size_x=40, size_y=40):
        if start == "gliders":
            if size_x < 40:
                print("Needs at least 40 pixels wide for gliders")
                sys.exit(1)
            elif size_y < 10:
                print("Needs at least 10 pixels long for gliders")
                sys.exit(1)
            else:
                self.gliders()
        else:
            self.random_world()

        self.mode = mode
        if mode == "curses":
            self.screen = curses.initscr()
            self.screen.border(0)

    def gliders(self):
        """ Set the world to Gosper Glider Gun"""
        world = [[0 for x in range(SIZE_X)] for y in range(SIZE_Y)]
        world[1][25] = 1
        world[2][23] = 1
        world[2][25] = 1
        world[3][13:15] = [1, 1]
        world[3][21:23] = [1, 1]
        world[3][35:37] = [1, 1]
        world[4][12] = 1
        world[4][16] = 1
        world[4][21:23] = [1, 1]
        world[4][35:37] = [1, 1]
        world[5][1:3] = [1, 1]
        world[5][11] = 1
        world[5][17] = 1
        world[5][21:23] = [1, 1]
        world[6][1:3] = [1, 1]
        world[6][11] = 1
        world[6][15] = 1
        world[6][17:19] = [1, 1]
        world[6][23] = 1
        world[6][25] = 1
        world[7][11] = 1
        world[7][17] = 1
        world[7][25] = 1
        world[8][12] = 1
        world[8][16] = 1
        world[9][13:15] = [1, 1]
        self.world = world

    def random_world(self):
        self.world = [[random.randint(0, 1)
                       for x in range(SIZE_X)] for y in range(SIZE_Y)]

    def _calculate_neighbours(self, position):
        """Return the number of neighbours of the cell in position position"""
        x, y = position
        cnt = 0
        if x == 0 and y == 0:
            for v in range(0, 2):
                for u in range(0, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif x == SIZE_X - 1 and y == 0:
            for v in range(0, 2):
                for u in range(-1, 1):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif x == 0 and y == SIZE_Y - 1:
            for v in range(-1, 1):
                for u in range(0, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif x == SIZE_X - 1 and y == SIZE_Y - 1:
            for v in range(-1, 1):
                for u in range(-1, 1):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif x == 0:
            for v in range(-1, 2):
                for u in range(0, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif y == 0:
            for v in range(0, 2):
                for u in range(-1, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif x == SIZE_X - 1:
            for v in range(-1, 2):
                for u in range(-1, 1):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        elif y == SIZE_Y - 1:
            for v in range(-1, 1):
                for u in range(-1, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        else:
            for v in range(-1, 2):
                for u in range(-1, 2):
                    if u != 0 or v != 0:
                        cnt += self.world[y + v][x + u]
        return cnt

    def _new_cell(self, cell, neighbours):
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

    def update(self):
        """ Update the current world one step """
        new_world = []
        for y, line in enumerate(self.world):
            new_line = []
            for x, cell in enumerate(line):
                neighbours = self._calculate_neighbours((x, y))
                new_line.append(self._new_cell(cell, neighbours))
            new_world.append(new_line)
        self.world = new_world

    def print_world(self):
        if self.mode == "curses":
            self._print_curses()
        elif self.mode == "screen":
            self._print_to_screen()
        else:
            pass

    def _print_to_screen(self):
        """Print world to screen"""
        for line in self.world:
            for x in line:
                if x == 1:
                    print("#", end="")
                else:
                    print("_", end="")
            print()

    def _print_curses(self, offset_x=10, offset_y=2):
        """Print the world using ncurses"""
        for y, line in enumerate(self.world):
            for x, cell in enumerate(line):
                if cell == 1:
                    self.screen.addch(y + offset_y, x + offset_x, "#")
                else:
                    self.screen.addch(y + offset_y, x + offset_x, " ")
        self.screen.refresh()

    def kill_screen(self):
        """ Kill the screen and cleanup """
        if self.mode == "curses":
            curses.endwin()

    def animate(self, steps, dt=0.05):
        """ Update and print the screen 'step' times"""
        for i in range(steps):
            self.update()
            self.print_world()
            time.sleep(dt)


def main():
    """ Main function """
    world = World(start="gliders", mode="curses", size_x=SIZE_X, size_y=SIZE_Y)
    world.animate(200, 0.05)
    world.kill_screen()


if __name__ == "__main__":
    try:
        main()
    except:
        curses.endwin()
