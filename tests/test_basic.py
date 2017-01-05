from .context import game_of_life as gol


def test_zero_world_is_empty():
    world = gol.World(10, 10)
    world.zero()
    assert len(world.world) == 0
