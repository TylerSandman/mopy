"""
This is the main Monte Carlo Tree Search module.

Mopy is responsible for running the main MCTS (Monte Carlo Tree Search)
algorithm on a given game, with the appropriate policies for selection,
simulation, and result backpropagation.

See Browne et al(2012) for an in-depth overview of MCTS methods:
http://www.cameronius.com/cv/mcts-survey-master.pdf
"""

from mctree import MCTree
from policies import backup, selection, simulation


class Mopy(object):
    """The main class for executing the MCTS algorithm"""

    def __init__(
            self, *,
            sel_policy=selection.UCT,
            sim_policy=simulation.random_action,
            backup_policy=backup.win_loss_ratio):
        """
        Initialize the algorithm with appropriate policies.

        Args:
            sel_policy (Optional[function(MCTree) -> MCTree]):
                The policy to be used to select the next node to be expanded.
                Defaults to the traditional UCT policy.
            sim_policy (Optional[function(Game, State) -> Action]):
                The policy to be used to choose actions during
                game simulations from the selected node.
                Defaults to choosing actions uniformly at random.
            backup_policy (Optional[function(MCTree, Result)]):
                The policy to be used to backpropagate game simulation
                results up the tree. Defaults to updating
                the win/loss ratio of nodes.
        """
        self.sel_policy = sel_policy
        self.sim_policy = sim_policy
        self.backup_policy = backup_policy

    def search(self, game, state, num_sims=1000):
        """
        Search for the best action of `game` from `state`.

        Args:
            game (Game): The game implementation to be used for MCTS.

            state (State): The current state of `game`.

            num_sims (Optional[int]): The number of simulations to run in
            `state` before returning the current best action. Default to 1000.

        Returns:
            Action that represents the action with the maximum reward
            from `state`

        Notes:
            `game` and `state` must be full implementations of the Game and
            State abstract base classes.
        """
        root = MCTree(game, state)
        for n in range(num_sims):
            selected_node = root.select(self.sel_policy)
            result = selected_node.simulate_game(self.sim_policy)
            selected_node.backup_result(result, self.backup_policy)

        return root.get_best_action()
