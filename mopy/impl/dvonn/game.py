"""
This module contains a concrete implementation of the game Dvonn.

See: http://www.gipf.com/dvonn/rules/rules.html
for more information about Dvonn and its ruleset.
"""

from mopy.game import Game
from mopy.impl.dvonn.state import DvonnState, Cell
from mopy.impl.dvonn.action import DvonnAction


class DvonnGame(Game):

    def __init__(self):
        pass

    def new_game(self):
        """Returns a DvonnState right before White's first move."""
        s = DvonnState()
        s.legal_actions = self._calculate_legal_actions(s)
        return s

    def do_action(self, state, action):
        """Place or move a ring or ring stack on the board."""
        if action.type == DvonnAction.Type.PLACE:
            self._do_place_action(state, action.end)
        elif action.type == DvonnAction.Type.MOVE:
            self._do_move_action(state, action.end, action.start)
        state.legal_actions = self._calculate_legal_actions(state)

    def is_over(self, state):
        """Returns True if and only if neither player has no legal actions."""
        return len(state.legal_actions) == 0

    def get_result(self, state):
        """The winner of Dvonn is whoever owns the most rings at the end."""
        done = self.is_over(state)
        if not done:
            raise Exception("Game is not done yet!")

        rings = self._get_total_rings(state)
        if rings[0] > rings[1]:
            return 0
        return 1

    def get_legal_actions(self, state):
        """
        Get legal actions for `state`.
        Since checking if a game is over requires checking if any legal
        actions are available, we offload the responsibility to the state
        and update it automatically after every action to improve efficiency.
        """
        return state.legal_actions

    def _calculate_legal_actions(self, state):
        """
        Get all legal actions in the current board state.
        Note that often one player will not be able to move, even
        though it is technically their turn. In this case, they must pass
        their turn on to the next player.
        """
        player = state.players[state.current_player]
        if player.num_player_rings > 0:
            return self._get_legal_place_actions(state)
        move_actions = self._get_legal_move_actions(state)
        # Current player passes
        if not move_actions:
            state.current_player = (state.current_player + 1) % 2
            return self._get_legal_move_actions(state)
        return move_actions

    def _get_legal_move_actions(self, state):
        """
        Get all legal move actions in the current board state.
        Note a move action is legal if and only if the current
        player owns the stack they wish to move, that stack
        is not fully surrounded by other rings, and the stack
        can only move on top of another stack of rings. Furthermore,
        a stack may ONLY move adjacent the distance equal to its size.
        """
        actions = []
        grid = state.board.grid
        for x, row in enumerate(grid):
            for y, cell in enumerate(row):
                if (cell.is_owned_by(state.current_player) and not
                        state.board.is_surrounded(cell)):
                    dist = cell.num_rings
                    neighbours = cell.grid_neighbour_positions(dist)
                    for n_x, n_y in neighbours:
                        if (state.board.is_on_board(n_x, n_y) and
                                grid[n_x][n_y].is_occupied()):
                            to, fr = (n_x, n_y), (x, y)
                            a = DvonnAction(DvonnAction.Type.MOVE, to, fr)
                            actions.append(a)
        return actions

    def _get_legal_place_actions(self, state):
        """
        Get all legal place actions in the current board state.
        Note a player can only place a ring on an empty cell.
        """
        actions = []
        grid = state.board.grid
        for x, row in enumerate(grid):
            for y, cell in enumerate(row):
                if cell.owner == Cell.Owner.EMPTY:
                    a = DvonnAction(DvonnAction.Type.PLACE, (x, y))
                    actions.append(a)
        return actions

    def _get_total_rings(self, state):
        white_rings = 0
        black_rings = 0
        grid = state.board.grid

        for row in grid:
            for cell in row:
                # White owns this
                if cell.owner == Cell.Owner.WHITE:
                    white_rings += cell.num_rings
                # Black owns this
                elif cell.owner == Cell.Owner.BLACK:
                    black_rings += cell.num_rings

        return (white_rings, black_rings)

    def _do_move_action(self, state, end, start):
        s_x, s_y = start
        e_x, e_y = end
        start_cell = state.board.grid[s_x][s_y]
        end_cell = state.board.grid[e_x][e_y]

        # The stack on the second cell grows
        end_cell.num_white_rings += start_cell.num_white_rings
        end_cell.num_black_rings += start_cell.num_black_rings
        end_cell.num_dvonn_rings += start_cell.num_dvonn_rings
        end_cell.owner = start_cell.owner

        # All rings move off the first cell
        start_cell.num_white_rings = 0
        start_cell.num_black_rings = 0
        start_cell.num_dvonn_rings = 0
        start_cell.owner = Cell.Owner.EMPTY

        # Check for components not connected to a red piece
        state.board.remove_isolated_rings()

        state.current_player = (state.current_player + 1) % 2

    def _do_place_action(self, state, pos):
        x, y = pos
        cell = state.board.grid[x][y]
        cell.num_white_rings = 1
        cell.owner = Cell.Owner.WHITE
        player = state.players[state.current_player]

        # Initial Dvonn ring placement phase
        if player.num_dvonn_rings > 0:
            cell.num_white_rings = 0
            player.num_dvonn_rings -= 1
            cell.owner = Cell.Owner.RED
            cell.num_dvonn_rings = 1
        else:
            player.num_player_rings -= 1
            if state.current_player == 1:
                cell.num_white_rings = 0
                cell.num_black_rings = 1
                cell.owner = Cell.Owner.BLACK

        next_player = state.players[(state.current_player + 1) % 2]
        # The player who started the first phase also starts the second phase.
        # Therefore, white moves immediately after he places his last ring.
        if player.num_player_rings > 0 or next_player.num_player_rings > 0:
            state.current_player = (state.current_player + 1) % 2
