"""
This module contains a representation of a state of the game Dvonn.

To internally represent Dvonn's unconventional hexagonal grid, axial
coordinates were used. More specifically, we treat a hexagonal grid
to have 3 axes. Moving E and W consitutes movement along the x-axis.
Moving N or S constitutes movement along the z-axis. Finally, in axial
coordinates, the y-coordinate can be implicitly calculated as y = -x - z
since all 3 coordinates sum to zero by definition.

The top-left most hexagonal tile is the axial coordinate (0, 0). Full setup:

     (0, 0)(1,0)(2,0)(3,0)(4,0)(5,0)(6,0)(7,0)(8,0)
   (-1,1)(0,1)(1,1)(2,1)(3,1)(4,1)(5,1)(6,1)(7,1)(8,1)
(-2,2)(-1,2)(0,2)(1,2)(2,2)(3,2)(4,2)(5,2)(6,2)(7,2)(8,2)
   (-2,3)(-1,3)(0,3)(1,3)(2,3)(3,3)(4,3)(5,3)(6,3)(7,3)
     (-2,4)(-1,4)(0,4)(1,4)(2,4)(3,4)(4,4)(5,4)(6,4)

We simply convert axial coordinates to traditional grid coordinates and store
the board in a 2D array. However, we need to pad elements at the beginning
and end of rows with Null-like values so they're not a part of the game.

See: http://www.redblobgames.com/grids/hexagons/
"""

from mopy.state import State
from enum import Enum


class Cell(object):
    """Represents a single tile on the Dvonn hexagonal grid."""

    class Owner(Enum):
        WHITE = 1
        BLACK = 2
        RED = 3
        EMPTY = 4
        NULL = 5

    def __init__(self, r, c):
        """
        Setup a cell in its initial state at the beginning of the game.

        Attributes:
            r (int): The x-coordinate of a cell in axial form.
                We store cell coords this way to calculate movement easier.
            c (int): Represents the z-coordinate of a cell in axial form.
            num_rings (int): How many rings occupy this cell.
            owner (Owner): The entity that has control over this cell.
                In Dvonn, the colour of the ring on top of the stack represents
                the owner. Null owners consitute cells not in-game.
            has_dvonn_ring (bool): Whether a red ring is on this cell. Used to
                check for connectedness during ring removal phase.
        """
        self.r = r
        self.c = c
        self.num_white_rings = 0
        self.num_black_rings = 0
        self.num_dvonn_rings = 0
        self.owner = Cell.Owner.EMPTY

    @property
    def num_rings(self):
        player_rings = self.num_white_rings + self.num_black_rings
        special_rings = self.num_dvonn_rings
        return player_rings + special_rings

    @property
    def has_dvonn_ring(self):
        return self.num_dvonn_rings > 0

    def __repr__(self):
        return str((self.r, self.c))

    def __eq__(self, other):
        return (self.r == other.r and self.c == other.c)

    def is_owned_by(self, player_num):
        """Returns True if and only if this cell is owned by `player_num`."""
        if player_num == 0:
            return self.owner == Cell.Owner.WHITE
        elif player_num == 1:
            return self.owner == Cell.Owner.BLACK

    def is_occupied(self):
        """Returns True if and only if at least one ring is on this cell."""
        return (self.owner == Cell.Owner.WHITE or
                self.owner == Cell.Owner.BLACK or
                self.owner == Cell.Owner.RED)

    def grid_neighbour_positions(self, dist=1):
        """
        Returns all neighbours in each of 6 adjacent directions in grid form.

        Args:
            dist (int): How far away each neighbour is from this cell.
                Defaults to 1 (immediate neighbours)

        Returns:
            List[(x, y)] representing all neighbouring positions in grid form.

        Example:
            Cell(-1, 3).grid_neighbour_positions(dist=2) ->
            [(1, 1), (1, 3), (3, 3), (5, 1), (5, -1), (3, -1)]
        """
        deltas = [(0, -1), (1, -1), (1, 0), (-1, 0), (0, 1), (-1, 1)]
        ax_pos = [(self.r + dist*d[0], self.c + dist*d[1]) for d in deltas]
        return [Cell.axial_to_grid(*n) for n in ax_pos]

    @staticmethod
    def grid_to_axial(x, y):
        """Convert x, y coordinates into axial (x, z) coordinates."""
        return (y - 2, x)

    @staticmethod
    def axial_to_grid(r, c):
        """Convert r, c coordinates into grid (x, y) coordinates."""
        return (c, r + 2)


class Board(object):
    """Represents the hexagonal grid of a Dvonn game."""

    def __init__(self):
        """Set up an empty board, nullifying spaces out of play."""
        self.grid = []
        for x in range(5):
            row = []
            for y in range(11):
                r, c = Cell.grid_to_axial(x, y)
                row.append(Cell(r, c))
            self.grid.append(row)

        # We're "padding" the cells that are out of range of the hexagonal
        # representation of the grid.
        self.grid[0][0].owner = Cell.Owner.NULL
        self.grid[0][1].owner = Cell.Owner.NULL
        self.grid[1][0].owner = Cell.Owner.NULL
        self.grid[3][10].owner = Cell.Owner.NULL
        self.grid[4][9].owner = Cell.Owner.NULL
        self.grid[4][10].owner = Cell.Owner.NULL

        self.removed_white_rings = 0
        self.removed_black_rings = 0

    def is_on_board(self, x, y):
        """Returns True if and only if (x, y) is a valid grid board pos."""
        num_rows = len(self.grid)
        num_cols = len(self.grid[0])
        return 0 <= x < num_rows and 0 <= y < num_cols

    def remove_isolated_rings(self):
        """
        Remove all isolated player rings on the board.

        Note that pieces and stacks must remain in contact, directly
        or indirectly, with at least one Dvonn ring to remain in play.
        That is, there must be a path of rings from a player ring to a
        Dvonn ring, or else it is removed from play. A Dvonn ring is always
        in contact with itself, so they are never removed.

        This algorithm uses DFS to find all connected ring components, and
        removes components which are considered "isolated" from a Dvonn ring.

        Could be improved in the future by implementing a dynamic connected
        components algorithm.
        """
        visited = [[False for cell in row] for row in self.grid]
        for x, row in enumerate(self.grid):
            for y, cell in enumerate(row):
                if cell.is_occupied() and not visited[x][y]:
                    if self._is_isolated_component(x, y, visited):
                        self._remove_component(x, y)

    def is_surrounded(self, cell):
        """
        Returns True if and only if `cell` is fully surrounded.

        A cell is considered surrounded if all of its immediate neighbours
        are other rings of any colour. Hence, edge rings are never surrounded.
        """
        neighbours = cell.grid_neighbour_positions()

        for n_x, n_y in neighbours:
            # We're on an edge
            if not self.is_on_board(n_x, n_y):
                return False
            neighbour = self.grid[n_x][n_y]
            if not neighbour.is_occupied():
                return False
        return True

    def _is_isolated_component(self, x, y, visited):
        visited[x][y] = True
        cell = self.grid[x][y]
        neighbours = cell.grid_neighbour_positions()
        is_isolated = (not cell.has_dvonn_ring)

        for n_x, n_y in neighbours:
            if self.is_on_board(n_x, n_y) and not visited[n_x][n_y]:
                neighbour = self.grid[n_x][n_y]
                if neighbour.is_occupied():
                    if not self._is_isolated_component(n_x, n_y, visited):
                        is_isolated = False
        return is_isolated

    def _remove_component(self, x, y):
        cell = self.grid[x][y]
        self.removed_white_rings += cell.num_white_rings
        self.removed_black_rings += cell.num_black_rings
        cell.owner = Cell.Owner.EMPTY
        cell.num_white_rings = 0
        cell.num_black_rings = 0
        cell.num_dvonn_rings = 0
        neighbours = cell.grid_neighbour_positions()

        for n_x, n_y in neighbours:
            if self.is_on_board(n_x, n_y):
                neighbour = self.grid[n_x][n_y]
                if neighbour.is_occupied():
                    self._remove_component(n_x, n_y)


class Player(object):
    """Wrapper class to store information specific to each player."""

    def __init__(self, player_num):
        # Each player starts with 23 rings of their colour.
        self.num_player_rings = 23
        # White starts with 2 Dvonn rings, and Black 1.
        self.num_dvonn_rings = 2
        if player_num == 1:
            self.num_dvonn_rings = 1


class DvonnState(State):
    """Represents the full state of a Dvonn game at any time."""

    def __init__(self, current_player=0):
        super().__init__(current_player)
        self.legal_actions = []
        self.board = Board()
        self.players = [Player(0), Player(1)]
