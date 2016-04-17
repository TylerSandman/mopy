"""
Contains simulation policies for MCTS.

All policies should be represented as a function that takes a Game and State
and returns an Action. Simulation policies determine which actions are taken
during game simulation phases of MCTS. See the main Mopy module and MCTree
for more details on how policies are incorporated.
"""

from random import choice


def random_action(game, state):
    """
    Policy to choose an action from `state` randomly. Default MCTS policy.

    Args:
        game (Game): The game that can operate on actions and states.
        state (State): The current state of a `game` instance.

    Returns:
        Action representing a legal action that can be taken from `state`.
        Chosen uniformly at random.
    """
    all_actions = game.get_legal_actions(state)
    return choice(all_actions)
