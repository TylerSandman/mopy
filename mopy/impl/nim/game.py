"""This module contains a concrete implementation of the game Nim."""

from random import choice
from mopy.game import Game
from mopy.impl.nim.state import NimState
from mopy.impl.nim.action import NimAction


class NimGame(Game):

    def __init__(self):
        pass

    def new_game(self):
        """
        Initialize a new game with 3 heaps with 3, 4, and 5 elements.

        Initial state looks like the following:


        Player 1's move

                x
            x   x
        x   x   x
        x   x   x
        x   x   x
        ----------
        H1  H2  H3
        """
        heaps = [3, 4, 5]
        current_player = 0
        return NimState(heaps, current_player)

    def do_action(self, state, action):
        """Take a non-zero number of elements from a heap."""
        state.heaps[action.heap_num] -= action.num_taken
        state.current_player = 1 if state.current_player == 0 else 0

    def is_over(self, state):
        """Game is only over when all heaps are empty."""
        return sum(state.heaps) == 0

    def get_result(self, state):
        """
        If the game is over, the winner is the previous player.
        This is because after we execute the final action, we still
        advance the current player. Make sure to only call this when
        the game is actually complete!
        """
        done = self.is_over(state)
        if not done:
            raise Exception("Game is not done yet!")
        return 1 if state.current_player == 0 else 0

    def get_random_action(self, state):
        """Take a random number of elements from a random heap."""
        return choice(self.get_legal_actions(state))

    def get_legal_actions(self, state):
        """
        Return all possible take actions the current player can take.
        Note that you can take any number of elements from any heap
        from 1 to the number of elements on that heap.
        """
        actions = []
        heaps = state.heaps

        for i, h in enumerate(heaps):
            for n in range(1, h + 1):
                actions.append(NimAction(i, n))
        return actions
