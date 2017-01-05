from .context import game_of_life as gol


def test_zero_world_is_empty():
    world = gol.World.zero()
    assert len(world) == 0
