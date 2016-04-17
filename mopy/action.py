"""Contains the abstract base class for general game actions."""

from abc import ABCMeta, abstractmethod


class Action(object):
    """
    Represents a general game action. All implementations
    of MCTS games should use concrete actions that subclass from Action. This
    base class is pretty bare to leave flexibility for game definitions.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass    # Need to define equality to compare action lists
