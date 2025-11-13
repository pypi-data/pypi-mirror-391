# Epsilon-Greedy

A minimal, tested epsilon-greedy action selector for Reinforcement Learning.
Includes action masking and tie-aware probability allocation.

## Usage

```python
from epsgreedy import epsilon_greedy

action_values = [1.2, 0.5, 1.2, -0.3]   # Q(s, ·)
# Mask out invalid actions (e.g., action 1 is invalid here)
invalid = [False, True, False, False]

a, p = epsilon_greedy(action_values, epsilon=0.1, invalid=invalid)
print(a, p)  # chosen action index, probabilities over actions
```

## Install
```bash
pip install aditya-epsgreedy-20251112
```

## Testing
```bash
pip install pytest
pytest -q
```

## License
MIT