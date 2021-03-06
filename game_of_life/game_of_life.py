""" Conways game of life in python """
import curses
import time
import random
import signal
import sys
from itertools import product, chain

# pylint: disable=unused-import
from typing import Dict, Tuple, NewType, Any, Set, Callable, Iterable, List
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
    def __init__(self, size_x: int = 10, size_y: int = 10, randomize: bool = False) -> None:
        self.world = set()  # type: Set[Pos]
        if randomize:
            self.randomize(int(size_x * size_y * 1 / 3), size_x, size_y)

    def randomize(self, num: int, size_x: int, size_y: int):
        """ Create @num number of alive cells between (0, 0) and (size_x, size_y) """
        if num > size_x * size_y:
            raise ValueError("Trying to add more cells than space in world")
        self.world = set()
        all_cells = product(range(size_x), range(size_y))  # type: Iterable[Any]
        for cell in random.sample(list(all_cells), num):
            self.world.add(cell)

    def _find_corner(self, func: Callable[[Iterable[int]], int], empty_pos: Pos) -> Pos:
        """ Helper function to find corners of bounding rectangle of alive cells """
        if not self.world:
            # World empty
            return empty_pos
        else:
            x = func(cell[0] for cell in self.world)
            y = func(cell[1] for cell in self.world)
        return (x, y)

    def min_pos(self) -> Pos:
        """ Return the top left position of the bounding rectangle of all alive cells """
        return self._find_corner(min, (0, 0))

    def max_pos(self) -> Pos:
        """ Return the bottom, right position with alive cell"""
        return self._find_corner(max, (0, 0))

    @staticmethod
    def _new_cell(cell: bool, neighbours: int) -> bool:
        """Returns the new cell based on how many alive neighbours there is"""
        if cell:
            return 2 <= neighbours < 4
        return neighbours == 3

    def calculate_neighbours(self, pos: Pos) -> int:
        """ calculate the number of neighbours of cell pos """
        neighbours = 0
        x, y = pos
        for d_x, d_y in self.neighbours(pos):
            neighbour_pos = (x + d_x, y + d_y)
            neighbours += 1 if neighbour_pos in self.world else 0
        return neighbours

    @staticmethod
    def neighbours(pos: Pos) -> Iterable[Pos]:
        """ Calculate the positions of all neighbours of @pos """
        x, y = pos
        yield x - 1, y - 1
        yield x, y - 1
        yield x + 1, y - 1

        yield x - 1, y
        yield x + 1, y

        yield x - 1, y + 1
        yield x, y + 1
        yield x + 1, y + 1

    def cell_alive(self, pos: Pos) -> bool:
        """ Is this cell alive next generation """
        neighbours = self.calculate_neighbours(pos)
        return self._new_cell(pos in self.world, neighbours)

    def update(self) -> None:
        """ Update the current world one step """
        new_world = set()

        recalculate = self.world | set(chain(*(self.neighbours(pos) for pos in self.world)))

        for position in recalculate:
            if self.cell_alive(position):
                new_world.add(position)

        self.world = new_world

    def set_cell(self, pos: Pos) -> None:
        """ Create a live cell at @pos """
        self.world.add(pos)

    def lines(self, top_left: Pos = None, bottom_right: Pos = None) -> List[str]:
        """Return world between @top_left and @bottom_right as list of strings """
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

    def __str__(self) -> str:
        return "\n".join(self.lines())

    def __getitem__(self, pos: Pos) -> int:
        return 1 if pos in self.world else 0

    def __len__(self) -> int:
        return len(self.world)


class Game:
    """ Class handling the user interface """
    def __init__(self, size_x: int = 20, size_y: int = 20, randomize: bool = True) -> None:

        self.size_x = size_x
        self.size_y = size_y

        self.world = World(self.size_x, self.size_y, randomize)
        self.top_corner = (0, 0)
        self.bottom_corner = (self.size_x, self.size_y)

    def move_left(self) -> None:
        """ Move the viewing window of the world to the left """
        self.top_corner = (self.top_corner[0] - 1, self.top_corner[1])
        self.bottom_corner = (self.bottom_corner[0] - 1, self.bottom_corner[1])

    def move_right(self) -> None:
        """ Move the viewing window of the world to the right """
        self.top_corner = (self.top_corner[0] + 1, self.top_corner[1])
        self.bottom_corner = (self.bottom_corner[0] + 1, self.bottom_corner[1])

    def move_up(self) -> None:
        """ Move the viewing window of the world to the up """
        self.top_corner = (self.top_corner[0], self.top_corner[1] - 1)
        self.bottom_corner = (self.bottom_corner[0], self.bottom_corner[1] - 1)

    def move_down(self) -> None:
        """ Move the viewing window of the world to the down """
        self.top_corner = (self.top_corner[0], self.top_corner[1] + 1)
        self.bottom_corner = (self.bottom_corner[0], self.bottom_corner[1] + 1)

    def get_number_of_generations(self) -> int:
        try:
            num = int(self.ask_user("How many generations?"))
        except ValueError:
            self.ask_user("Enter integer please")
            return None
        return num

    def handle_command(self, command: int) -> None:
        """ Handle commands
            space: continue one generation
            w or up: move screen up
            a or left: move screen left
            s or down: move screen down
            f or right: move screen right
            r: ask user how many generations to run and then run them
        """

        if command == ord('w') or command == curses.KEY_UP:
            self.move_up()
        elif command == ord('s') or command == curses.KEY_DOWN:
            self.move_down()
        elif command == ord('a') or command == curses.KEY_LEFT:
            self.move_left()
        elif command == ord('d') or command == curses.KEY_RIGHT:
            self.move_right()
        elif command == ord("r"):
            num = self.get_number_of_generations()
            if num is None:
                return
            self.animate(num, 0.001)

        elif command == ord(" "):
            self.world.update()

        elif command == ord("q"):
            self.exit("Quitting", 0)

    def animate(self, steps: int, timestep: float = 0.2) -> None:
        """ Update and print the screen 'step' times"""
        for _ in range(steps):
            self.world.update()
            self.print_world()
            time.sleep(timestep)

    def exit(self, msg: str = None, status: int = 0) -> None:
        """ Exit game of life """
        self.kill()
        if msg:
            print(msg)
        sys.exit(status)

    def kill(self) -> None:
        """ Should be implemented by child class """
        raise NotImplementedError

    def ask_user(self, question: str) -> str:
        """ Should be implemented by child class """
        raise NotImplementedError

    def print_world(self) -> None:
        """ Should be implemented by child class """
        raise NotImplementedError


class CursesGame(Game):
    """ Game of life with ncurses UI """

    def __init__(self,
                 size_x: int = 20,
                 size_y: int = 20,
                 randomize: bool = True,
                 max_size: bool = False) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.init_curses(max_size)
        super().__init__(self.size_x, self.size_y, randomize)

    def init_curses(self, max_size: bool) -> None:
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

    def ask_user(self, question: str) -> str:
        """ Ask the users a question, return answer as string """
        q_size = len(question)
        self.screen.addstr(self.size_y // 2, self.size_x // 2 - q_size // 2,
                           question + ' ', curses.color_pair(1))
        answer = self.screen.getstr().decode("UTF-8")
        return answer

    def kill(self) -> None:
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

    def kill(self) -> None:
        """ Nothing needs to be done to cleanup a terminal based ui """
        pass


signal.signal(signal.SIGINT, signal_handler)
