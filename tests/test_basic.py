""" Tests for game of life """
from itertools import combinations

import pytest

from .context import game_of_life as gol


NEIGHBOURS = [(x, y)
              for x in range(3)
              for y in range(3)
              if not (x == 1 and y == 1)]


class TestWorldPositions:
    def test_min_pos_empty_world_is_0_0(self):
        world = gol.World(randomize=False)
        assert world.min_pos() == (0, 0)


    def test_max_pos_empty_world_is_0_0(self):
        world = gol.World(randomize=False)
        assert world.max_pos() == (0, 0)

    @pytest.mark.parametrize("pos",
                             [(1, 4),
                              (-4, -15),
                              (-54, 1000),
                              (74, -125)])
    def test_one_cell_is_both_min_and_max(self, pos):
        world = gol.World(randomize=False)
        world.set_cell(pos)
        assert world.max_pos() == pos and world.min_pos() == pos

    def test_bounding_rectangle(self):
        """
        Alive cells    Bounding rectangle
        --x-            X+++
        ---x        ->  +..+
        x---            +..+
        --x-            +++X

        """
        world = gol.World(randomize=False)
        positions = [(0, 2), (2, 0), (3, 1), (2, 3)]
        for pos in positions:
            world.set_cell(pos)
        assert world.min_pos() == (0, 0) and world.max_pos() == (3, 3)


class TestPrintWorld:
    def test_print_empty_world(self, capsys):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        print(world)
        out, _ = capsys.readouterr()
        assert out == "\n"

    def test_print_screen_empty_world(self, capsys):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        gol.print_screen(world)
        out, _ = capsys.readouterr()
        assert out == "\n"

    def test_print_one_cell_world(self, capsys):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        world.set_cell((1, 1))
        print(world)
        out, _ = capsys.readouterr()
        assert out == gol.ALIVE_SYMBOL + "\n"

    def test_print_screen_one_cell_world(self, capsys):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        world.set_cell((1, 1))
        gol.print_screen(world)
        out, _ = capsys.readouterr()
        assert out == gol.ALIVE_SYMBOL + "\n"

    def test_print_screen_one_cell_world_with_surroundings(self, capsys):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        world.set_cell((1, 1))
        gol.print_screen(world, (0, 0), (2, 2))
        out, _ = capsys.readouterr()
        string = "\n".join([
            gol.DEAD_SYMBOL * 3,
            gol.DEAD_SYMBOL + gol.ALIVE_SYMBOL + gol.DEAD_SYMBOL,
            gol.DEAD_SYMBOL * 3])
        assert out == string + "\n"


class TestWorldInit:
    def test_new_world_is_empty(self):
        world = gol.World(randomize=False)
        assert len(world) == 0

    @pytest.mark.parametrize("num", range(16))
    def test_random_init_contains_correct_number_of_alive_cells(self, num):
        world = gol.World(randomize=False)
        world.randomize(num, size_x=4, size_y=4)
        assert len(world) == num

    def test_random_init_with_too_many_cells_raises_exception(self):
        world = gol.World(randomize=False)
        with pytest.raises(ValueError):
            world.randomize(3 * 3 + 1, size_x=3, size_y=3)

class TestUpdateCells:

    def test_step_empty_world_is_empty(self):
        world = gol.World(randomize=False)
        world.update()
        assert len(world) == 0

    @pytest.mark.parametrize("alive_cells, alive",
                             [(list(combinations(NEIGHBOURS, 2)), 0),
                              (list(combinations(NEIGHBOURS, 3)), 1),
                              (list(combinations(NEIGHBOURS, 4)), 0)])
    def test_dead_cell(self, alive_cells, alive):
        """
        ----------------------+------------------------
        2 neighbours -> dead  | 3 neighbours -> lives
        xx-    ???            | xxx    ???
        --- -> ?-?            | --- -> ?x?
        ---    ???            | ---    ???
                              |
        ----------------------+------------------------
        4 neighbours -> dead  |
        xxx    ???            |
        --- -> ?-?            |
        --x    ???            |
                              |
        ----------------------+------------------------
        """
        for positions in alive_cells:
            world = gol.World(3, 3, randomize=False)
            for x, y in positions:
                world.set_cell((x, y))
            world.update()
            assert world[(1, 1)] == alive

    @pytest.mark.parametrize("alive_cells,alive",
                             [(list(combinations(NEIGHBOURS, 0)), 0),
                              (list(combinations(NEIGHBOURS, 1)), 0),
                              (list(combinations(NEIGHBOURS, 2)), 1),
                              (list(combinations(NEIGHBOURS, 3)), 1),
                              (list(combinations(NEIGHBOURS, 4)), 0)])
    def test_live_cell(self, alive_cells, alive):
        """
        ----------------------+------------------------
        0 neighbours -> dies  |  1 neighbour -> dies
        ---    ???            |  ---    ???
        -x- -> ?-?            |  -x- -> ?-?(
        ---    ???            |  --x    ???
                              |
        ----------------------+------------------------
        2 neighbours -> lives |  3 neighbours -> lives
        --x    ???            |  --x    ???
        -x- -> ?x?            |  xx- -> ?x?
        --x    ???            |  --x    ???
        ----------------------+------------------------
        4 neighbours -> dies  |
        --x    ???            |
        xx- -> ?x?            |
        x-x    ???            |
        ----------------------+------------------------
        """
        for positions in alive_cells:
            world = gol.World(3, 3, randomize=False)
            world.set_cell((1, 1))
            for x, y in positions:
                world.set_cell((x, y))
            world.update()
            assert world[(1, 1)] == alive
