""" Tests for game of life """
from itertools import combinations

import pytest

from .context import game_of_life as gol


NEIGHBOURS = [(x, y)
              for x in range(3)
              for y in range(3)
              if not (x == 1 and y == 1)]


class TestWorldInit:
    def test_new_world_is_empty(self):
        world = gol.World(randomize=False)
        assert len(world) == 0

    @pytest.mark.parametrize("num", range(16))
    def test_random_init_contains_correct_number_of_alive_cells(self, num):
        world = gol.World(randomize=False, size_x=4, size_y=4)
        world.randomize(num)
        assert len(world) == num

    def test_random_init_with_too_many_cells_raises_exception(self):
        world = gol.World(randomize=False, size_x=3, size_y=3)
        with pytest.raises(ValueError):
            world.randomize(3 * 3 + 1)

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
