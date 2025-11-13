from epsgreedy import epsilon_greedy

def test_probs_sum_to_one():
    a, p = epsilon_greedy([1.0, 2.0, 3.0], epsilon=0.2)
    assert abs(sum(p) - 1.0) < 1e-9

def test_invalid_mask_excludes_actions():
    # action 1 invalid
    a, p = epsilon_greedy([1.0, 2.0, 3.0], epsilon=0.0, invalid=[False, True, False])
    assert p[1] == 0.0
    assert a in (0, 2)

def test_deterministic_greedy():
    a, p = epsilon_greedy([0.1, 0.9, 0.5], epsilon=0.0)
    assert a == 1
    assert max(p) == 1.0