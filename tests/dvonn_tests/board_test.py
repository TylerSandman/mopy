from mopy.impl.dvonn.state import Cell
from mopy.impl.dvonn.game import DvonnGame
import pytest


@pytest.fixture
def game(scope="module"):
    return DvonnGame()


@pytest.fixture
def new_state(game):
    return game.new_game()


@pytest.fixture
def full_state(new_state):
    full_state = new_state
    grid = full_state.board.grid
    # Populate the board
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            cell.owner = Cell.Owner.WHITE if y % 2 == 0 else Cell.Owner.BLACK
            if cell.is_owned_by(y % 2):
                cell.num_white_rings = 1
            else:
                cell.num_black_rings = 1

    # Place the red rings
    for x, y in [(2, 0), (3, 5), (0, 9)]:
        grid[x][y].owner = Cell.Owner.RED
        grid[x][y].num_dvonn_rings = 1

    for n in range(2):
        full_state.players[n].num_player_rings = 0
        full_state.players[n].num_dvonn_rings = 0

    return full_state


@pytest.mark.parametrize("test_cell, test_dist, expected", [
    (Cell(0, 0), 1, [(0, 3), (1, 2), (1, 1), (0, 1), (-1, 2), (-1, 3)]),
    (Cell(2, 2), 1, [(1, 4), (1, 5), (2, 5), (3, 4), (3, 3), (2, 3)]),
    (Cell(-1, 3), 2, [(1, 1), (1, 3), (3, 3), (5, 1), (5, -1), (3, -1)]),
    (Cell(8, 0), 3, [(-3, 10), (-3, 13), (0, 13), (3, 10), (3, 7), (0, 7)])
])
def test_grid_neighbour_positions(test_cell, test_dist, expected):
    neighbours = test_cell.grid_neighbour_positions(test_dist)
    assert all(e in neighbours for e in expected)


def test_ring_removal(full_state):

    board = full_state.board
    # Remove rings to isolate lower right corner
    for x, y in [(0, 10), (1, 9), (2, 8), (3, 7), (4, 6)]:
        visited = [[False for cell in row] for row in board.grid]
        assert not board._is_isolated_component(x, y, visited)
        cell = board.grid[x][y]
        cell.num_white_rings = 0
        cell.num_black_rings = 0
        cell.owner = Cell.Owner.EMPTY
        cell.num_dvonn_rings = 0

    # Remove the newly isolated group of rings
    visited = [[False for cell in row] for row in board.grid]
    assert(board._is_isolated_component(2, 9, visited))
    board.remove_isolated_rings()
    for x, y in [(1, 10), (2, 9), (3, 8), (4, 7), (2, 10), (3, 9), (4, 8)]:
        cell = board.grid[x][y]
        assert cell.owner == Cell.Owner.EMPTY
        assert cell.num_white_rings == 0
        assert cell.num_black_rings == 0
        assert cell.num_dvonn_rings == 0


@pytest.mark.parametrize("test_cell, expected", [
    (Cell(0, 0), False),
    (Cell(0, 1), True),
    (Cell(-2, 2), False),
    (Cell(2, 4), False),
    (Cell(4, 3), True),
    (Cell(8, 0), False),
    (Cell(2, 2), True),
    (Cell(8, 2), False),
    (Cell(2, 3), True)
])
def test_surround(full_state, test_cell, expected):
    assert full_state.board.is_surrounded(test_cell) == expected
