from gae_returns import discounted_cumsum, n_step_target, gae

def test_discounted_cumsum_lengths():
    r = [1.0, 0.0, -1.0]
    out = discounted_cumsum(r, gamma=0.9)
    assert len(out) == len(r)

def test_n_step_target_matches_manual():
    r = [1.0, 0.5]
    g = n_step_target(r, gamma=0.9, bootstrap_value=0.2)
    # manual: 1.0 + 0.9*0.5 + 0.9^2*0.2
    manual = 1.0 + 0.9*0.5 + (0.9**2)*0.2
    assert abs(g - manual) < 1e-12

def test_gae_shapes():
    rewards = [1.0, 0.0, 0.5]
    values  = [0.2, 0.3, 0.4, 0.0]
    adv, ret = gae(rewards, values, gamma=0.99, lam=0.95)
    assert len(adv) == len(rewards)
    assert len(ret) == len(rewards)