"""This module is responsible for node-level operations for MCTS."""

from copy import deepcopy
from random import choice
from operator import attrgetter
from collections import defaultdict


class MCTree(object):
    """
    A representation of a node in MCTS. This is usually only used by Mopy.

    Note that this class is easily extensible by subclassing and
    just defining a new __init__ and get_best_child. Everything
    else is abstracted to passed policies and the high level MCTS algorithm.
    """

    def __init__(self, game, state, action=None, parent=None):
        """
        Set up the node containing current game state information.

        Args:
            game (Game): The game we're performing MCTS on.
            state (State): The current state of `game`
            action (Optional[Action]): The action that was taken to get to
                `state`. Defaults to None (root node case).
            parent (Optional[MCTree]): Node representing the state from the
                previous turn. Defaults to None (root node case).

        Attributes:
            children (list[MCTree]): Nodes from taking actions in `state`.
            won_games [float]: How many simulated games won from `state`.
                Could be a non-whole number depending on chosen backup policy.
            total_games [float]: Number of simulated games done from `state`.
        """
        self.game = game
        self.state = state
        self.action = action
        self.parent = parent
        self.children = []
        self.won_games = 0
        self.total_games = 0

    @property
    def win_ratio(self):
        """float: Represents the w/l ratio of simulated games from self."""
        if self.total_games == 0:
            return 0
        return self.won_games / self.total_games

    def select(self, sel_policy):
        """
        Selection phase for MCTS. Uses appropriate policy.

        Args:
            sel_policy (function(MCTree) -> MCTree): The policy to be used
                to select the next node to be expanded. See Mopy for more
                information.

        Returns:
            MCTree chosen by following `sel_policy` from the current node.
        """
        root = self
        while not root.game.is_over(root.state):
            num_actions = len(root.game.get_legal_actions(root.state))
            num_explored = len(root.children)
            # If we haven't explored all possible actions, expand
            if num_explored < num_actions:
                return root._expand()
            # If we have, get the best action to rollout from
            else:
                root = sel_policy(root)
        return root

    def simulate_game(self, sim_policy):
        """
        Simulation phase for MCTS. Uses appropriate policy.

        Args:
            sim_policy (function(Game, State) -> Action): The policy to be
                used to choose actions during game simulations. See Mopy
                for more information.

        Returns:
            int representing the zero-indexed player number of the winner
            of the simulated game from the current node.
        """
        current_state = deepcopy(self.state)
        while not self.game.is_over(current_state):
            next_action = sim_policy(self.game, current_state)
            self.game.do_action(current_state, next_action)
        return self.game.get_result(current_state)

    def backup_result(self, result, backup_policy):
        """
        Backpropagation phase for MCTS. Uses appropriate policy.

        Args:
            result (int): Zero-indexed player number of the winner
                of the game at the current node.
            backup_policy (function(MCTree, Result)): The policy to be
                used to backpropagate the game simulation results up
                the tree. See Mopy for more information.
        """
        root = self
        while root:
            backup_policy(root, result)
            root = root.parent

    def get_best_action(self):
        """
        Selects best action to take from current root state.

        Returns:
            Action representing the best immediate action from
            current node.

        Notes:
            Most MCTS implementations select the action with the best
            win/loss ratio. If this isn't the behaviour you want, you
            can subclass MCTree and just reimplement get_best_action
            to your liking.
        """
        best_node = max(self.children, key=attrgetter("win_ratio"))
        return best_node.action

    def combine_root_actions(self, other):
        """
        Combines actions of direct children of self and other.

        Args:
            other (MCTree): The tree whose actions we're merging into
                our current tree.

        Notes:
            This only merges direct children of self and other, since when
            performing action selection that's all we care about. If an action
            isn't a child of our original tree, we add it. Otherwise, we add
            the win ratios together. This is mainly used at the last step
            of parallel search when we have to merge all simulation results.
        """
        won_count_map, total_count_map = defaultdict(int), defaultdict(int)
        original_actions = set()
        for c in self.children:
            won_count_map[c.action] += c.won_games
            total_count_map[c.action] += c.total_games
            original_actions.add(c.action)
        for c in other.children:
            if c.action not in original_actions:
                self.children.append(MCTree(self.game, self.state, c.action))
            won_count_map[c.action] += c.won_games
            total_count_map[c.action] += c.total_games
        for c in self.children:
            won, total = won_count_map[c.action], total_count_map[c.action]
            c.won_games, c.total_games = won, total

    def _expand(self):
        """Expansion phase for MCTS for nodes with unexplored actions."""
        all_actions = self.game.get_legal_actions(self.state)
        explored_actions = [c.action for c in self.children]
        new_actions = [a for a in all_actions if a not in explored_actions]

        next_action = choice(new_actions)
        next_state = deepcopy(self.state)
        self.game.do_action(next_state, next_action)

        new_node = MCTree(self.game, next_state, next_action, parent=self)
        self.children.append(new_node)
        return new_node
