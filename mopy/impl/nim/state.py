"""This module contains a representation of a state of the game Nim"""

from mopy.state import State


class NimState(State):

    def __init__(self, heaps, current_player):
        """
        Create a state based on the current player and remaining heaps.

        Args:
            heaps (list[int]): Represents the remaining heaps in Nim. Each
                element represents an individual heap, while the value
                of each element represents how many elements are left
                in that individual heap.
            current_player (int): Zero-indexed integer representing whose
                turn it currently is.

        Example:
            The state NimState([1,2,3], 0) corresponds to:

            Player 1's move

                    x
                x   x
            x   x   x
            ----------
            H1  H2  H3
        """
        super().__init__(current_player)
        self.heaps = heaps

    def __repr__(self):
        heaps = str(self.heaps)
        player = str(self.current_player)
        return heaps + " P" + player
