""" Tests for game of life """

# pylint: disable=no-self-use
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name

import pytest  # type: ignore

from .context import game_of_life as gol


@pytest.fixture
def curses_game():
    game = gol.CursesGame(size_x=5, size_y=5, randomize=True)
    yield game
    game.kill()


@pytest.fixture
def game():
    return gol.ScreenGame(size_x=5, size_y=5, randomize=True)


@pytest.fixture
def empty_screen_game():
    return gol.ScreenGame(size_x=5, size_y=5, randomize=False)


class TestGame:

    def test_corners_moves_if_move_left(self, game):
        old_top_corner = game.top_corner
        old_bottom_corner = game.bottom_corner
        game.move_left()
        assert game.top_corner == (old_top_corner[0] - 1, old_top_corner[1])
        assert game.bottom_corner == (old_bottom_corner[0] - 1, old_bottom_corner[1])

    def test_corners_moves_if_move_right(self, game):
        old_top_corner = game.top_corner
        old_bottom_corner = game.bottom_corner
        game.move_right()
        assert game.top_corner == (old_top_corner[0] + 1, old_top_corner[1])
        assert game.bottom_corner == (old_bottom_corner[0] + 1, old_bottom_corner[1])

    def test_corners_moves_if_move_up(self, game):
        old_top_corner = game.top_corner
        old_bottom_corner = game.bottom_corner
        game.move_up()
        assert game.top_corner == (old_top_corner[0], old_top_corner[1] - 1)
        assert game.bottom_corner == (old_bottom_corner[0], old_bottom_corner[1] - 1)

    def test_corners_moves_if_move_down(self, game):
        old_top_corner = game.top_corner
        old_bottom_corner = game.bottom_corner
        game.move_down()
        assert game.top_corner == (old_top_corner[0], old_top_corner[1] + 1)
        assert game.bottom_corner == (old_bottom_corner[0], old_bottom_corner[1] + 1)

    def test_exit_raises_system_exit(self, game):
        with pytest.raises(SystemExit):
            game.exit()

    def test_exit_with_msg_print_message(self, game, capsys):
        with pytest.raises(SystemExit):
            game.exit("this is error message")
        out, _err = capsys.readouterr()
        assert out == "this is error message\n"

    def test_exit_exits_with_correct_code(self, game):
        with pytest.raises(SystemExit) as exit_info:
            game.exit(status=20)

        assert exit_info.value.code == 20

    def test_handle_command_w_calls_move_up(self, game, mocker):
        mocker.patch.object(game, "move_up")
        game.handle_command(ord("w"))
        assert game.move_up.called

    def test_handle_command_s_calls_move_down(self, game, mocker):
        mocker.patch.object(game, "move_down")
        game.handle_command(ord("s"))
        assert game.move_down.called

    def test_handle_command_a_calls_move_left(self, game, mocker):
        mocker.patch.object(game, "move_left")
        game.handle_command(ord("a"))
        assert game.move_left.called

    def test_handle_command_d_calls_move_right(self, game, mocker):
        mocker.patch.object(game, "move_right")
        game.handle_command(ord("d"))
        assert game.move_right.called

    def test_handle_command_q_calls_exit(self, game, mocker):
        mocker.patch.object(game, "exit")
        game.handle_command(ord("q"))
        assert game.exit.called

    def test_handle_command_space_calls_update_world(self, game, mocker):
        mocker.patch.object(game.world, "update")
        game.handle_command(ord(" "))
        assert game.world.update.called

    def test_handle_command_r_calls_get_number_of_generations(self, game, mocker):
        mocker.patch.object(game, "get_number_of_generations")
        game.handle_command(ord("r"))
        assert game.get_number_of_generations.called

    def test_get_number_of_generations_calls_ask_user(self, game, mocker):
        mocker.patch.object(game, "ask_user")
        game.get_number_of_generations()
        assert game.ask_user.called

    def test_get_number_of_generations_with_invalid_input_returns_None(self, game, mocker):
        mocker.patch.object(game, "ask_user")
        game.ask_user.return_value = "tjosan"
        assert game.get_number_of_generations() is None


class TestScreenGame:

    def test_print_empty_game(self, empty_screen_game, capsys):
        empty_screen_game.print_world()
        out, _err = capsys.readouterr()
        assert out == "\n"

    def test_animate_empty_game_prints_empty_worlds(self, empty_screen_game, capsys):
        steps = 10
        empty_screen_game.animate(steps, timestep=0)
        out, _err = capsys.readouterr()
        assert out == steps * "\n"
