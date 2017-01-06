""" Conways game of life in python """
import curses
import time
import random
import signal
import sys

# pylint: disable=unused-import
from typing import Dict, Tuple, NewType, Any, Set, Callable, Iterator

# pylint: disable=invalid-name
Pos = Tuple[int, int]


def signal_handler(_sig, _frame):
    """ Make Ctrl-c exit close curses window """
    curses.endwin()
    sys.exit(0)


class World:
    """ World class """
    def __init__(self, size_x=10, size_y=10, randomize=True):
        # type : (int, int, Bool) -> None
        self.size_y = size_y
        self.size_x = size_x
        self.make_neigh_cache()
        self.world = set()  # type: Set[Pos]
        if randomize:
            self.random(int(size_x * size_y * 1 / 3))

    def random(self, num):
        # type: (int) -> None
        """ Create @num number of alive cells """
        self.world = set()
        for _ in range(num):
            x = random.randint(0, self.size_x)
            y = random.randint(0, self.size_y)
            self.world.add((x, y))

    def _find_corner(self, func, empty_pos):
        # type: (Callable[[Iterator[int]], int], Pos) -> Pos
        """ Helper function to find corners of bounding rectangle of alive cells """
        if not self.world:
            # World empty
            return empty_pos
        else:
            x = func(cell[0] for cell in self.world)
            y = func(cell[1] for cell in self.world)
        return (x, y)

    def min_pos(self):
        # type: () -> Pos
        """ Return the top left position of the bounding rectangle of all alive cells """
        return self._find_corner(min, (0, 0))

    def max_pos(self):
        # type: () -> Pos
        """ Return the bottom, right position with alive cell"""
        return self._find_corner(max, (10, 10))

    @staticmethod
    def _new_cell(cell, neighbours):
        # type: (bool, int) -> bool
        """Returns the new cell based on how many alive neighbours there is"""
        if cell:
            return 2 <= neighbours < 4
        else:
            return neighbours == 3

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
        x, y = pos
        for d_x, d_y in self._neigh_cache:
            neighbour_pos = (x + d_x, y + d_y)
            neighbours += 1 if neighbour_pos in self.world else 0
        return neighbours

    def update_cell(self, new_world, pos):
        # type: (Set[Pos], Pos) -> Set[Pos]
        """ Update the cell at position pos """
        neighbours = self.calculate_neighbours(pos)
        new_cell = self._new_cell(pos in self.world, neighbours)
        if new_cell:
            new_world.add(pos)
        return new_world

    def update_neighbours(self, new_world, pos, updated_cells):
        # type: (Set[Pos], Pos, Set[Pos]) -> Tuple[Set[Pos], Set[Pos]]
        """Update the cells in new_world around cell in position pos"""
        for x, y in self._makro_cell_cache:
            if (pos[0] + x, pos[1] + y) in updated_cells:
                # Cell already updated, continue
                continue
            else:
                # Cell not updated yet, updating
                new_world = self.update_cell(new_world, (pos[0] + x, pos[1] + y))
                updated_cells.add((pos[0] + x, pos[1] + y))
        return new_world, updated_cells

    def update(self):
        # type: () -> None
        """ Update the current world one step """
        new_world = set()  # type: Set[Pos]
        updated_cells = set()  # type: Set[Pos]
        for pos in self.world:
            new_world, updated_cells = self.update_neighbours(new_world, pos, updated_cells)
        self.world = new_world

    def set_cell(self, pos):
        """ Create a live cell at @pos """
        # type: (Pos) -> None
        self.world.add(pos)

    def __str__(self):
        # type: () -> str
        string = ""
        for y in range(self.size_y):
            for x in range(self.size_x):
                if (x, y) in self.world:
                    string += "#"
                else:
                    string += "-"
            string += "\n"
        return string

    def __getitem__(self, pos):
        # type: (Pos) -> int
        return 1 if pos in self.world else 0

    def __len__(self):
        return len(self.world)


def print_screen(world, start_pos=None, end_pos=None):
    # type: (World, Pos, Pos) -> None
    """Print @world between @start_pos and @end_pos to stdout"""
    if start_pos and end_pos:
        # Print world from start_pos to end_pos
        start_x, start_y = start_pos
        end_x, end_y = end_pos
    else:
        # No positions specified. Print the whole world
        start_x, start_y = world.min_pos()
        end_x, end_y = world.max_pos()

    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if world[(x, y)]:
                print("#", end="")
            else:
                print("_", end="")
        print()


def print_curses(world, screen, start_pos, end_pos):
    # type: (World, Any, Pos, Pos) -> None
    """Print the @world from @start_pos to @end_pos on ncurses @screen"""
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    # TODO: Rewrite this
    list_of_lines = [''.join(
        ['#' if world[(x, y)] else ','
         for x in range(start_x, end_x + 1)])
                     for y in range(start_y, end_y + 1)]
    # TODO Add colors?
    for line_no, line in enumerate(list_of_lines):
        screen.addstr(line_no + 1, 1, line)
    screen.refresh()


class Game:
    """ Class handling the user interface """
    def __init__(self, mode="screen", size_x=20, size_y=20,
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
            print_curses(self.world, self.screen,
                         self.top_corner,
                         self.bottom_corner)
        elif self.mode == "screen":
            print_screen(self.world)
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
