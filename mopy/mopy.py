"""
This is the main Monte Carlo Tree Search module.

Mopy is responsible for running the main MCTS (Monte Carlo Tree Search)
algorithm on a given game, with the appropriate policies for selection,
simulation, and result backpropagation.

See Browne et al(2012) for an in-depth overview of MCTS methods:
http://www.cameronius.com/cv/mcts-survey-master.pdf
"""

from multiprocessing import Process, Manager
from mopy.mctree import MCTree
from mopy.policies import backup, selection, simulation
from time import clock


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

    def search(self, game, state, search_time=0.5):
        """
        Search for the best action of `game` from `state`.

        Args:
            game (Game): The game implementation to be used for MCTS.

            state (State): The current state of `game`.

            num_sims (Optional[float]): How long to run the MCTS for in
                seconds. Defaults to half a second (0.5).

        Returns:
            Action that represents the action with the maximum reward
            from `state`

        Notes:
            `game` and `state` must be full implementations of the Game and
            State abstract base classes.
        """
        root = MCTree(game, state)
        start_time = clock()
        while (clock() - start_time) < search_time:
            selected_node = root.select(self.sel_policy)
            result = selected_node.simulate_game(self.sim_policy)
            selected_node.backup_result(result, self.backup_policy)

        return root.get_best_action()

    def parallel_search(self, game, state, search_time=0.5, num_workers=4):
        """
        Searches for the best action of `game` from `state` in parallel.

        We split up MCTS evenly amonst `num_workers` processes. Each worker
        runs an equal fraction of `num_sims`. Once every worker has ran their
        MCTS individually, all the distinct tree roots are combined into
        a final tree which we then choose the best action from. Note that
        `search_time` is total seconds for the search, not the search time
        per worker.

        Based off root parallelization found in Chaslot et al:
        dke.maastrichtuniversity.nl/m.winands/documents/multithreadedMCTS2.pdf

        Best results are usually found when `num_workers` is equal to the
        number of CPU cores available. That is, if you are using 4 cores,
        8 workers will show little to no improvement from 4 workers.
        """
        manager = Manager()
        root_list = manager.list()
        procs = []
        worker_search_time = search_time / num_workers
        for _ in range(num_workers):
            p = Process(target=self._search_job,
                        args=(root_list, game, state, worker_search_time,))
            procs.append(p)
            p.start()
        for p in procs:
            p.join()

        first_root = root_list[0]
        for i in range(1, len(root_list)):
            first_root.combine_root_actions(root_list[i])
        return first_root.get_best_action()

    def _search_job(self, root_list, game, state, search_time):
        root = MCTree(game, state)
        start_time = clock()
        while (clock() - start_time) < search_time:
            selected_node = root.select(self.sel_policy)
            result = selected_node.simulate_game(self.sim_policy)
            selected_node.backup_result(result, self.backup_policy)
        root_list.append(root)
