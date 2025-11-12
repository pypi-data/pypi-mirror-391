import pytest
from qlearn import qlearn_step, TabularQAgent

def test_qlearn_step_zero_init():
    Q = {}
    updated = qlearn_step(Q, state=0, action=1, reward=1.0, next_state=1, alpha=0.5, gamma=0.0)
    # since Q[0][1] starts at 0, with gamma=0, new value should be 0 + alpha * (1 - 0) = 0.5
    assert pytest.approx(updated, rel=1e-6) == 0.5
    assert Q[0][1] == updated

def test_tabular_agent_basic():
    agent = TabularQAgent(n_actions=2, alpha=1.0, gamma=0.0, epsilon=0.0, seed=123)
    # deterministic: select greedy action (both are 0 so choose any)
    a = agent.get_action(0)
    assert a in (0,1)
    # update and check policy
    agent.update(0, 0, reward=2.0, next_state=0)
    pol = agent.policy()
    assert pol[0] == 0
