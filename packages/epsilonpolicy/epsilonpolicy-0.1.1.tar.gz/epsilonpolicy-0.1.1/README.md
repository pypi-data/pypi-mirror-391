# epsilonpolicy

A minimal epsilon-greedy action selection function.

## Install
```bash
pip install epsilonpolicy
from epsilonpolicy import epsilon_greedy

Q = {}
actions = ["left", "right", "up", "down"]
action = epsilon_greedy(Q, state="S", actions=actions, epsilon=0.2)
print(action)
