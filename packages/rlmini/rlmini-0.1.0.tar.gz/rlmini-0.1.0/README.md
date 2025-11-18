# rlmini — tiny reinforcement learning utilities

A minimal, well-documented Python package that implements a small tabular Q-learning helper suitable for Gym environments.

## Features
- `q_learning()` function: run tabular Q-learning with an OpenAI Gym-compatible environment.
- Small, dependency-light package: `numpy` and `gymnasium`.

## Quick start

```bash
python -m pip install rlmini
python -c "from rlmini import q_learning; import gymnasium as gym; env=gym.make('FrozenLake-v1', is_slippery=False); q_learning(env, episodes=500)"
```

