""" Tests for game of life """
from .context import game_of_life as gol
from itertools import combinations
import pytest


NEIGHBOURS = [(x, y)
              for x in range(3)
              for y in range(3)
              if not (x == 1 and y == 1)]


def test_new_world_is_empty():
    world = gol.World(randomize=False)
    assert len(world) == 0


def test_step_empty_world_is_empty():
    world = gol.World(randomize=False)
    world.update()
    assert len(world) == 0


@pytest.mark.parametrize("alive_cells, alive",
                         [(list(combinations(NEIGHBOURS, 2)), 0),
                          (list(combinations(NEIGHBOURS, 3)), 1),
                          (list(combinations(NEIGHBOURS, 4)), 0)])
def test_dead_cell(alive_cells, alive):
    """

    2 neighbours -> stays dead
    xx-    ???
    --- -> ?-?
    ---    ???

    3 neighbours -> lives
    xxx    ???
    --- -> ?x?
    ---    ???

    4 neighbours -> stays dead
    xxx    ???
    --- -> ?-?
    --x    ???


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
def test_live_cell(alive_cells, alive):
    """

    0 neighbours -> dies
    ---    ???
    -x- -> ?-?
    ---    ???

    1 neighbour -> dies
    ---    ???
    -x- -> ?-?
    --x    ???

    2 neighbours -> survives
    --x    ???
    -x- -> ?x?
    --x    ???

    3 neighbours -> survives
    --x    ???
    xx- -> ?x?
    --x    ???

    4 neighbours -> dies
    --x    ???
    xx- -> ?x?
    x-x    ???

    """
    for positions in alive_cells:
        world = gol.World(3, 3, randomize=False)
        world.set_cell((1, 1))
        for x, y in positions:
            world.set_cell((x, y))
        world.update()
        assert world[(1, 1)] == alive
