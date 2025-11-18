
# jayditya-rl-update

A tiny Python package with a single Reinforcement Learning helper function:
`q_learning_update`, which performs a one-step Q-learning update.

## Quick Start

\\`\\`\\`python
from jayditya_rl_update import q_learning_update

q_new = q_learning_update(
    q_value=0.5,
    reward=1.0,
    next_max_q=0.8,
    alpha=0.1,
    gamma=0.99,
)
print(q_new)
\\`\\`\\`

## Installation

\\`\\`\\`
pip install jayditya-rl-update
\\`\\`\\`

