# rl-epsilon-decay

A lightweight package that implements an **epsilon decay** function — commonly used in Reinforcement Learning to gradually reduce exploration.

## Example Usage
```python
from rlepsilondecay_colab import epsilon_decay

eps = epsilon_decay(initial_epsilon=1.0, min_epsilon=0.01, decay_rate=0.95, step=10)
print('Decayed epsilon:', eps)
```

Author: SAAHIL DESAI
