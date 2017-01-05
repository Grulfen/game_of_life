""" Conways game of life in python """
import curses
import time
import random
import signal
import sys

# pylint: disable=unused-import
from typing import Dict, Tuple, NewType, Any, Set

# pylint: disable=invalid-name
Pos = Tuple[int, int]


def signal_handler(_sig, _frame):
    """ Make Ctrl-c exit close curses window """
    curses.endwin()
    sys.exit(0)


# TODO: Separate visualisation from World class

class World:
    """ World class """
    def __init__(self, size_x=10, size_y=10):
        self.size_y = size_y
        self.size_x = size_x
        self.make_neigh_cache()
        self.world = self.zero()
        self.random(int(size_x * size_y * 1 / 3))

    @staticmethod
    def zero():
        # type: () -> Dict[Pos, int]
        """ Set the world to all zeros """
        return {}

    def random(self, num):
        # type: (int) -> None
        """ Create @num number of alive cells """
        self.zero()
        for _ in range(num):
            x = random.randint(0, self.size_x)
            y = random.randint(0, self.size_y)
            self.world[(x, y)] = 1

    def print_screen(self, start_pos=None, end_pos=None):
        # type: (Pos, Pos) -> None
        """Print world to screen"""
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
                if self.world.get((x, y), False):
                    print("#", end="")
                else:
                    print("_", end="")
            print()

    def print_curses(self, screen, start_pos, end_pos):
        # type: (Any, Pos, Pos) -> None
        """Print the world from start_pos to end_pos on ncurses screen"""
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        # TODO: Rewrite this
        list_of_lines = [''.join(
            ['#' if self.world.get((x, y), False) else ','
             for x in range(start_x, end_x + 1)])
                         for y in range(start_y, end_y + 1)]
        # TODO Add colors?
        for line_no, line in enumerate(list_of_lines):
            screen.addstr(line_no + 1, 1, line)
        screen.refresh()

    def min_pos(self):
        # type: () -> Pos
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
        # type: () -> Pos
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

    @staticmethod
    def _new_cell(cell, neighbours):
        # type: (int, int) -> int
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

    def make_neigh_cache(self):
        # type: () -> None
        """ Create lists of relative positions of neighbours and
            cells in a 3x3 block """
        self._neigh_cache = [(x, y)
                             for x in range(-1, 2)
                             for y in range(-1, 2)
                             if not (x == 0 and y == 0)]
        self._makro_cell_cache = [(x, y)
                                  for x in range(-1, 2)
                                  for y in range(-1, 2)]

    def calculate_neighbours(self, pos):
        # type: (Pos) -> int
        """ calculate the number of neighbours of cell pos """
        neighbours = 0
        pos_x, pos_y = pos
        for x, y in self._neigh_cache:
            neighbours += self.world.get((pos_x + x, pos_y + y), 0)
        return neighbours

    def update_cell(self, new_world, pos):
        # type: (Dict[Pos, int], Pos) -> Dict[Pos, int]
        """ Update the cell at position pos """
        neighbours = self.calculate_neighbours(pos)
        new_cell = self._new_cell(self.world.get((pos[0], pos[1]), 0),
                                  neighbours)
        if new_cell == 1:
            new_world[(pos)] = 1
        return new_world

    def update_neighbours(self, new_world, pos, updated_cells):
        # type: (Dict[Pos, int], Pos, Set[Pos]) -> Tuple[Dict[Pos, int], Set[Pos]]
        """Update the cells in new_world around cell in position pos"""
        for x, y in self._makro_cell_cache:
            if (pos[0] + x, pos[1] + y) in updated_cells:
                # Cell already updated, continue
                continue
            else:
                # Cell not updated yet, updating
                new_world = self.update_cell(new_world,
                                             (pos[0] + x, pos[1] + y))
                updated_cells.add((pos[0] + x, pos[1] + y))
        return new_world, updated_cells

    def update(self):
        # type: () -> None
        """ Update the current world one step """
        new_world = {}  # type: Dict[Pos, int]
        updated_cells = set()  # type: Set[Pos]
        for pos, _cell in self.world.items():
            new_world, updated_cells = self.update_neighbours(new_world, pos,
                                                              updated_cells)
        self.world = new_world

    def __str__(self):
        # type: () -> str
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
    def __init__(self, start=False, mode="screen", size_x=20, size_y=20,
                 max_size=False):

        self.size_x = size_x
        self.size_y = size_y
        self.mode = mode

        if self.mode == "curses":
            self.init_curses(max_size)

        self.world = World(self.size_x, self.size_y)
        self.top_corner = (0, 0)
        self.bottom_corner = (self.size_x, self.size_y)

    def init_curses(self, max_size):
        """ Initilize the curses screen """
        self.screen = curses.initscr()
        curses.start_color()
        if not curses.has_colors():
            self.exit("Error, no color support", 1)
        else:
            # We have color support
            # Pair 1, green on black background
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        if max_size:
            # Get maximum size of screen
            size_y_max, size_x_max = self.screen.getmaxyx()
            # Need space for border
            self.size_y, self.size_x = size_y_max - 3, size_x_max - 3

        self.screen.border(0)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        curses.curs_set(0)

    def ask_user(self, question):
        """ Ask the users a question, return answer as string """
        q_size = len(question)
        self.screen.addstr(self.size_y // 2, self.size_x // 2 - q_size // 2,
                           question + ' ', curses.color_pair(1))
        answer = self.screen.getstr().decode("UTF-8")
        return answer

    def prompt(self):
        """ Wait for user input and update world:
            space: continue one generation
            w or up: move screen up
            a or left: move screen left
            s or down: move screen down
            f or right: move screen right
            r: ask user how many generations to run and then run them
        """
        answer = self.screen.getch()
        if answer == ord('w') or answer == curses.KEY_UP:
            # Move world down
            self.top_corner = (self.top_corner[0], self.top_corner[1] - 1)
            self.bottom_corner = (self.bottom_corner[0],
                                  self.bottom_corner[1] - 1)
            self.print_world()
        elif answer == ord('s') or answer == curses.KEY_DOWN:
            # Move world up
            self.top_corner = (self.top_corner[0], self.top_corner[1] + 1)
            self.bottom_corner = (self.bottom_corner[0],
                                  self.bottom_corner[1] + 1)
            self.print_world()
        elif answer == ord('a') or answer == curses.KEY_LEFT:
            # Move world right
            self.top_corner = (self.top_corner[0] - 1, self.top_corner[1])
            self.bottom_corner = (self.bottom_corner[0] - 1,
                                  self.bottom_corner[1])
            self.print_world()
        elif answer == ord('d') or answer == curses.KEY_RIGHT:
            # Move world left
            self.top_corner = (self.top_corner[0] + 1, self.top_corner[1])
            self.bottom_corner = (self.bottom_corner[0] + 1,
                                  self.bottom_corner[1])
            self.print_world()
        elif answer == ord("r"):
            # Ask user how many generations to animate
            try:
                num = int(self.ask_user("How many generations"))
            except ValueError:
                self.ask_user("Enter integer please")
                return
            self.animate(num, 0.001)

        elif answer == ord(" "):
            # Update world
            self.world.update()
            self.print_world()

        elif answer == ord("q"):
            # quit game
            self.exit("Quitting", 0)

        else:
            self.prompt()

    def print_world(self):
        """ print the world to curses or as ascii """
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

    def exit(self, msg=None, status=0):
        """ Exit game of life """
        self.kill_screen()
        if msg:
            print(msg)
        if not isinstance(status, int):
            status = 0
        sys.exit(status)

    def animate(self, steps, timestep=0.2):
        """ Update and print the screen 'step' times"""
        for _ in range(steps):
            self.world.update()
            self.print_world()
            time.sleep(timestep)


signal.signal(signal.SIGINT, signal_handler)
