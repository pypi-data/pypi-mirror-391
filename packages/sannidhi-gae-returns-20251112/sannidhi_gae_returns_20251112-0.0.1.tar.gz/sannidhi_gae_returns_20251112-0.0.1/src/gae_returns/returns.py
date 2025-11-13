from typing import Sequence, Tuple, List

def discounted_cumsum(rewards: Sequence[float], gamma: float) -> List[float]:
    """
    Compute discounted cumulative returns G_t = sum_{k=0}^{T-t-1} gamma^k r_{t+k}

    Args:
        rewards: sequence of rewards r_0 ... r_{T-1}
        gamma: discount factor in [0, 1]

    Returns:
        list of same length as rewards with discounted returns starting at each t.
    """
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be in [0, 1]")
    T = len(rewards)
    out = [0.0] * T
    g = 0.0
    for t in reversed(range(T)):
        g = rewards[t] + gamma * g
        out[t] = g
    return out

def n_step_target(rewards: Sequence[float], gamma: float, bootstrap_value: float = 0.0) -> float:
    """
    Compute an n-step TD target given a finite sequence of rewards and an optional bootstrap value.

    For rewards r_0..r_{n-1}, target is:
        r_0 + gamma r_1 + ... + gamma^{n-1} r_{n-1} + gamma^n * bootstrap_value

    Args:
        rewards: sequence r_0..r_{n-1}
        gamma: discount factor in [0, 1]
        bootstrap_value: V_{t+n} to bootstrap from (default 0.0)

    Returns:
        scalar float target
    """
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be in [0, 1]")
    g = bootstrap_value
    for r in reversed(rewards):
        g = r + gamma * g
    return g

def gae(rewards: Sequence[float], values: Sequence[float], gamma: float, lam: float) -> Tuple[List[float], List[float]]:
    """
    Generalized Advantage Estimation (GAE).
    See: Schulman et al., 2015 (arXiv:1506.02438)

    Args:
        rewards: length T
        values: length T+1 (includes terminal V_T)
        gamma: discount factor in [0, 1]
        lam: lambda parameter in [0, 1]

    Returns:
        (advantages, returns) where
          advantages: length T
          returns: length T, with R_t = advantages[t] + values[t]
    """
    if len(values) != len(rewards) + 1:
        raise ValueError("values must have length len(rewards) + 1")
    if not (0.0 <= gamma <= 1.0 and 0.0 <= lam <= 1.0):
        raise ValueError("gamma and lam must be in [0, 1]")

    T = len(rewards)
    adv = [0.0] * T
    gae_accum = 0.0
    for t in reversed(range(T)):
        delta = rewards[t] + gamma * values[t + 1] - values[t]
        gae_accum = delta + gamma * lam * gae_accum
        adv[t] = gae_accum
    ret = [adv[t] + values[t] for t in range(T)]
    return adv, ret