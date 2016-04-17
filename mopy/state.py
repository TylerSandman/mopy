"""Contains the abstract base class for general game states."""

from abc import ABCMeta, abstractmethod


class State(object):
    """
    Represents a general game state. All implementations
    of MCTS games should use concrete states that subclass from State.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, current_player=0):
        """
        Initialize a new state of a game.

        Args:
            current_player (Optional[int]): Zero-indexed integer representing
                the current player. Defaults to Player 1 (0).

        Notes:
            This base class is pretty bare to leave flexibility for game
            definitions. However, most MCTS implementations require you
            to keep track of the current player for backpropagation.
        """
        self.current_player = current_player
