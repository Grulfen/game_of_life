# game_of_life.py
# Conway's game of life
import curses
import time
import random
import signal
import sys
import logging

logging.basicConfig(filename="life.log", filemode="w",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def signal_handler(signal, frame):
    """ Make Ctrl-c exit close curses window """
    logging.info("Caught SIGINT, closing")
    curses.endwin()
    sys.exit(0)


class World():
    """ World class """
    def __init__(self, size_x=10, size_y=10):
        self.size_y = size_y
        self.size_x = size_x
        self.zero()
        self.random(int(size_x*size_y*2/3))

    def zero(self):
        """ Set the world to all zeros """
        logging.info("Clearing world")
        world = {}
        self.world = world

    def random(self, num):
        self.zero()
        for i in range(num):
            x = random.randint(0, self.size_x)
            y = random.randint(0, self.size_x)
            self.world[(x, y)] = 1

    def print_screen(self, world=False, start_pos=None, end_pos=None):
        """Print world to screen"""
        if not world:
            world = self.world
        if start_pos and end_pos:
            # Print world from start_pos to end_pos
            start_x, start_y = start_pos
            end_x, end_y = end_pos
        else:
            # No positions specified. Print the whole world
            start_x, start_y = self.min_pos()
            end_x, end_y = self.max_pos()
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if world.get((x, y), False):
                    print("#", end="")
                else:
                    print("_", end="")
            print()

    def print_curses(self, screen, start_pos, end_pos):
        """Print the world from start_pos to end_pos on ncurses screen"""
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        offset_x = start_x - 1
        offset_y = start_y - 1
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if self.world.get((x, y), False):
                    screen.addch(x - offset_x, y - offset_y, "#")
                else:
                    screen.addch(x - offset_x, y - offset_y, "-")
        screen.refresh()

    def min_pos(self):
        """ Return the top, left position with alive cell"""
        cells = list(self.world.keys())
        if not cells:
            # World empty
            return (0, 0)
        else:
            leftmost = cells[0][0]
            upmost = cells[0][1]
            for cell in cells:
                x, y = cell
                if x < leftmost:
                    leftmost = x
                if y < upmost:
                    upmost = y
        return (leftmost, upmost)

    def max_pos(self):
        """ Return the bottom, right position with alive cell"""
        cells = list(self.world.keys())
        if not cells:
            # World empty
            return (10, 10)
        else:
            rightmost = cells[0][0]
            downmost = cells[0][1]
            for cell in cells:
                x, y = cell
                if x > rightmost:
                    rightmost = x
                if y > downmost:
                    downmost = y
        return (rightmost, downmost)

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

    def calculate_neighbours(self, pos):
        """ calculate the number of neighbours of cell pos """
        neighbours = 0
        pos_x, pos_y = pos
        for y in range(-1, 2):
            for x in range(-1, 2):
                if (x == 0 and y == 0):
                    continue
                else:
                    neighbours += self.world.get((pos_x + x, pos_y + y), 0)
        return neighbours

    def update_cell(self, new_world, pos):
        """ Update the cell at position pos """
        neighbours = self.calculate_neighbours(pos)
        new_cell = self._new_cell(self.world.get((pos[0], pos[1]),
                                                 0), neighbours)
        if new_cell == 1:
            new_world[(pos)] = 1
        return new_world

    def update_neighbours(self, new_world, pos, updated_cells):
        """Update the cells in new_world around cell in position pos"""
        for x in range(-1, 2):
            for y in range(-1, 2):
                if (x, y) in updated_cells:
                    continue
                else:
                    new_world = self.update_cell(new_world,
                                                 (pos[0] + x, pos[1] + y))
                    updated_cells.append((pos[0] + x, pos[y] + y))
        return new_world, updated_cells

    def update(self):
        """ Update the current world one step """
        new_world = {}
        updated_cells = []
        for pos, cell in self.world.items():
            new_world, updated_cells = self.update_neighbours(new_world, pos,
                                                              updated_cells)
        self.world = new_world

    def __str__(self):
        string = ""
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.world.get((x, y), False):
                    string += "#"
                else:
                    string += "-"
            string += "\n"
        return string


class Game:
    def __init__(self, start=False, mode="screen", size_x=40, size_y=40):
        self.size_y = size_y
        self.size_x = size_x
        self.world = World(size_x, size_y)
        self.top_corner = (0, 0)
        self.bottom_corner = (size_x, size_y)
        if start == "gliders":
            if size_x < 40:
                print("Needs at least 40 pixels wide for gliders")
                sys.exit(1)
            elif size_y < 10:
                print("Needs at least 10 pixels long for gliders")
                sys.exit(1)
            else:
                self.gliders()

        self.mode = mode

    def initialize_screen(self):
        """ Initialize curses """
        if self.mode == "curses":
            self.screen = curses.initscr()
            self.screen.border(0)

            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)
            curses.curs_set(0)

    def gliders(self):
        """ Set the world to Gosper Glider Gun"""
        #TODO Fix with dictionary world
        logging.info("Generating Gosper Glider Gun world")
        world = [[0 for x in range(self.size_x)] for y in range(self.size_y)]
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

    def ask_user(self, question):
        """ Ask the users a question, return answer as string """
        self.screen.addstr(self.size_y // 2, self.size_x // 2, question + ' ')
        answer = self.screen.getstr().decode("UTF-8")
        return answer

    def prompt(self):
        """ Wait for user input and update world:
            space: continue one generation
            up: move screen up
            left: move screen left
            down: move screen down
            right: move screen right
        """
        answer = self.screen.getch()
        logging.debug("Got char %d, symbol %c" % (answer, chr(answer)))
        if answer == ord('w') or answer == curses.KEY_UP:
            # Move world down
            self.top_corner = (self.top_corner[0] - 1, self.top_corner[1])
            self.bottom_corner = (self.bottom_corner[0] - 1,
                                  self.bottom_corner[1])
            self.print_world()
        elif answer == ord('s') or answer == curses.KEY_DOWN:
            # Move world up
            self.top_corner = (self.top_corner[0] + 1, self.top_corner[1])
            self.bottom_corner = (self.bottom_corner[0] + 1,
                                  self.bottom_corner[1])
            self.print_world()
        elif answer == ord('a') or answer == curses.KEY_LEFT:
            # Move world right
            self.top_corner = (self.top_corner[0], self.top_corner[1] - 1)
            self.bottom_corner = (self.bottom_corner[0],
                                  self.bottom_corner[1] - 1)
            self.print_world()
        elif answer == ord('d') or answer == curses.KEY_RIGHT:
            # Move world left
            self.top_corner = (self.top_corner[0], self.top_corner[1] + 1)
            self.bottom_corner = (self.bottom_corner[0],
                                  self.bottom_corner[1] + 1)
            self.print_world()
        elif answer == ord(" "):
            # Update world
            self.world.update()
            self.print_world()
        elif answer == ord("q"):
            # quit game
            self.kill_screen()
            sys.exit(0)
        else:
            self.prompt()

    def print_world(self):
        if self.mode == "curses":
            self.world.print_curses(self.screen, self.top_corner,
                                    self.bottom_corner)
        elif self.mode == "screen":
            self.world.print_screen()
        else:
            pass

    def kill_screen(self):
        """ Kill the screen and cleanup """
        if self.mode == "curses":
            curses.endwin()

    def animate(self, steps, dt=0.5):
        """ Update and print the screen 'step' times"""
        logging.info("Started animation")
        for i in range(steps):
            self.world.update()
            self.print_world()
            time.sleep(dt)
        logging.info("Animation finished")


signal.signal(signal.SIGINT, signal_handler)
