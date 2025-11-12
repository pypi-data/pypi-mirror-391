# rl-discounted-return

A lightweight package to compute **discounted cumulative returns** — a key concept in Reinforcement Learning (RL).

## Example Usage
```python
from rldiscountedreturn_colab import discounted_return
rewards = [1, 1, 1, 1, 1]
gamma = 0.9
print(discounted_return(rewards, gamma))  # Output: 4.095
```

Author: Jinal Chhajer
