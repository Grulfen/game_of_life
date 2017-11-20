""" Test for the World class of game of life """

# pylint: disable=no-self-use
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

from itertools import combinations
import pytest  # type: ignore

from .context import game_of_life as gol


NEIGHBOURS = [(x, y)
              for x in range(-1, 2)
              for y in range(-1, 2)
              if not (x == 0 and y == 0)]


@pytest.fixture
def world():
    return gol.World(size_x=10, size_y=10)


class TestWorldPositions:
    """ Test calculation of max and min pos of world """
    def test_min_pos_empty_world_is_0_0(self, world):
        assert world.min_pos() == (0, 0)

    def test_max_pos_empty_world_is_0_0(self, world):
        assert world.max_pos() == (0, 0)

    @pytest.mark.parametrize("pos",
                             [(1, 4),
                              (-4, -15),
                              (-54, 1000),
                              (74, -125)])
    def test_one_cell_is_both_min_and_max(self, pos, world):
        world.set_cell(pos)
        assert world.max_pos() == pos and world.min_pos() == pos

    def test_bounding_rectangle(self, world):
        """
        Alive cells    Bounding rectangle
        --x-            X+++
        ---x        ->  +..+
        x---            +..+
        --x-            +++X

        """
        positions = [(0, 2), (2, 0), (3, 1), (2, 3)]
        for pos in positions:
            world.set_cell(pos)
        assert world.min_pos() == (0, 0) and world.max_pos() == (3, 3)


class TestPrintWorld:
    """ Test printing the world """
    def test_print_empty_world(self, capsys, world):
        print(world)
        out, _ = capsys.readouterr()
        assert out == "\n"

    def test_print_one_cell_world(self, capsys, world):
        world.set_cell((1, 1))
        print(world)
        out, _ = capsys.readouterr()
        assert out == gol.ALIVE_SYMBOL + "\n"

    def test_print_screen_3x4_world(self, capsys, world):
        """
        --x-
        -x-x
        x---

        """
        positions = [(0, 2), (1, 1), (2, 0), (3, 1)]
        for pos in positions:
            world.set_cell(pos)
        print(world)
        out, _ = capsys.readouterr()
        string = "\n".join([
            "{d}{d}{a}{d}".format(d=gol.DEAD_SYMBOL, a=gol.ALIVE_SYMBOL),
            "{d}{a}{d}{a}".format(d=gol.DEAD_SYMBOL, a=gol.ALIVE_SYMBOL),
            "{a}{d}{d}{d}".format(d=gol.DEAD_SYMBOL, a=gol.ALIVE_SYMBOL),
            ])
        assert out == string + "\n"


class TestWorldInit:
    """ Test initial world state """
    def test_new_world_is_empty(self, world):
        assert not world

    @pytest.mark.parametrize("num", range(16))
    def test_random_init_contains_correct_number_of_alive_cells(self, num, world):
        world.randomize(num, size_x=4, size_y=4)
        assert len(world) == num

    def test_random_init_with_too_many_cells_raises_exception(self, world):
        with pytest.raises(ValueError):
            world.randomize(3 * 3 + 1, size_x=3, size_y=3)


class TestWorldNeighbours:
    """ Test the neighbours calculation """

    def test_has_correct_neighbours(self, world):
        position = (2, 2)
        assert sorted(world.neighbours(position)) == sorted((position[0] + x, position[1] + y)
                                                            for x, y in NEIGHBOURS)


class TestUpdateCells:
    """ Test updating the world some generation """

    def test_step_empty_world_is_empty(self, world):
        world.update()
        assert not world

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
            world = gol.World(3, 3)
            for x, y in positions:
                world.set_cell((x, y))
            world.update()
            assert world[(0, 0)] == alive

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
            world = gol.World(3, 3)
            world.set_cell((0, 0))
            for x, y in positions:
                world.set_cell((x, y))
            world.update()
            assert world[(0, 0)] == alive
