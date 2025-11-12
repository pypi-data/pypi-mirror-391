"""
Deep Q-Network (DQN) Implementation for Trading
==============================================

This module implements Deep Q-Network algorithms specifically designed for algorithmic trading.
Includes Double DQN, Dueling DQN, and prioritized experience replay for stable learning.

Key Features:
- Deep neural network Q-function approximation
- Double DQN for reduced overestimation bias
- Dueling architecture for better value estimation
- Prioritized experience replay for efficient learning
- Risk-aware exploration and position sizing
- Multi-asset portfolio optimization
- Hardware acceleration support (GPU/TPU)
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
    raise ImportError("Either PyTorch or TensorFlow must be installed for DQN functionality")


@dataclass
class DQNConfig:
    """Configuration for DQN algorithm"""

    # Network architecture
    network_type: str = "torch"  # "torch" or "tensorflow"
    hidden_layers: List[int] = field(default_factory=lambda: [128, 128, 64])
    activation: str = "relu"
    dropout_rate: float = 0.1

    # Learning parameters
    learning_rate: float = 0.001
    discount_factor: float = 0.99
    exploration_rate: float = 1.0
    exploration_decay: float = 0.995
    min_exploration_rate: float = 0.01

    # Experience replay
    replay_buffer_size: int = 50000
    batch_size: int = 64
    target_update_frequency: int = 1000

    # Double DQN
    use_double_dqn: bool = True

    # Dueling DQN
    use_dueling: bool = True

    # Prioritized replay
    use_prioritized_replay: bool = True
    priority_alpha: float = 0.6
    priority_beta: float = 0.4
    priority_beta_increment: float = 1e-6

    # Risk management
    risk_aversion: float = 0.1
    max_drawdown_limit: float = 0.1
    position_size_limit: float = 0.1

    # Training parameters
    max_episodes: int = 2000
    max_steps_per_episode: int = 2000
    convergence_threshold: float = 1e-4
    early_stopping_patience: int = 100

    # Hardware acceleration
    use_gpu: bool = True
    device: Optional[str] = None

    # Trading specific
    transaction_cost: float = 0.001
    slippage_model: str = "percentage"
    market_impact: bool = True

    # Multi-asset support
    n_assets: int = 1  # Number of assets to trade
    max_position_per_asset: float = 0.2


Experience = namedtuple('Experience',
                       ['state', 'action', 'reward', 'next_state', 'done', 'priority'])


class PrioritizedReplayBuffer:
    """Prioritized Experience Replay Buffer"""

    def __init__(self, capacity: int, alpha: float = 0.6):
        self.capacity = capacity
        self.alpha = alpha
        self.buffer = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0
        self.size = 0

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool):
        """Add experience to buffer with max priority"""
        max_priority = self.priorities.max() if self.size > 0 else 1.0

        experience = Experience(state, action, reward, next_state, done, max_priority)

        if self.size < self.capacity:
            self.buffer.append(experience)
            self.size += 1
        else:
            self.buffer[self.position] = experience

        self.priorities[self.position] = max_priority
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size: int, beta: float = 0.4) -> Tuple:
        """Sample batch with priorities"""
        if self.size < batch_size:
            return None

        # Calculate sampling probabilities
        priorities = self.priorities[:self.size]
        probs = priorities ** self.alpha
        probs /= probs.sum()

        # Sample indices
        indices = np.random.choice(self.size, batch_size, p=probs, replace=False)

        # Calculate importance sampling weights
        weights = (self.size * probs[indices]) ** (-beta)
        weights /= weights.max()  # Normalize

        # Get experiences
        experiences = [self.buffer[idx] for idx in indices]

        # Extract arrays
        states = np.array([exp.state for exp in experiences])
        actions = np.array([exp.action for exp in experiences])
        rewards = np.array([exp.reward for exp in experiences])
        next_states = np.array([exp.next_state for exp in experiences])
        dones = np.array([exp.done for exp in experiences])

        return states, actions, rewards, next_states, dones, indices, weights

    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        """Update priorities for sampled experiences"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority

    def __len__(self) -> int:
        return self.size


class DuelingQNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Dueling Q-Network architecture for better value estimation"""

    def __init__(self, input_dim: int, output_dim: int, hidden_layers: List[int]):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for DuelingQNetwork")

        super().__init__()

        # Feature extraction layers
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_layers[:-1]:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim

        self.feature_layer = nn.Sequential(*layers)

        # Value stream
        self.value_stream = nn.Sequential(
            nn.Linear(prev_dim, hidden_layers[-1]),
            nn.ReLU(),
            nn.Linear(hidden_layers[-1], 1)
        )

        # Advantage stream
        self.advantage_stream = nn.Sequential(
            nn.Linear(prev_dim, hidden_layers[-1]),
            nn.ReLU(),
            nn.Linear(hidden_layers[-1], output_dim)
        )

    def forward(self, x):
        features = self.feature_layer(x)
        values = self.value_stream(features)
        advantages = self.advantage_stream(features)

        # Combine value and advantage streams
        q_values = values + (advantages - advantages.mean(dim=1, keepdim=True))
        return q_values


class StandardQNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Standard Q-Network architecture"""

    def __init__(self, input_dim: int, output_dim: int, hidden_layers: List[int]):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for StandardQNetwork")

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

        layers.append(nn.Linear(prev_dim, output_dim))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class DQNTrader:
    """Deep Q-Network implementation for trading"""

    def __init__(self, config: DQNConfig, state_dim: int, action_dim: int):
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
        if config.use_dueling:
            self.q_network = DuelingQNetwork(state_dim, action_dim, config.hidden_layers)
            self.target_network = DuelingQNetwork(state_dim, action_dim, config.hidden_layers)
        else:
            self.q_network = StandardQNetwork(state_dim, action_dim, config.hidden_layers)
            self.target_network = StandardQNetwork(state_dim, action_dim, config.hidden_layers)

        if TORCH_AVAILABLE:
            self.q_network.to(self.device)
            self.target_network.to(self.device)
            self.target_network.load_state_dict(self.q_network.state_dict())

        # Initialize optimizer
        if TORCH_AVAILABLE:
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=config.learning_rate)

        # Initialize replay buffer
        if config.use_prioritized_replay:
            self.replay_buffer = PrioritizedReplayBuffer(config.replay_buffer_size, config.priority_alpha)
        else:
            self.replay_buffer = deque(maxlen=config.replay_buffer_size)

        # Exploration parameters
        self.exploration_rate = config.exploration_rate
        self.priority_beta = config.priority_beta

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.losses = []
        self.step_count = 0

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""

        if training and np.random.random() < self.exploration_rate:
            return np.random.randint(self.action_dim)

        if not TORCH_AVAILABLE:
            return np.random.randint(self.action_dim)

        # Convert state to tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()

    def train_on_batch(self) -> Optional[float]:
        """Train on a batch of experiences"""

        if not TORCH_AVAILABLE:
            return None

        # Sample batch
        if self.config.use_prioritized_replay:
            batch = self.replay_buffer.sample(self.config.batch_size, self.priority_beta)
            if batch is None:
                return None

            states, actions, rewards, next_states, dones, indices, weights = batch
            weights = torch.FloatTensor(weights).to(self.device)
        else:
            if len(self.replay_buffer) < self.config.batch_size:
                return None

            batch = np.random.choice(len(self.replay_buffer), self.config.batch_size, replace=False)
            experiences = [self.replay_buffer[idx] for idx in batch]

            states = np.array([exp.state for exp in experiences])
            actions = np.array([exp.action for exp in experiences])
            rewards = np.array([exp.reward for exp in experiences])
            next_states = np.array([exp.next_state for exp in experiences])
            dones = np.array([exp.done for exp in experiences])
            weights = torch.ones(self.config.batch_size).to(self.device)

        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Target Q-values
        with torch.no_grad():
            if self.config.use_double_dqn:
                # Double DQN: Use online network to select actions, target network for values
                next_actions = self.q_network(next_states).argmax(1, keepdim=True)
                next_q_values = self.target_network(next_states).gather(1, next_actions)
            else:
                # Standard DQN
                next_q_values = self.target_network(next_states).max(1, keepdim=True)[0]

            target_q_values = rewards.unsqueeze(1) + (1 - dones.unsqueeze(1)) * \
                            self.config.discount_factor * next_q_values

        # Compute loss
        loss = F.mse_loss(current_q_values, target_q_values, reduction='none')
        loss = (loss * weights.unsqueeze(1)).mean()

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Update priorities if using prioritized replay
        if self.config.use_prioritized_replay:
            td_errors = (current_q_values - target_q_values).detach().cpu().numpy().flatten()
            new_priorities = np.abs(td_errors) + 1e-6
            self.replay_buffer.update_priorities(indices, new_priorities)

            # Update beta
            self.priority_beta = min(1.0, self.priority_beta + self.config.priority_beta_increment)

        return loss.item()

    def update_target_network(self):
        """Update target network weights"""
        if TORCH_AVAILABLE:
            self.target_network.load_state_dict(self.q_network.state_dict())

    def store_experience(self, state: np.ndarray, action: int, reward: float,
                        next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""

        if self.config.use_prioritized_replay:
            self.replay_buffer.push(state, action, reward, next_state, done)
        else:
            experience = Experience(state, action, reward, next_state, done, 1.0)
            self.replay_buffer.append(experience)

    def train_episode(self, env) -> Tuple[float, int]:
        """Train for one episode"""

        state = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False
        episode_loss = 0.0
        loss_count = 0

        while not done and steps < self.config.max_steps_per_episode:
            # Select and execute action
            action = self.select_action(state, training=True)
            next_state, reward, done, info = env.step(action)

            # Store experience
            self.store_experience(state, action, reward, next_state, done)

            # Train on batch
            loss = self.train_on_batch()
            if loss is not None:
                episode_loss += loss
                loss_count += 1

            episode_reward += reward
            state = next_state
            steps += 1
            self.step_count += 1

            # Update target network
            if self.step_count % self.config.target_update_frequency == 0:
                self.update_target_network()

        # Decay exploration rate
        self.exploration_rate = max(
            self.config.min_exploration_rate,
            self.exploration_rate * self.config.exploration_decay
        )

        avg_loss = episode_loss / loss_count if loss_count > 0 else 0.0
        return episode_reward, steps, avg_loss

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the DQN agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting DQN training for {n_episodes} episodes...")
        print(f"Using device: {self.device if TORCH_AVAILABLE else 'CPU (no PyTorch)'}")
        print(f"Double DQN: {self.config.use_double_dqn}")
        print(f"Dueling: {self.config.use_dueling}")
        print(f"Prioritized Replay: {self.config.use_prioritized_replay}")

        for episode in range(n_episodes):
            episode_reward, episode_length, avg_loss = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            self.losses.append(avg_loss)

            if (episode + 1) % 25 == 0:
                avg_reward = np.mean(self.episode_rewards[-25:])
                avg_length = np.mean(self.episode_lengths[-25:])
                avg_loss_val = np.mean(self.losses[-25:]) if self.losses[-25:] else 0
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}, Avg Loss = {avg_loss_val:.4f}, "
                      f"Exploration Rate = {self.exploration_rate:.3f}, "
                      f"Buffer Size = {len(self.replay_buffer)}")

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "losses": self.losses,
            "final_exploration_rate": self.exploration_rate
        }

    def predict(self, state: np.ndarray) -> int:
        """Predict best action for given state"""
        return self.select_action(state, training=False)

    def save_model(self, path: str):
        """Save model weights"""
        if TORCH_AVAILABLE:
            torch.save({
                'q_network': self.q_network.state_dict(),
                'target_network': self.target_network.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'config': self.config,
                'exploration_rate': self.exploration_rate
            }, path)

    def load_model(self, path: str):
        """Load model weights"""
        if TORCH_AVAILABLE:
            checkpoint = torch.load(path)
            self.q_network.load_state_dict(checkpoint['q_network'])
            self.target_network.load_state_dict(checkpoint['target_network'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.exploration_rate = checkpoint.get('exploration_rate', self.config.exploration_rate)


class MultiAssetDQNTrader:
    """DQN trader for multiple assets with portfolio optimization"""

    def __init__(self, config: DQNConfig, n_assets: int, state_dim_per_asset: int):
        self.config = config
        self.n_assets = n_assets
        self.state_dim_per_asset = state_dim_per_asset

        # Total state dimension includes all assets plus portfolio state
        total_state_dim = n_assets * state_dim_per_asset + 10  # +10 for portfolio features

        # Action space: for each asset, hold/buy/sell with different sizes
        action_dim = n_assets * 30  # 30 actions per asset (3 types x 10 sizes)

        self.dqn = DQNTrader(config, total_state_dim, action_dim)

        # Portfolio state tracking
        self.portfolio_cash = config.n_assets * 10000  # Initial cash per asset
        self.portfolio_positions = np.zeros(n_assets)

    def get_portfolio_state(self) -> np.ndarray:
        """Get current portfolio state"""
        total_value = self.portfolio_cash + np.sum(self.portfolio_positions)
        return np.array([
            self.portfolio_cash / total_value,  # Cash ratio
            np.mean(self.portfolio_positions),  # Average position
            np.std(self.portfolio_positions),   # Position diversity
            np.max(self.portfolio_positions),   # Max position
            np.min(self.portfolio_positions),   # Min position
            total_value,                        # Total portfolio value
            len(self.portfolio_positions[self.portfolio_positions > 0]),  # Number of long positions
            len(self.portfolio_positions[self.portfolio_positions < 0]),  # Number of short positions
            np.sum(np.abs(self.portfolio_positions)),  # Total exposure
            np.var(self.portfolio_positions)     # Position variance
        ])

    def decode_action(self, action_idx: int) -> List[Tuple[int, str, float]]:
        """Decode action index into asset-specific actions"""
        actions = []
        for asset_idx in range(self.n_assets):
            asset_action_idx = action_idx % 30
            action_idx = action_idx // 30

            action_type_idx = asset_action_idx // 10
            action_types = ["hold", "buy", "sell"]
            action_type = action_types[action_type_idx]

            position_size = (asset_action_idx % 10) / 9.0  # 0.0 to 1.0

            actions.append((asset_idx, action_type, position_size))

        return actions

    def execute_portfolio_action(self, actions: List[Tuple[int, str, float]],
                                current_prices: np.ndarray) -> float:
        """Execute portfolio actions and return reward"""

        total_reward = 0.0
        transaction_costs = 0.0

        for asset_idx, action_type, position_size in actions:
            current_price = current_prices[asset_idx]
            current_position = self.portfolio_positions[asset_idx]

            if action_type == "buy":
                # Buy with position size (as fraction of available cash)
                max_buy_value = self.portfolio_cash * position_size
                shares_to_buy = max_buy_value / current_price
                cost = shares_to_buy * current_price * (1 + self.config.transaction_cost)

                if cost <= self.portfolio_cash:
                    self.portfolio_positions[asset_idx] += shares_to_buy
                    self.portfolio_cash -= cost
                    transaction_costs += cost * self.config.transaction_cost

            elif action_type == "sell" and current_position > 0:
                # Sell with position size
                shares_to_sell = current_position * position_size
                revenue = shares_to_sell * current_price * (1 - self.config.transaction_cost)

                self.portfolio_positions[asset_idx] -= shares_to_sell
                self.portfolio_cash += revenue
                transaction_costs += shares_to_sell * current_price * self.config.transaction_cost

        # Calculate portfolio reward (change in total value)
        total_value = self.portfolio_cash + np.sum(self.portfolio_positions * current_prices)
        reward = total_value - (self.config.n_assets * 10000)  # Change from initial value

        # Add risk penalty
        position_concentration = np.max(np.abs(self.portfolio_positions)) / np.sum(np.abs(self.portfolio_positions))
        if position_concentration > self.config.max_position_per_asset:
            reward -= 100  # Penalty for excessive concentration

        return reward

    def select_action(self, states: np.ndarray, training: bool = True) -> int:
        """Select action for multi-asset portfolio"""
        # Combine all asset states with portfolio state
        portfolio_state = self.get_portfolio_state()
        combined_state = np.concatenate([states.flatten(), portfolio_state])

        return self.dqn.select_action(combined_state, training)

    def train_episode(self, env) -> Tuple[float, int, float]:
        """Train for one episode with multi-asset portfolio"""
        return self.dqn.train_episode(env)

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the multi-asset DQN agent"""
        return self.dqn.train(env, n_episodes)


def create_dqn_trader(config: Optional[DQNConfig] = None,
                     state_dim: int = 15, action_dim: int = 30) -> DQNTrader:
    """Factory function for DQN trader"""
    if config is None:
        config = DQNConfig()
    return DQNTrader(config, state_dim, action_dim)


def create_multi_asset_dqn_trader(config: Optional[DQNConfig] = None,
                                 n_assets: int = 5) -> MultiAssetDQNTrader:
    """Factory function for multi-asset DQN trader"""
    if config is None:
        config = DQNConfig(n_assets=n_assets)
    return MultiAssetDQNTrader(config, n_assets, state_dim_per_asset=15)


# Example usage and testing
if __name__ == "__main__":
    # Test single asset DQN
    print("Testing DQN Trader...")

    if TORCH_AVAILABLE:
        config = DQNConfig(max_episodes=5)  # Short training for demo
        trader = create_dqn_trader(config)

        print(f"DQN Trader created with {sum(p.numel() for p in trader.q_network.parameters())} parameters")
        print(f"Using device: {trader.device}")
        print("DQN configuration:")
        print(f"  - Double DQN: {config.use_double_dqn}")
        print(f"  - Dueling: {config.use_dueling}")
        print(f"  - Prioritized Replay: {config.use_prioritized_replay}")
        print(f"  - Hidden layers: {config.hidden_layers}")

        # Test prediction on random state
        test_state = np.random.normal(0, 1, 15)
        action = trader.predict(test_state)
        print(f"Predicted action for random state: {action}")

    else:
        print("PyTorch not available - DQN functionality disabled")
        print("Install PyTorch to enable DQN trading: pip install torch")
