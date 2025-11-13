from typing import Sequence, Optional, Tuple, List
import random

def epsilon_greedy(
    action_values: Sequence[float],
    epsilon: float = 0.1,
    rng: Optional[random.Random] = None,
    invalid: Optional[Sequence[bool]] = None,
) -> Tuple[int, List[float]]:
    """
    Choose an action using epsilon-greedy with optional action masking.

    Args:
        action_values: Sequence of action values (e.g., Q(s, ·)).
        epsilon: Exploration rate in [0, 1]. With prob. epsilon choose uniformly at random
                 among valid actions; otherwise choose a greedy action.
        rng: Optional random.Random instance for reproducibility.
        invalid: Optional mask of length len(action_values). True = invalid action.
                 Invalid actions receive probability 0 and are never chosen.

    Returns:
        (action_index, probabilities)
        action_index: int — chosen action (index into action_values)
        probabilities: list[float] — probability for each action (0.0 for invalid ones)

    Notes:
        - If multiple greedy actions tie for the max value, the (1-epsilon) mass is split evenly among them.
        - If all actions are masked invalid, raises ValueError.
    """
    if rng is None:
        rng = random.Random()

    n = len(action_values)
    if n == 0:
        raise ValueError("action_values must be non-empty")

    if invalid is None:
        invalid = [False] * n
    if len(invalid) != n:
        raise ValueError("invalid mask must have same length as action_values")

    valid_indices = [i for i, bad in enumerate(invalid) if not bad]
    if not valid_indices:
        raise ValueError("All actions are invalid; cannot select an action.")

    # Find greedy set (ties allowed) among valid actions
    max_val = max(action_values[i] for i in valid_indices)
    greedy_set = [i for i in valid_indices if action_values[i] == max_val]

    # Build probability vector
    probs = [0.0] * n
    m = len(valid_indices)
    if m == 0:
        raise ValueError("No valid actions available.")

    explore_share = epsilon / m  # uniform over valid actions
    for i in valid_indices:
        probs[i] = explore_share

    # Split exploit mass (1 - epsilon) evenly across greedy_set
    if greedy_set:
        exploit_share = (1.0 - epsilon) / len(greedy_set)
        for i in greedy_set:
            probs[i] += exploit_share

    # Sample according to probs
    r = rng.random()
    cum = 0.0
    chosen = valid_indices[-1]  # fallback
    for i, p in enumerate(probs):
        if p <= 0.0:
            continue
        cum += p
        if r <= cum:
            chosen = i
            break

    return chosen, probs