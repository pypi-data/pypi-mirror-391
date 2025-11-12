# rl-softmax-policy

Implements **Softmax (Boltzmann) Action Selection**, a probabilistic exploration strategy for Reinforcement Learning agents.

## Example Usage
```python
from rlsoftmaxpolicy_colab import softmax_action_selection

q_values = [1.0, 2.0, 3.0]
temperature = 0.8
action = softmax_action_selection(q_values, temperature)
print('Selected action:', action)
```

Author: Afi Prasla
