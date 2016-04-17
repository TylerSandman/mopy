"""This module contains a representation of an action in the game Nim."""

from mopy.action import Action


class NimAction(Action):

    def __init__(self, heap_num, num_taken):
        """
        Create an action representing taking some elements from a heap.

        Args:
            heap_num (int): Zero-indexed integer representing the index
                of the heap from which to take elements off of.
            num_taken (int): How many elements we take off heap `heap_num`.
                Must be between 1 and the size of heap `heap_num`.
        """
        self.heap_num = heap_num
        self.num_taken = num_taken

    def __eq__(self, other):
        eq_i = self.heap_num == other.heap_num
        eq_num = self.num_taken == other.num_taken
        return eq_i and eq_num

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def __repr__(self):
        h_i = self.heap_num
        n = self.num_taken
        return "Taking " + str(n) + " from heap " + str(h_i)
