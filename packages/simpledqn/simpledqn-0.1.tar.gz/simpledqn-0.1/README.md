\# SimpleDQN



A simple PyTorch-based Deep Q-Network (DQN) implementation for beginners in Reinforcement Learning.



\## Installation

```bash

pip install simpledqn

```



\## Usage

```python

from simpledqn import DQNAgent

import gymnasium as gym



env = gym.make("CartPole-v1")

agent = DQNAgent(env, episodes=100)

agent.train()

agent.plot\_rewards()

```



