""" Conways game of life in python """
import curses
import time
import random
import signal
import sys
from itertools import product

# pylint: disable=unused-import
from typing import Dict, Tuple, NewType, Any, Set, Callable, Iterable
# pylint: enable=unused-import

# pylint: disable=invalid-name
Pos = Tuple[int, int]
# pylint: enable=invalid-name

DEAD_SYMBOL = '-'
ALIVE_SYMBOL = '#'


def signal_handler(_sig, _frame):
    """ Make Ctrl-c exit close curses window """
    curses.endwin()
    sys.exit(0)


class World:
    """ World class """
    def __init__(self, size_x=10, size_y=10, randomize=False):
        # type : (int, int, Bool) -> None
        self.make_neigh_cache()
        self.world = set()  # type: Set[Pos]
        if randomize:
            self.randomize(int(size_x * size_y * 1 / 3), size_x, size_y)

    def randomize(self, num, size_x, size_y):
        # type: (int, int, int) -> None
        """ Create @num number of alive cells between (0, 0) and (size_x, size_y) """
        if num > size_x * size_y:
            raise ValueError("Trying to add more cells than space in world")
        self.world = set()
        all_cells = product(range(size_x), range(size_y))  # type: Iterable[Any]
        for cell in random.sample(list(all_cells), num):
            self.world.add(cell)

    def _find_corner(self, func, empty_pos):
        # type: (Callable[[Iterable[int]], int], Pos) -> Pos
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
        return self._find_corner(max, (0, 0))

    @staticmethod
    def _new_cell(cell, neighbours):
        # type: (bool, int) -> bool
        """Returns the new cell based on how many alive neighbours there is"""
        if cell:
            return 2 <= neighbours < 4
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
        # type: (Pos) -> None
        """ Create a live cell at @pos """
        self.world.add(pos)

    def lines(self, top_left=None, bottom_right=None):
        # type: (World, Pos, Pos) -> List[str]
        """Return @world between @top_left and @bottom_right as list of strings """
        if top_left is None:
            top_left = self.min_pos()

        if bottom_right is None:
            bottom_right = self.max_pos()

        world_lines = []
        if not self.world:
            return []

        for y in range(top_left[1], bottom_right[1] + 1):
            string = ""
            for x in range(top_left[0], bottom_right[0] + 1):
                if (x, y) in self.world:
                    string += ALIVE_SYMBOL
                else:
                    string += DEAD_SYMBOL
            world_lines.append(string)
        return world_lines

    def __str__(self):
        # type: () -> str
        return "\n".join(self.lines())

    def __getitem__(self, pos):
        # type: (Pos) -> int
        return 1 if pos in self.world else 0

    def __len__(self):
        return len(self.world)


class Game:
    """ Class handling the user interface """
    def __init__(self, size_x=20, size_y=20, randomize=True):

        self.size_x = size_x
        self.size_y = size_y

        self.world = World(self.size_x, self.size_y, randomize)
        self.top_corner = (0, 0)
        self.bottom_corner = (self.size_x, self.size_y)

    def move_left(self):
        """ Move the viewing window of the world to the left """
        self.top_corner = (self.top_corner[0] - 1, self.top_corner[1])
        self.bottom_corner = (self.bottom_corner[0] - 1, self.bottom_corner[1])

    def move_right(self):
        """ Move the viewing window of the world to the right """
        self.top_corner = (self.top_corner[0] + 1, self.top_corner[1])
        self.bottom_corner = (self.bottom_corner[0] + 1, self.bottom_corner[1])

    def move_up(self):
        """ Move the viewing window of the world to the up """
        self.top_corner = (self.top_corner[0], self.top_corner[1] + 1)
        self.bottom_corner = (self.bottom_corner[0], self.bottom_corner[1] + 1)

    def move_down(self):
        """ Move the viewing window of the world to the down """
        self.top_corner = (self.top_corner[0], self.top_corner[1] - 1)
        self.bottom_corner = (self.bottom_corner[0], self.bottom_corner[1] - 1)

    def handle_command(self, command):
        """ Handle commands
            space: continue one generation
            w or up: move screen up
            a or left: move screen left
            s or down: move screen down
            f or right: move screen right
            r: ask user how many generations to run and then run them
        """

        if command == ord('w') or command == curses.KEY_UP:
            self.move_down()
        elif command == ord('s') or command == curses.KEY_DOWN:
            self.move_up()
        elif command == ord('a') or command == curses.KEY_LEFT:
            self.move_left()
        elif command == ord('d') or command == curses.KEY_RIGHT:
            self.move_right()
        elif command == ord("r"):
            # Ask user how many generations to animate
            try:
                num = int(self.ask_user("How many generations"))
            except ValueError:
                self.ask_user("Enter integer please")
                return
            self.animate(num, 0.001)

        elif command == ord(" "):
            self.world.update()

        elif command == ord("q"):
            self.exit("Quitting", 0)

    def animate(self, steps, timestep=0.2):
        """ Update and print the screen 'step' times"""
        for _ in range(steps):
            self.world.update()
            self.print_world()
            time.sleep(timestep)

    def exit(self, msg=None, status=0):
        """ Exit game of life """
        self.kill()
        if msg:
            print(msg)
        if not isinstance(status, int):
            status = 0
        sys.exit(status)

    def kill(self):
        """ Should be implemented by child class """
        raise NotImplementedError

    def ask_user(self, question):
        """ Should be implemented by child class """
        raise NotImplementedError

    def print_world(self) -> None:
        """ Should be implemented by child class """
        raise NotImplementedError


class CursesGame(Game):
    """ Game of life with ncurses UI """

    def __init__(self, size_x=20, size_y=20, randomize=True, max_size=False):
        self.size_x = size_x
        self.size_y = size_y
        self.init_curses(max_size)
        super().__init__(self.size_x, self.size_y, randomize)

    def init_curses(self, max_size: bool):
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

    def print_world(self) -> None:
        """ Print the world ncurses """

        list_of_lines = self.world.lines(self.top_corner, self.bottom_corner)

        # TODO Add colors?
        for line_no, line in enumerate(list_of_lines):
            self.screen.addstr(line_no + 1, 1, line)
        self.screen.refresh()

    def get_command_from_user(self) -> int:
        """ Get a command from user using curses """
        return self.screen.getch()

    def ask_user(self, question):
        """ Ask the users a question, return answer as string """
        q_size = len(question)
        self.screen.addstr(self.size_y // 2, self.size_x // 2 - q_size // 2,
                           question + ' ', curses.color_pair(1))
        answer = self.screen.getstr().decode("UTF-8")
        return answer

    def kill(self):
        """ Close the curses window """
        curses.endwin()


class ScreenGame(Game):
    """ Game of life with terminal UI """

    def print_world(self) -> None:
        """ print the world to terminal """
        print(self.world)

    def get_command_from_user(self) -> int:
        """ Get a command from user using terminal """
        raise NotImplementedError('Prompt is not supported for "screen" mode worlds')

    def kill(self):
        """ Nothing needs to be done to cleanup a terminal based ui """
        pass


signal.signal(signal.SIGINT, signal_handler)
