import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

class DQNAgent:
    def __init__(self, env, episodes=500, gamma=0.99, lr=1e-3, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.env = env
        self.episodes = episodes
        self.gamma = gamma
        self.lr = lr
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=50000)
        self.batch_size = 64
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        obs_size = env.observation_space.shape[0]
        n_actions = env.action_space.n

        self.policy_net = self._build_model(obs_size, n_actions).to(self.device)
        self.target_net = self._build_model(obs_size, n_actions).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.loss_fn = nn.MSELoss()

        self.rewards_history = []

    def _build_model(self, input_dim, output_dim):
        return nn.Sequential(
            nn.Linear(input_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, output_dim)
        )

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if random.random() < self.epsilon:
            return self.env.action_space.sample()
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state)
        return q_values.argmax().item()

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q_values = self.target_net(next_states).max(1)[0]
        target = rewards + self.gamma * next_q_values * (1 - dones)

        loss = self.loss_fn(q_values, target.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def train(self):
        for ep in range(self.episodes):
            state, _ = self.env.reset()
            total_reward = 0
            done = False

            while not done:
                action = self.act(state)
                next_state, reward, done, truncated, _ = self.env.step(action)
                self.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                self.replay()

            self.rewards_history.append(total_reward)
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            if ep % 10 == 0:
                self.target_net.load_state_dict(self.policy_net.state_dict())
                print(f"Episode {ep}/{self.episodes}, Reward: {total_reward}, Epsilon: {self.epsilon:.2f}")

        print("Training finished!")

    def plot_rewards(self):
        plt.plot(self.rewards_history)
        plt.title("DQN Rewards over Episodes")
        plt.xlabel("Episode")
        plt.ylabel("Total Reward")
        plt.show()
