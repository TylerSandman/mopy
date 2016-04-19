"""This module contains a representation of an action in the game Dvonn."""

from mopy.action import Action
from enum import Enum


class DvonnAction(Action):

    class Type(Enum):
        PLACE = 1
        MOVE = 2

    def __init__(self, type_, end, start=None):
        """
        Create an action representing placing or moving a ring.

        Args:
            type_ (Type): Which action to take.
            end (Tuple(int, int)): The final grid position of the ring or
                ring stack to be placed or moved.
            start (Tuple(int, int)): The grid position of the ring to be
                moved during this action. Only to be used during MOVE actions.
                Defaults to None.
        """
        self.type = type_
        self.end = end
        self.start = start

    def __eq__(self, other):
        eq_type = self.type == other.type
        eq_end = self.end == other.end
        eq_start = self.start == other.start
        return (eq_type and eq_end and eq_start)

    def __repr__(self):
        if self.type == DvonnAction.Type.PLACE:
            return self.type.name + " at " + str(self.end)
        return self.type.name + " " + str(self.start) + " to " + str(self.end)
