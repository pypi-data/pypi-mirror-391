
"""RL utilities: Q-learning update function."""

from typing import Union

Number = Union[float, int]

def q_learning_update(
    q_value: Number,
    reward: Number,
    next_max_q: Number,
    alpha: float = 0.1,
    gamma: float = 0.99,
) -> float:
    """One-step Q-learning update.

    Args:
        q_value: Current Q(s,a).
        reward: Reward received after taking action.
        next_max_q: max_a' Q(s', a').
        alpha: Learning rate.
        gamma: Discount factor.

    Returns:
        Updated Q value.
    """

    td_target = reward + gamma * next_max_q
    td_error = td_target - float(q_value)
    return float(q_value) + alpha * td_error
