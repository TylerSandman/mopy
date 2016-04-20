from mopy.mctree import MCTree
from mopy.impl.nim.game import NimGame
from copy import deepcopy
import pytest


@pytest.fixture
def game(scope='module'):
    return NimGame()


@pytest.fixture
def root_left(game):
    s = game.new_game()
    r = MCTree(game, s)
    all_actions = game.get_legal_actions(s)
    mid = len(all_actions) // 2
    for a in all_actions[:mid]:
        new_s = deepcopy(s)
        game.do_action(new_s, a)
        r.children.append(MCTree(game, new_s, a))
    return r


@pytest.fixture
def root_right(game):
    s = game.new_game()
    r = MCTree(game, s)
    all_actions = game.get_legal_actions(s)
    mid = len(all_actions) // 2
    for a in all_actions[mid:]:
        new_s = deepcopy(s)
        game.do_action(new_s, a)
        r.children.append(MCTree(game, new_s, a))
    return r


@pytest.fixture
def root(game):
    s = game.new_game()
    r = MCTree(game, s)
    all_actions = game.get_legal_actions(s)
    for a in all_actions:
        new_s = deepcopy(s)
        game.do_action(new_s, a)
        r.children.append(MCTree(game, new_s, a))
    return r


def test_root_combine(root_left, root_right, root):
    root_left.combine_root_actions(root_right)
    expected_actions = set()
    combined_actions = set()
    for c in root.children:
        expected_actions.add(c.action)
    for c in root_left.children:
        combined_actions.add(c.action)
    assert len(expected_actions) == len(combined_actions)
    assert all(e in combined_actions for e in expected_actions)


def test_win_ratio_combine(root_left, root_right, root):
    left_copy = deepcopy(root_left)
    for c in left_copy.children:
        c.won_games += 1
        c.total_games += 1
    for c in root_right.children:
        c.won_games += 1
        c.total_games += 2
    root_left.combine_root_actions(left_copy)
    root_left.combine_root_actions(root_right)

    expected_actions = set()
    combined_actions = set()
    for c in root.children:
        expected_actions.add(c.action)
    for c in root_left.children:
        combined_actions.add(c.action)
    assert len(expected_actions) == len(combined_actions)
    assert all(e in combined_actions for e in expected_actions)

    mid = len(left_copy.children)
    for c in root_left.children[:mid]:
        assert int(c.win_ratio) == 1
    for c in root_left.children[mid:]:
        assert c.win_ratio == 0.5
