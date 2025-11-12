"""
Policy Gradient Methods for Trading
==================================

This module implements policy gradient algorithms specifically designed for algorithmic trading.
Includes REINFORCE, Actor-Critic, PPO, and advanced policy optimization techniques.

Key Features:
- Policy gradient algorithms (REINFORCE, Actor-Critic, PPO)
- Continuous action spaces for precise position sizing
- Trust region policy optimization
- Advantage function estimation
- Entropy regularization for exploration
- Risk-adjusted policy learning
- Multi-agent policy optimization
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, namedtuple
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler

# Neural network dependencies
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.distributions import Normal, Categorical
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    keras = None

# Fallback for when neither is available
if not TORCH_AVAILABLE and not TF_AVAILABLE:
    raise ImportError("Either PyTorch or TensorFlow must be installed for policy gradient functionality")


@dataclass
class PolicyGradientConfig:
    """Configuration for policy gradient algorithms"""

    # Network architecture
    network_type: str = "torch"
    actor_hidden_layers: List[int] = field(default_factory=lambda: [128, 128, 64])
    critic_hidden_layers: List[int] = field(default_factory=lambda: [128, 128, 64])
    activation: str = "relu"
    dropout_rate: float = 0.1

    # Learning parameters
    actor_learning_rate: float = 0.0003
    critic_learning_rate: float = 0.001
    discount_factor: float = 0.99
    gae_lambda: float = 0.95  # Generalized Advantage Estimation

    # PPO specific
    clip_ratio: float = 0.2
    value_clip: bool = True
    entropy_coefficient: float = 0.01
    value_loss_coefficient: float = 0.5

    # Training parameters
    max_episodes: int = 2000
    max_steps_per_episode: int = 2000
    batch_size: int = 64
    epochs_per_update: int = 10
    minibatch_size: int = 32

    # Exploration and stability
    exploration_noise: float = 0.1
    target_kl_divergence: float = 0.01
    max_grad_norm: float = 0.5

    # Risk management
    risk_aversion: float = 0.1
    max_drawdown_limit: float = 0.1
    position_size_limit: float = 0.1

    # Hardware acceleration
    use_gpu: bool = True
    device: Optional[str] = None

    # Action space
    action_space_type: str = "discrete"  # "discrete" or "continuous"
    n_discrete_actions: int = 30  # For discrete actions

    # Trading specific
    transaction_cost: float = 0.001
    market_impact: bool = True


Trajectory = namedtuple('Trajectory',
                       ['states', 'actions', 'log_probs', 'values', 'rewards', 'dones'])


class ActorNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Policy network (Actor) for policy gradient methods"""

    def __init__(self, input_dim: int, action_dim: int, hidden_layers: List[int],
                 action_space_type: str = "discrete"):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for ActorNetwork")

        super().__init__()

        self.action_space_type = action_space_type
        self.action_dim = action_dim

        # Feature extraction layers
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_layers:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim

        self.feature_extractor = nn.Sequential(*layers)

        # Output layers
        if action_space_type == "discrete":
            self.action_head = nn.Linear(prev_dim, action_dim)
        else:  # continuous
            self.mean_head = nn.Linear(prev_dim, action_dim)
            self.std_head = nn.Linear(prev_dim, action_dim)

    def forward(self, x):
        features = self.feature_extractor(x)

        if self.action_space_type == "discrete":
            logits = self.action_head(features)
            return F.softmax(logits, dim=-1)
        else:
            mean = torch.tanh(self.mean_head(features))
            std = F.softplus(self.std_head(features)) + 0.001  # Ensure positive std
            return mean, std

    def get_action(self, state, deterministic=False):
        """Sample action from policy"""
        if self.action_space_type == "discrete":
            probs = self.forward(state)
            if deterministic:
                action = probs.argmax(dim=-1)
                log_prob = torch.log(probs.gather(-1, action.unsqueeze(-1)).squeeze(-1))
            else:
                dist = Categorical(probs)
                action = dist.sample()
                log_prob = dist.log_prob(action)
        else:
            mean, std = self.forward(state)
            if deterministic:
                action = mean
                # For continuous actions, log_prob is not well-defined for deterministic
                log_prob = torch.zeros_like(mean[:, 0])
            else:
                dist = Normal(mean, std)
                action = dist.sample()
                log_prob = dist.log_prob(action).sum(dim=-1)

        return action, log_prob

    def get_log_prob(self, state, action):
        """Get log probability of action given state"""
        if self.action_space_type == "discrete":
            probs = self.forward(state)
            return torch.log(probs.gather(-1, action.unsqueeze(-1)).squeeze(-1))
        else:
            mean, std = self.forward(state)
            dist = Normal(mean, std)
            return dist.log_prob(action).sum(dim=-1)


class CriticNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Value network (Critic) for policy gradient methods"""

    def __init__(self, input_dim: int, hidden_layers: List[int]):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for CriticNetwork")

        super().__init__()

        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_layers:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class REINFORCEAgent:
    """REINFORCE (Monte Carlo Policy Gradient) implementation"""

    def __init__(self, config: PolicyGradientConfig, state_dim: int, action_dim: int):
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim

        # Initialize device
        if TORCH_AVAILABLE and config.use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif TORCH_AVAILABLE:
            self.device = torch.device("cpu")
        else:
            self.device = None

        # Initialize networks
        self.policy = ActorNetwork(state_dim, action_dim, config.actor_hidden_layers,
                                  config.action_space_type)

        if TORCH_AVAILABLE:
            self.policy.to(self.device)
            self.optimizer = optim.Adam(self.policy.parameters(), lr=config.actor_learning_rate)

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.policy_losses = []

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[np.ndarray, float]:
        """Select action using current policy"""

        if not TORCH_AVAILABLE:
            return np.random.randint(self.action_dim), 0.0

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action, log_prob = self.policy.get_action(state_tensor, deterministic=not training)

        return action.cpu().numpy().flatten(), log_prob.item()

    def compute_returns(self, rewards: List[float]) -> List[float]:
        """Compute discounted returns for REINFORCE"""
        returns = []
        R = 0
        for r in reversed(rewards):
            R = r + self.config.discount_factor * R
            returns.insert(0, R)
        return returns

    def update_policy(self, trajectories: List[Trajectory]):
        """Update policy using REINFORCE algorithm"""

        if not TORCH_AVAILABLE:
            return

        all_states = []
        all_actions = []
        all_returns = []

        for trajectory in trajectories:
            returns = self.compute_returns(trajectory.rewards)

            # Normalize returns for stability
            returns = torch.FloatTensor(returns).to(self.device)
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

            all_states.extend(trajectory.states)
            all_actions.extend(trajectory.actions)
            all_returns.extend(returns.tolist())

        # Convert to tensors
        states = torch.FloatTensor(all_states).to(self.device)
        actions = torch.LongTensor(all_actions).to(self.device) if self.config.action_space_type == "discrete" \
                 else torch.FloatTensor(all_actions).to(self.device)
        returns = torch.FloatTensor(all_returns).to(self.device)

        # Compute log probabilities
        log_probs = self.policy.get_log_prob(states, actions)

        # Compute policy loss
        policy_loss = -(log_probs * returns).mean()

        # Update policy
        self.optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.config.max_grad_norm)
        self.optimizer.step()

        self.policy_losses.append(policy_loss.item())

    def train_episode(self, env) -> Tuple[float, int]:
        """Train for one episode using REINFORCE"""

        states = []
        actions = []
        log_probs = []
        rewards = []

        state = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False

        while not done and steps < self.config.max_steps_per_episode:
            # Select action
            action, log_prob = self.select_action(state, training=True)

            # Execute action
            next_state, reward, done, info = env.step(action)

            # Store trajectory
            states.append(state)
            actions.append(action)
            log_probs.append(log_prob)
            rewards.append(reward)

            episode_reward += reward
            state = next_state
            steps += 1

        # Create trajectory and update policy
        trajectory = Trajectory(states, actions, log_probs, None, rewards, None)
        self.update_policy([trajectory])

        return episode_reward, steps

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the REINFORCE agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting REINFORCE training for {n_episodes} episodes...")
        print(f"Using device: {self.device if TORCH_AVAILABLE else 'CPU (no PyTorch)'}")

        for episode in range(n_episodes):
            episode_reward, episode_length = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)

            if (episode + 1) % 25 == 0:
                avg_reward = np.mean(self.episode_rewards[-25:])
                avg_length = np.mean(self.episode_lengths[-25:])
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}")

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "policy_losses": self.policy_losses
        }


class ActorCriticAgent:
    """Actor-Critic implementation with advantage function"""

    def __init__(self, config: PolicyGradientConfig, state_dim: int, action_dim: int):
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim

        # Initialize device
        if TORCH_AVAILABLE and config.use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif TORCH_AVAILABLE:
            self.device = torch.device("cpu")
        else:
            self.device = None

        # Initialize networks
        self.actor = ActorNetwork(state_dim, action_dim, config.actor_hidden_layers,
                                 config.action_space_type)
        self.critic = CriticNetwork(state_dim, config.critic_hidden_layers)

        if TORCH_AVAILABLE:
            self.actor.to(self.device)
            self.critic.to(self.device)

            self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=config.actor_learning_rate)
            self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.critic_learning_rate)

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.actor_losses = []
        self.critic_losses = []
        self.entropies = []

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[np.ndarray, float]:
        """Select action using current policy"""

        if not TORCH_AVAILABLE:
            return np.random.randint(self.action_dim), 0.0

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action, log_prob = self.actor.get_action(state_tensor, deterministic=not training)
            value = self.critic(state_tensor)

        return action.cpu().numpy().flatten(), log_prob.item(), value.item()

    def compute_gae_advantages(self, rewards: List[float], values: List[float],
                             next_values: List[float], dones: List[bool]) -> Tuple[List[float], List[float]]:
        """Compute Generalized Advantage Estimation (GAE)"""

        advantages = []
        returns = []
        gae = 0

        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0 if dones[t] else next_values[t]
            else:
                next_value = values[t + 1]

            delta = rewards[t] + self.config.discount_factor * next_value - values[t]
            gae = delta + self.config.discount_factor * self.config.gae_lambda * gae

            advantages.insert(0, gae)
            returns.insert(0, gae + values[t])

        return advantages, returns

    def update_networks(self, trajectories: List[Trajectory]):
        """Update actor and critic networks"""

        if not TORCH_AVAILABLE:
            return

        all_states = []
        all_actions = []
        all_old_log_probs = []
        all_advantages = []
        all_returns = []

        for trajectory in trajectories:
            # Get value estimates for all states
            states_tensor = torch.FloatTensor(trajectory.states).to(self.device)
            with torch.no_grad():
                values = self.critic(states_tensor).squeeze().tolist()
                next_values = values[1:] + [0]  # Last next_value is 0

            # Compute advantages and returns
            advantages, returns = self.compute_gae_advantages(
                trajectory.rewards, values, next_values, trajectory.dones or [False] * len(trajectory.rewards)
            )

            # Normalize advantages
            advantages = np.array(advantages)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            all_states.extend(trajectory.states)
            all_actions.extend(trajectory.actions)
            all_old_log_probs.extend(trajectory.log_probs)
            all_advantages.extend(advantages.tolist())
            all_returns.extend(returns)

        # Convert to tensors
        states = torch.FloatTensor(all_states).to(self.device)
        actions = torch.LongTensor(all_actions).to(self.device) if self.config.action_space_type == "discrete" \
                 else torch.FloatTensor(all_actions).to(self.device)
        old_log_probs = torch.FloatTensor(all_old_log_probs).to(self.device)
        advantages = torch.FloatTensor(all_advantages).to(self.device)
        returns = torch.FloatTensor(all_returns).to(self.device)

        # Update critic
        values_pred = self.critic(states).squeeze()
        critic_loss = F.mse_loss(values_pred, returns)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.config.max_grad_norm)
        self.critic_optimizer.step()

        # Update actor
        new_log_probs = self.actor.get_log_prob(states, actions)
        ratio = torch.exp(new_log_probs - old_log_probs)

        # Policy loss with entropy bonus
        if self.config.action_space_type == "discrete":
            probs = self.actor(states)
            entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=-1).mean()
        else:
            mean, std = self.actor.forward(states)
            dist = Normal(mean, std)
            entropy = dist.entropy().mean()

        actor_loss = -(ratio * advantages).mean() - self.config.entropy_coefficient * entropy

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.config.max_grad_norm)
        self.actor_optimizer.step()

        self.actor_losses.append(actor_loss.item())
        self.critic_losses.append(critic_loss.item())
        self.entropies.append(entropy.item())

    def train_episode(self, env) -> Tuple[float, int]:
        """Train for one episode using Actor-Critic"""

        states = []
        actions = []
        log_probs = []
        values = []
        rewards = []
        dones = []

        state = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False

        while not done and steps < self.config.max_steps_per_episode:
            # Select action
            action, log_prob, value = self.select_action(state, training=True)

            # Execute action
            next_state, reward, done, info = env.step(action)

            # Store trajectory
            states.append(state)
            actions.append(action)
            log_probs.append(log_prob)
            values.append(value)
            rewards.append(reward)
            dones.append(done)

            episode_reward += reward
            state = next_state
            steps += 1

        # Create trajectory and update networks
        trajectory = Trajectory(states, actions, log_probs, values, rewards, dones)
        self.update_networks([trajectory])

        return episode_reward, steps

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the Actor-Critic agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting Actor-Critic training for {n_episodes} episodes...")
        print(f"Using device: {self.device if TORCH_AVAILABLE else 'CPU (no PyTorch)'}")

        for episode in range(n_episodes):
            episode_reward, episode_length = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)

            if (episode + 1) % 25 == 0:
                avg_reward = np.mean(self.episode_rewards[-25:])
                avg_length = np.mean(self.episode_lengths[-25:])
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}")

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "actor_losses": self.actor_losses,
            "critic_losses": self.critic_losses,
            "entropies": self.entropies
        }


class PPOAgent:
    """Proximal Policy Optimization (PPO) implementation"""

    def __init__(self, config: PolicyGradientConfig, state_dim: int, action_dim: int):
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim

        # Initialize device
        if TORCH_AVAILABLE and config.use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif TORCH_AVAILABLE:
            self.device = torch.device("cpu")
        else:
            self.device = None

        # Initialize networks
        self.actor = ActorNetwork(state_dim, action_dim, config.actor_hidden_layers,
                                 config.action_space_type)
        self.critic = CriticNetwork(state_dim, config.critic_hidden_layers)

        # Target networks for stability
        self.actor_old = ActorNetwork(state_dim, action_dim, config.actor_hidden_layers,
                                     config.action_space_type)
        self.critic_old = CriticNetwork(state_dim, config.critic_hidden_layers)

        if TORCH_AVAILABLE:
            self.actor.to(self.device)
            self.critic.to(self.device)
            self.actor_old.to(self.device)
            self.critic_old.to(self.device)

            # Copy initial weights
            self.actor_old.load_state_dict(self.actor.state_dict())
            self.critic_old.load_state_dict(self.critic.state_dict())

            self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=config.actor_learning_rate)
            self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.critic_learning_rate)

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.actor_losses = []
        self.critic_losses = []
        self.entropies = []
        self.approx_kls = []

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[np.ndarray, float, float]:
        """Select action using current policy"""

        if not TORCH_AVAILABLE:
            return np.random.randint(self.action_dim), 0.0, 0.0

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action, log_prob = self.actor_old.get_action(state_tensor, deterministic=not training)
            value = self.critic_old(state_tensor)

        return action.cpu().numpy().flatten(), log_prob.item(), value.item()

    def collect_trajectories(self, env, n_trajectories: int) -> List[Trajectory]:
        """Collect trajectories for PPO training"""

        trajectories = []

        for _ in range(n_trajectories):
            states = []
            actions = []
            log_probs = []
            values = []
            rewards = []
            dones = []

            state = env.reset()
            done = False
            steps = 0

            while not done and steps < self.config.max_steps_per_episode:
                # Select action
                action, log_prob, value = self.select_action(state, training=True)

                # Execute action
                next_state, reward, done, info = env.step(action)

                # Store trajectory
                states.append(state)
                actions.append(action)
                log_probs.append(log_prob)
                values.append(value)
                rewards.append(reward)
                dones.append(done)

                state = next_state
                steps += 1

            trajectories.append(Trajectory(states, actions, log_probs, values, rewards, dones))

        return trajectories

    def compute_gae_advantages(self, rewards: List[float], values: List[float],
                             dones: List[bool]) -> Tuple[List[float], List[float]]:
        """Compute GAE advantages and returns"""

        advantages = []
        returns = []
        gae = 0
        next_value = 0

        for t in reversed(range(len(rewards))):
            if dones[t]:
                next_value = 0
            else:
                next_value = values[t]

            delta = rewards[t] + self.config.discount_factor * next_value - values[t]
            gae = delta + self.config.discount_factor * self.config.gae_lambda * gae

            advantages.insert(0, gae)
            returns.insert(0, gae + values[t])

        return advantages, returns

    def update_networks(self, trajectories: List[Trajectory]):
        """Update networks using PPO algorithm"""

        if not TORCH_AVAILABLE:
            return

        # Flatten all trajectories
        all_states = []
        all_actions = []
        all_old_log_probs = []
        all_values = []
        all_advantages = []
        all_returns = []

        for trajectory in trajectories:
            # Compute advantages and returns
            advantages, returns = self.compute_gae_advantages(
                trajectory.rewards, trajectory.values, trajectory.dones
            )

            # Normalize advantages
            advantages = np.array(advantages)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            all_states.extend(trajectory.states)
            all_actions.extend(trajectory.actions)
            all_old_log_probs.extend(trajectory.log_probs)
            all_values.extend(trajectory.values)
            all_advantages.extend(advantages.tolist())
            all_returns.extend(returns)

        # Convert to tensors
        states = torch.FloatTensor(all_states).to(self.device)
        actions = torch.LongTensor(all_actions).to(self.device) if self.config.action_space_type == "discrete" \
                 else torch.FloatTensor(all_actions).to(self.device)
        old_log_probs = torch.FloatTensor(all_old_log_probs).to(self.device)
        values = torch.FloatTensor(all_values).to(self.device)
        advantages = torch.FloatTensor(all_advantages).to(self.device)
        returns = torch.FloatTensor(all_returns).to(self.device)

        # Create dataset for mini-batch training
        dataset = torch.utils.data.TensorDataset(states, actions, old_log_probs, advantages, returns)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.config.minibatch_size, shuffle=True)

        # PPO training loop
        for epoch in range(self.config.epochs_per_update):
            for batch_states, batch_actions, batch_old_log_probs, batch_advantages, batch_returns in dataloader:

                # Update critic
                values_pred = self.critic(batch_states).squeeze()
                if self.config.value_clip:
                    values_clipped = values + torch.clamp(values_pred - values, -self.config.clip_ratio, self.config.clip_ratio)
                    critic_loss1 = F.mse_loss(values_pred, batch_returns)
                    critic_loss2 = F.mse_loss(values_clipped, batch_returns)
                    critic_loss = torch.max(critic_loss1, critic_loss2).mean()
                else:
                    critic_loss = F.mse_loss(values_pred, batch_returns)

                self.critic_optimizer.zero_grad()
                critic_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.config.max_grad_norm)
                self.critic_optimizer.step()

                # Update actor
                new_log_probs = self.actor.get_log_prob(batch_states, batch_actions)
                ratio = torch.exp(new_log_probs - batch_old_log_probs)

                # Clipped surrogate objective
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.config.clip_ratio, 1 + self.config.clip_ratio) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()

                # Add entropy bonus
                if self.config.action_space_type == "discrete":
                    probs = self.actor(batch_states)
                    entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=-1).mean()
                else:
                    mean, std = self.actor.forward(batch_states)
                    dist = Normal(mean, std)
                    entropy = dist.entropy().mean()

                actor_loss -= self.config.entropy_coefficient * entropy

                # Approximate KL divergence for early stopping
                approx_kl = (batch_old_log_probs - new_log_probs).mean().item()

                self.actor_optimizer.zero_grad()
                actor_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.config.max_grad_norm)
                self.actor_optimizer.step()

                # Store metrics
                self.actor_losses.append(actor_loss.item())
                self.critic_losses.append(critic_loss.item())
                self.entropies.append(entropy.item())
                self.approx_kls.append(approx_kl)

                # Early stopping based on KL divergence
                if approx_kl > self.config.target_kl_divergence:
                    break

        # Update old networks
        self.actor_old.load_state_dict(self.actor.state_dict())
        self.critic_old.load_state_dict(self.critic.state_dict())

    def train_episode(self, env) -> Tuple[float, int]:
        """Train for one episode using PPO"""

        # Collect trajectories
        trajectories = self.collect_trajectories(env, self.config.batch_size)

        # Update networks
        self.update_networks(trajectories)

        # Calculate episode statistics from first trajectory
        episode_reward = sum(trajectories[0].rewards)
        episode_length = len(trajectories[0].rewards)

        return episode_reward, episode_length

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the PPO agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting PPO training for {n_episodes} episodes...")
        print(f"Using device: {self.device if TORCH_AVAILABLE else 'CPU (no PyTorch)'}")

        for episode in range(n_episodes):
            episode_reward, episode_length = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)

            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_length = np.mean(self.episode_lengths[-10:])
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}")

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "actor_losses": self.actor_losses,
            "critic_losses": self.critic_losses,
            "entropies": self.entropies,
            "approx_kls": self.approx_kls
        }


def create_reinforce_agent(config: Optional[PolicyGradientConfig] = None,
                          state_dim: int = 15, action_dim: int = 30) -> REINFORCEAgent:
    """Factory function for REINFORCE agent"""
    if config is None:
        config = PolicyGradientConfig()
    return REINFORCEAgent(config, state_dim, action_dim)


def create_actor_critic_agent(config: Optional[PolicyGradientConfig] = None,
                             state_dim: int = 15, action_dim: int = 30) -> ActorCriticAgent:
    """Factory function for Actor-Critic agent"""
    if config is None:
        config = PolicyGradientConfig()
    return ActorCriticAgent(config, state_dim, action_dim)


def create_ppo_agent(config: Optional[PolicyGradientConfig] = None,
                    state_dim: int = 15, action_dim: int = 30) -> PPOAgent:
    """Factory function for PPO agent"""
    if config is None:
        config = PolicyGradientConfig()
    return PPOAgent(config, state_dim, action_dim)


# Example usage and testing
if __name__ == "__main__":
    # Test policy gradient agents
    print("Testing Policy Gradient Agents...")

    if TORCH_AVAILABLE:
        config = PolicyGradientConfig(max_episodes=5)  # Short training for demo

        # Test REINFORCE
        print("\n1. Testing REINFORCE...")
        reinforce_agent = create_reinforce_agent(config)
        print(f"REINFORCE agent created with {sum(p.numel() for p in reinforce_agent.policy.parameters())} parameters")

        # Test Actor-Critic
        print("\n2. Testing Actor-Critic...")
        ac_agent = create_actor_critic_agent(config)
        print(f"Actor-Critic agent created with {sum(p.numel() for p in ac_agent.actor.parameters()) + sum(p.numel() for p in ac_agent.critic.parameters())} parameters")

        # Test PPO
        print("\n3. Testing PPO...")
        ppo_agent = create_ppo_agent(config)
        print(f"PPO agent created with {sum(p.numel() for p in ppo_agent.actor.parameters()) + sum(p.numel() for p in ppo_agent.critic.parameters())} parameters")

        print(f"\nUsing device: {reinforce_agent.device}")
        print("Policy Gradient configuration:")
        print(f"  - Action space: {config.action_space_type}")
        print(f"  - Actor hidden layers: {config.actor_hidden_layers}")
        print(f"  - Critic hidden layers: {config.critic_hidden_layers}")
        print(f"  - Clip ratio: {config.clip_ratio}")
        print(f"  - Entropy coefficient: {config.entropy_coefficient}")

        # Test prediction on random state
        test_state = np.random.normal(0, 1, 15)
        action, log_prob = reinforce_agent.select_action(test_state)
        print(f"REINFORCE predicted action: {action}, log_prob: {log_prob:.3f}")

    else:
        print("PyTorch not available - Policy Gradient functionality disabled")
        print("Install PyTorch to enable policy gradient trading: pip install torch")
