# GAE & Returns

Tiny, dependency-free utilities to compute:
- Discounted cumulative returns
- n-step TD target
- Generalized Advantage Estimation (GAE)

## Usage
```python
from gae_returns import discounted_cumsum, n_step_target, gae

r = [1.0, 0.0, -1.0]
print(discounted_cumsum(r, gamma=0.9))  # -> [1.0 + 0.9*0 + 0.9^2*(-1), ...]

# n-step target for step t with bootstrap V_{t+n}
print(n_step_target(rewards=[1.0, 0.5], gamma=0.99, bootstrap_value=0.2))

# GAE given rewards and state values
rewards = [1.0, 0.0, 0.5]
values  = [0.2, 0.3, 0.4, 0.0]  # note extra terminal value V_T
adv, ret = gae(rewards, values, gamma=0.99, lam=0.95)
```

## Install
```bash
pip install sannidhi-gae-returns-20251112
```

## Testing
```bash
pip install pytest
pytest -q
```

## License
MIT