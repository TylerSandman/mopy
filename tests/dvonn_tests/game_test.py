from mopy.impl.dvonn.state import Cell
from mopy.impl.dvonn.action import DvonnAction
from mopy.impl.dvonn.game import DvonnGame
from copy import deepcopy
import pytest


@pytest.fixture
def game(scope="module"):
    return DvonnGame()


@pytest.fixture
def new_state(game):
    return game.new_game()


@pytest.fixture
def full_state(game, new_state):
    """Represents the state directly after white places his last ring."""
    full_state = deepcopy(new_state)
    grid = full_state.board.grid
    # Populate the board
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            cell.num_rings = 1
            cell.owner = Cell.Owner.WHITE if y % 2 == 0 else Cell.Owner.BLACK

    # Place the red rings
    for x, y in [(2, 0), (3, 5), (0, 9)]:
        grid[x][y].owner = Cell.Owner.RED
        grid[x][y].has_dvonn_ring = True

    for n in range(2):
        full_state.players[n].num_player_rings = 0
        full_state.players[n].num_dvonn_rings = 0

    grid[0][0].owner = Cell.Owner.NULL
    grid[0][1].owner = Cell.Owner.NULL
    grid[1][0].owner = Cell.Owner.NULL
    grid[3][10].owner = Cell.Owner.NULL
    grid[4][9].owner = Cell.Owner.NULL
    grid[4][10].owner = Cell.Owner.NULL
    full_state.legal_actions = game._calculate_legal_actions(full_state)
    return full_state


@pytest.fixture
def completed_state(game, new_state):
    """Represents an endgame state where neither player can move."""
    completed_state = deepcopy(new_state)

    for n in range(2):
        completed_state.players[n].num_dvonn_rings = 0
        completed_state.players[n].num_player_rings = 0

    grid = completed_state.board.grid
    grid[2][0].owner = Cell.Owner.BLACK
    grid[2][0].num_rings = 4
    grid[2][0].has_dvonn_ring = True

    grid[1][7].owner = Cell.Owner.BLACK
    grid[1][7].num_rings = 9
    grid[1][7].has_dvonn_ring = True

    grid[2][6].owner = Cell.Owner.WHITE
    grid[2][6].num_rings = 6
    grid[2][6].has_dvonn_ring = True

    grid[2][6].owner = Cell.Owner.WHITE
    grid[2][6].num_rings = 5
    grid[2][6].has_dvonn_ring = False
    actions = game._calculate_legal_actions(completed_state)
    completed_state.legal_actions = actions

    return completed_state


@pytest.mark.parametrize("positions", [
    ([(3, 5)]),
    ([(2, 0), (0, 3), (4, 5)]),
    ([(0, 2), (0, 10), (1, 1), (3, 0), (4, 0), (1, 10), (2, 10), (3, 9)])
])
def test_place_actions(game, new_state, positions):
    grid = new_state.board.grid

    for i, (x, y) in enumerate(positions):
        game.do_action(new_state, DvonnAction(DvonnAction.Type.PLACE, (x, y)))
        if i > 2:
            if i % 2 == 0:
                assert grid[x][y].owner == Cell.Owner.WHITE
            else:
                assert grid[x][y].owner == Cell.Owner.BLACK
        # Initial Dvonn ring placement phase
        else:
            assert grid[x][y].owner == Cell.Owner.RED
            assert grid[x][y].has_dvonn_ring
        assert grid[x][y].num_rings == 1

    num_placements = len(positions)
    num_player_placements = num_placements - 3
    p1, p2 = new_state.players[0], new_state.players[1]
    # Check if both players have the correct number of rings remaining.
    if num_player_placements > 0:
        assert p1.num_dvonn_rings == 0 and p2.num_dvonn_rings == 0
        assert p1.num_player_rings == (23 - num_player_placements // 2)
        assert p2.num_player_rings == (23 - (num_player_placements // 2 + 1))
    else:
        assert p1.num_player_rings == 23 and p2.num_player_rings == 23


@pytest.mark.parametrize("end, start", [
    ((0, 3), (0, 2)),
    ((1, 10), (2, 10)),
    (((3, 5)), (4, 4))
])
def test_move_actions(game, full_state, end, start):
    grid = full_state.board.grid
    (s_x, s_y), (e_x, e_y) = start, end
    game.do_action(full_state, DvonnAction(DvonnAction.Type.MOVE, end, start))
    assert grid[s_x][s_y].num_rings == 0
    assert grid[s_x][s_y].owner == Cell.Owner.EMPTY
    assert not grid[s_x][s_y].has_dvonn_ring
    assert grid[e_x][e_y].num_rings == 2
    assert grid[e_x][e_y].owner == Cell.Owner.WHITE


def test_legal_first_actions(game, new_state):
    all_actions = game.get_legal_actions(new_state)
    assert len(all_actions) == 49
    expected_actions = []
    grid = new_state.board.grid
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell.owner == cell.Owner.EMPTY:
                a = DvonnAction(DvonnAction.Type.PLACE, (x, y))
                expected_actions.append(a)
    assert all(a in expected_actions for a in all_actions)
    assert not any(a.type == DvonnAction.Type.MOVE for a in all_actions)


def test_legal_intermediate_actions(game, full_state):
    all_actions = game.get_legal_actions(full_state)
    full_state.current_player = (full_state.current_player + 1) % 2
    all_actions += game._calculate_legal_actions(full_state)
    assert not any(a.type == DvonnAction.Type.PLACE for a in all_actions)

    # Yes, I hand counted this.
    assert len(all_actions) == 83

    # These are all surrounded, so they shouldn't be a part of action space.
    for y in range(2, 10):
        blocked_a = DvonnAction(DvonnAction.Type.MOVE, (), start=(1, y))
        assert(blocked_a.start != a.start for a in all_actions)
    for y in range(1, 10):
        blocked_a = DvonnAction(DvonnAction.Type.MOVE, (), start=(2, y))
        assert(blocked_a.start != a.start for a in all_actions)
    for y in range(1, 9):
        blocked_a = DvonnAction(DvonnAction.Type.MOVE, (), start=(3, y))
        assert(blocked_a.start != a.start for a in all_actions)


def test_legal_completed_actions(game, completed_state):
    all_actions = game.get_legal_actions(completed_state)
    assert len(all_actions) == 0


def test_game_over(game, new_state, full_state, completed_state):
    assert game.is_over(completed_state)
    assert game.get_result(completed_state) == 1

    with pytest.raises(Exception):
        game.get_result(full_state)
    with pytest.raises(Exception):
        game.get_result(new_state)
