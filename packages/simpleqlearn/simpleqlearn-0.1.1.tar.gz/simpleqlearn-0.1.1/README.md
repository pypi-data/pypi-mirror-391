# simpleqlearn

A minimal, well-documented **Q-learning table update** function.

## Install
```bash
pip install simpleqlearn
from simpleqlearn import q_update

Q = {}
Q = q_update(Q, state="s1", action="a1", reward=1.0, next_state="s2")
print(Q)  # {'s1': {'a1': 0.1}} for default alpha=0.1, gamma=0.99
