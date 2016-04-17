from mopy.impl.nim.state import NimState
from mopy.impl.nim.action import NimAction
from mopy.impl.nim.game import NimGame
import pytest


@pytest.fixture
def game(scope="module"):
    return NimGame()


@pytest.fixture
def new_state(game):
    return game.new_game()


@pytest.fixture
def mid_state():
    return NimState([2, 0, 1], 0)


@pytest.fixture
def completed_state():
    return NimState([0, 0, 0], 0)


def test_legal_first_actions(game, new_state):
    all_actions = game.get_legal_actions(new_state)

    # Should be able to take 1-3 from heap 0,
    # 1-4 from heap 1, and 1-5 from heap 2
    for n in range(1, 4):
        assert NimAction(0, n) in all_actions
    for n in range(1, 5):
        assert NimAction(1, n) in all_actions
    for n in range(1, 6):
        assert NimAction(2, n) in all_actions


def test_legal_intermediate_actions(game, mid_state):
    all_actions = game.get_legal_actions(mid_state)

    # Should be able to take 1-2 from heap 0,
    # 0 from heap 1, 1 from heap 2
    assert NimAction(0, 1) in all_actions
    assert NimAction(0, 2) in all_actions
    assert NimAction(2, 1) in all_actions

    for n in range(3, 4):
        assert NimAction(0, n) not in all_actions
    for n in range(1, 5):
        assert NimAction(1, n) not in all_actions
    for n in range(2, 6):
        assert NimAction(2, n) not in all_actions


def test_action(game, new_state):
    game.do_action(new_state, NimAction(0, 3))

    assert new_state.current_player == 1
    assert new_state.heaps[0] == 0
    assert new_state.heaps[1] == 4
    assert new_state.heaps[2] == 5

    game.do_action(new_state, NimAction(1, 2))

    assert new_state.current_player == 0
    assert new_state.heaps[0] == 0
    assert new_state.heaps[1] == 2
    assert new_state.heaps[2] == 5


def test_game_over(game, new_state, mid_state, completed_state):

    assert game.is_over(completed_state)
    assert game.get_result(completed_state) == 1

    with pytest.raises(Exception):
        game.get_result(mid_state)
    with pytest.raises(Exception):
        game.get_result(new_state)
