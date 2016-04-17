"""Contains the abstract base class for a game."""

from abc import ABCMeta, abstractmethod


class Game(object):
    """
    Represents a general game to run MCTS on. All implementations of
    MCTS games should subclass from Game and define the appropriate methods.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def new_game(self):
        """
        Initialize a new game as if it were the first turn.

        Returns:
            State that represents the first turn of a new game.
        """
        pass

    @abstractmethod
    def get_legal_actions(self, state):
        """
        Collect all possible actions that can be taken from current state.

        Args:
            state (State): The current state of the game we're playing.

        Returns:
            list[Action] of all legal actions the current player can take.
        """
        pass

    @abstractmethod
    def do_action(self, state, action):
        """
        Execute an action and modify the current state accordingly.

        Args:
            state (State): The current state of the game we're playing.
                Modified by taking `action` instead of creating a new state.
            action (Action): The legal action from `state` to be executed.
        """
        pass

    @abstractmethod
    def is_over(self, state):
        """
        Determine if the current state represents the end of a game.

        Args:
            state (State): The current state of the game we're playing.

        Returns:
            True if no more actions can be taken and the game in `state`
            is complete. False otherwise.
        """
        pass

    @abstractmethod
    def get_result(self, state):
        """
        Get the result of a completed game.

        Args:
            state (State): The current state of the game we're playing.

        Returns:
            int which is a zero-indexed player number of the winner of the
            completed game at `state`.

        Notes:
            This should only be called with endgame states! You may get
            unexpected behaviour otherwise during MCTS.
        """
        pass
