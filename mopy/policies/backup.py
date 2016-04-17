"""
Contains result backpropagation policies for MCTS.

All policies should be represented as a function that takes a MCTree and
the result of a game, and updates a node accordingly. Backup policies dictate
how the results of simulated games affect game states beforehand. See the main
Mopy module and MCTree for more details on how policies are incorporated.
"""


def win_loss_ratio(node, winner):
    """
    Policy to update a node's win/loss ratio after a simulation result.

    Args:
        node (MCTree): The current node during backpropagation phase of MCTS.
        winner (int): Zero-indexed integer representing winner of a simulated
            game which is currently being backpropagated up the tree.
    """
    node.total_games += 1
    if node.state.current_player == winner:
        node.won_games += 1
