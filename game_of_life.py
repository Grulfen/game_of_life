# game_of_life.py
# Conway's game of life
import curses
import time
import random
import signal
import sys
import logging
import collections

logging.basicConfig(filename="life.log", filemode="w",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def signal_handler(signal, frame):
    """ Make Ctrl-c exit close curses window """
    logging.info("Caught SIGINT, closing")
    curses.endwin()
    sys.exit(0)


class World:
    def __init__(self, start=False, mode="screen", size_x=40, size_y=40):
        self.size_y = size_y
        self.size_x = size_x
        self.zero()
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

    def initialize_screen(self):
        """ Initialize curses """
        if self.mode == "curses":
            self.screen = curses.initscr()
            self.screen.border(0)

    def zero(self):
        """ Set the world to all zeros """
        logging.info("Generating empty world")
        world = collections.defaultdict(lambda: 0)
        self.world = world

    def gliders(self):
        """ Set the world to Gosper Glider Gun"""
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

    def random_world(self):
        logging.info("Generating random world")
        for i in range(self.size_x * self.size_y):
            x = random.randint(0, self.size_x)
            y = random.randint(0, self.size_x)
            self.world[(x, y)] = 1

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

    def update_cell(self, new_world, pos):
        """ Update the cell at position pos """
        neighbours = 0
        cell_x, cell_y = pos
        for y in range(-1, 2):
            for x in range(-1, 2):
                if not(x == 0 and y == 0):
                    neighbours += self.world[(x, y)]
        new_cell = self._new_cell(self.world[(pos[0], pos[1])], neighbours)
        if new_cell == 1:
            new_world[(pos[0], pos[y])] = 1
        return new_world

    def update_neighbours(self, new_world, pos):
        """Update the cells in new_world around cell in position pos"""
        for x in range(-1, 2):
            for y in range(-1, 2):
                new_world = self.update_cell(new_world,
                                             (pos[0] + x, pos[1] + y))
        return new_world

    def update(self):
        """ Update the current world one step """
        new_world = collections.defaultdict(lambda: 0)
        #TODO Fix update to dictionary type world
        world = self.world.copy()
        for pos, cell in world.items():
            if cell == 1:
                new_world = self.update_neighbours(new_world, pos)
        self.world = new_world

    def ask_user(self, question):
        """ Ask the users a question, return answer as string """
        self.screen.addstr(self.size_y // 2, self.size_x // 2, question + ' ')
        answer = self.screen.getstr().decode("UTF-8")
        return answer

    def again(self):
        """ Prompt user for continued animation, return False or the number of
        generations to animate """
        self.screen.addstr(self.size_y // 2, self.size_x // 2,
                           "Continue? Y/n\n")
        answer = self.screen.getch()
        logging.debug("Got char %d, symbol %c" % (answer, chr(answer)))
        if answer == 121 or answer == 89 or answer == 10:
            return self.ask_user("How many generations?")
        elif answer == 110 or answer == 78:
            return False
        else:
            return self.again()

    def print_world(self):
        if self.mode == "curses":
            self._print_curses()
        elif self.mode == "screen":
            self._print_to_screen()
        else:
            pass

    def _print_to_screen(self):
        """Print world to screen"""
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.world[(x, y)]:
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

    def save(self, filename="world.hur"):
        """ Save the world to filename """
        f = open(filename, 'w')
        f.write("{0:d},{1:d}\n".format(self.size_x, self.size_y))
        tmp_list = []
        cnt = 0
        current = 0
        for line in self.world:
            for cell in line:
                if cell == current:
                    cnt += 1
                else:
                    current = 1 - current
                    tmp_list.append(cnt)
                    cnt = 1
        if cnt != 0:
            tmp_list.append(cnt)
        f.write(','.join(str(s) for s in tmp_list))
        f.close()

    def load(self, filename="world.hur"):
        """ Load the world from filename """
        logging.info("Loading file {0}".format(filename))
        f = open(filename, 'r')
        size = f.readline()
        size = size.split(',')
        try:
            x, y = int(size[0]), int(size[1])
            logging.info("World size is {0:d}, {1:d}".format(x, y))
        except ValueError:
            logging.error("File not in correct format")
            sys.exit(1)
        world_compressed = f.readline().split(',')
        f.close()
        world_list = []
        current = 0
        for cnt in world_compressed:
            world_list.extend([current for x in range(int(cnt))])
            current = 1 - current
        self.size_x = x
        self.size_y = y
        self.zero()
        #logging.debug(world_list)
        for cnt in range(y):
            #FIXME funkar inte att ladda världen
            logging.debug("y*x = {0}, (y+1*x = {1}".format(y * x, (y + 1) * x))
            #logging.debug(world_list[cnt * x : (cnt + 1) * x])
            self.world[cnt] = world_list[cnt * x: (cnt + 1) * x]

    def animate(self, steps, dt=0.05):
        """ Update and print the screen 'step' times"""
        logging.info("Started animation")
        for i in range(steps):
            self.update()
            self.print_world()
            time.sleep(dt)
        logging.info("Animation finished")

    def __str__(self):
        tmp_str = []
        tmp_line = []
        for line in self.world:
            for cell in line:
                tmp_line.append(cell)
            tmp_str.append(''.join(str(s) for s in tmp_line))
            tmp_line = []
        return('\n'.join(str(s) for s in tmp_str))


signal.signal(signal.SIGINT, signal_handler)
