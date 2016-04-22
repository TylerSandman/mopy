"""
Contains node selection policies for MCTS.

All policies should be represented as a function that takes a MCTree
and returns another MCTree. Selection policies determine how the tree
is traversed from a node during the selection phase in order to find a node
to simulate a game from. See the main Mopy module and MCTree for more details
on how policies are incorporated.
"""

from math import log, sqrt
from random import random, choice
from operator import attrgetter


def _get_UCT_val(node, explore_rate):
    val = node.win_ratio
    C = explore_rate
    par_visits = node.parent.total_games
    node_visits = node.total_games
    return (val + 2*C*sqrt((2*log(par_visits)) / node_visits))


def UCT(node, explore_rate=0.2):
    """
    Policy to select children nodes based on UCT criteria.

    Args:
        node (MCTree): The current node during selection phase of MCTS.
        explore_rate (Optional[float]): Constant representing the exploration
            rate for UCT. Higher values bias node selection toward exploration
            while lower values bias node selection toward exploitation.
            Defaults to 0.2, an empirically confirmed good starting value.

    Returns:
        MCTree representing the child of `node` selected by UCT criteria.

    Notes:
        See: https://en.wikipedia.org/wiki/Monte_Carlo_tree_search for more
        information on UCT (yes I just linked to Wikipedia).
        For a more in-depth explanation, see Browne et al(2012):
        http://www.cameronius.com/cv/mcts-survey-master.pdf.
    """
    scores = [_get_UCT_val(c, explore_rate) for c in node.children]
    selected_i = scores.index(max(scores))
    return node.children[selected_i]


def epsilon_greedy(node, explore_rate=0.2, exploit_rate=0.2):
    """
    Policy to select children nodes based on greedy epsilon criteria.

    Args:
        node (MCTree): The current node during selection phase of MCTS.
        explore_rate (Optional[float]): Constant representing the exploration
            rate for greedy epsilon. Higher values will tend to choose random
            nodes more often.
        exploit_rate (Optional[float]): Constant representing the exploitation
            rate for greedy epsilon. LOWER values will tend to bias the
            selection toward exploiting the best nodes more often.

    Returns:
        MCTree representing the child of `node` selected by greedy epsilon.

    Notes:
        See Theorem 3 contained in:
        http://homes.di.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf
        for more information regarding the greedy epsilon policy.
    """
    node_visits = node.total_games
    num_actions = len(node.children)
    eps = min(1, (explore_rate*num_actions) / ((exploit_rate**2)*node_visits))

    best_node = max(node.children, key=attrgetter("win_ratio"))
    if random() < eps:
        return choice(node.children)
    return best_node
