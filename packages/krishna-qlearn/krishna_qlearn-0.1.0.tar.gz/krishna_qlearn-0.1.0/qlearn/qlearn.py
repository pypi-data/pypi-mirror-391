"""
Tiny tabular Q-learning implementation.

Designed to be simple and easy to understand for assignment use.
Works with discrete-state, discrete-action Gym-like environments.
"""

from typing import Dict, Tuple, Optional
import numpy as np
import random


def qlearn_step(
    Q: Dict[int, Dict[int, float]],
    state: int,
    action: int,
    reward: float,
    next_state: int,
    alpha: float = 0.1,
    gamma: float = 0.99,
) -> float:
    """
    Perform one tabular Q-learning update.

    Parameters
    ----------
    Q : dict
        Q table mapping state -> action -> value.
    state : int
        Current state index.
    action : int
        Action taken at current state.
    reward : float
        Reward received after taking action.
    next_state : int
        Next state index after taking action.
    alpha : float
        Learning rate.
    gamma : float
        Discount factor.

    Returns
    -------
    float
        The updated Q-value for (state, action).
    """
    Q.setdefault(state, {})
    Q.setdefault(next_state, {})
    Q[state].setdefault(action, 0.0)

    # max_a' Q[next_state][a'] (default 0 if no actions yet)
    next_q_values = Q[next_state].values()
    max_next = max(next_q_values) if next_q_values else 0.0

    td_target = reward + gamma * max_next
    td_error = td_target - Q[state][action]
    Q[state][action] += alpha * td_error
    return Q[state][action]


class TabularQAgent:
    """
    Simple tabular Q-learning agent for discrete-state, discrete-action environments.

    Example env requirement:
      - env.reset() -> state (int)
      - env.step(action) -> (next_state (int), reward (float), done (bool), info (dict))
      - env.action_space.n (int) or you can pass n_actions when creating the agent
      - states can be ints (if environment uses other types, map them to ints externally)
    """

    def __init__(
        self,
        n_actions: Optional[int] = None,
        alpha: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 0.1,
        seed: Optional[int] = None,
    ):
        self.Q: Dict[int, Dict[int, float]] = {}
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def set_n_actions(self, n: int) -> None:
        self.n_actions = n

    def get_action(self, state: int) -> int:
        """Epsilon-greedy action selection."""
        if self.n_actions is None:
            raise ValueError("n_actions must be set before selecting actions.")
        # exploration
        if random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        # exploitation: choose action with highest Q (ties random)
        self.Q.setdefault(state, {})
        qvals = [self.Q[state].get(a, 0.0) for a in range(self.n_actions)]
        max_val = max(qvals)
        # break ties uniformly at random
        candidates = [a for a, v in enumerate(qvals) if v == max_val]
        return random.choice(candidates)

    def update(self, state: int, action: int, reward: float, next_state: int) -> float:
        """Perform a Q-learning update and return the new Q-value."""
        return qlearn_step(self.Q, state, action, reward, next_state, self.alpha, self.gamma)

    def learn_episode(self, env, max_steps: int = 1000) -> float:
        """
        Run one episode in a gym-like env and update Q during the episode.

        Returns total reward collected in the episode.
        """
        if self.n_actions is None:
            # try to auto-detect
            try:
                self.n_actions = env.action_space.n
            except Exception:
                raise ValueError("n_actions not set and env.action_space.n unavailable.")

        state = env.reset()
        total_reward = 0.0
        for _ in range(max_steps):
            action = self.get_action(state)
            next_state, reward, done, _ = env.step(action)
            self.update(state, action, reward, next_state)
            total_reward += reward
            state = next_state
            if done:
                break
        return total_reward

    def policy(self):
        """Return a greedy policy dict mapping state -> best action."""
        policy = {}
        for s, actions in self.Q.items():
            best_a = max(actions.items(), key=lambda x: x[1])[0] if actions else 0
            policy[s] = best_a
        return policy
