"""
Q-Learning Implementation for Trading
====================================

This module implements Q-learning algorithms specifically designed for financial trading.
Includes tabular Q-learning, function approximation, and trading-specific adaptations.

Key Features:
- Tabular Q-learning for discrete state-action spaces
- Linear function approximation for continuous states
- Experience replay for stable learning
- Risk-aware exploration strategies
- Trading-specific reward functions
- Portfolio optimization integration
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import defaultdict, deque
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor


@dataclass
class QLearningConfig:
    """Configuration for Q-learning algorithm"""

    # Learning parameters
    learning_rate: float = 0.1
    discount_factor: float = 0.99
    exploration_rate: float = 1.0
    exploration_decay: float = 0.995
    min_exploration_rate: float = 0.01

    # Experience replay
    replay_buffer_size: int = 10000
    batch_size: int = 32
    target_update_frequency: int = 100

    # Risk management
    risk_aversion: float = 0.1
    max_drawdown_limit: float = 0.1
    position_size_limit: float = 0.1

    # Training parameters
    max_episodes: int = 1000
    max_steps_per_episode: int = 1000
    convergence_threshold: float = 1e-4
    early_stopping_patience: int = 50

    # Trading specific
    transaction_cost: float = 0.001
    slippage_model: str = "percentage"
    market_impact: bool = True


@dataclass
class TradingState:
    """Represents the current state of the trading environment"""

    # Market data
    price: float
    returns: float
    volatility: float
    volume: float

    # Technical indicators
    rsi: float
    macd: float
    bollinger_position: float

    # Portfolio state
    cash: float
    position: float
    portfolio_value: float
    unrealized_pnl: float

    # Market regime
    regime: str  # "bull", "bear", "sideways"

    # Time features
    hour_of_day: int
    day_of_week: int

    def to_array(self) -> np.ndarray:
        """Convert state to numpy array for ML models"""
        return np.array([
            self.price,
            self.returns,
            self.volatility,
            self.volume,
            self.rsi,
            self.macd,
            self.bollinger_position,
            self.cash,
            self.position,
            self.portfolio_value,
            self.unrealized_pnl,
            1 if self.regime == "bull" else 0,
            1 if self.regime == "bear" else 0,
            self.hour_of_day / 24.0,  # Normalize
            self.day_of_week / 7.0   # Normalize
        ])


@dataclass
class TradingAction:
    """Represents trading actions"""

    action_type: str  # "buy", "sell", "hold"
    position_size: float  # 0.0 to 1.0

    @classmethod
    def from_index(cls, action_idx: int, n_position_sizes: int = 10) -> TradingAction:
        """Convert action index to TradingAction"""
        action_types = ["hold", "buy", "sell"]
        action_type = action_types[action_idx // n_position_sizes]
        position_size = (action_idx % n_position_sizes) / (n_position_sizes - 1)
        return cls(action_type=action_type, position_size=position_size)

    def to_index(self, n_position_sizes: int = 10) -> int:
        """Convert TradingAction to index"""
        action_types = ["hold", "buy", "sell"]
        action_idx = action_types.index(self.action_type)
        size_idx = int(self.position_size * (n_position_sizes - 1))
        return action_idx * n_position_sizes + size_idx


class QTable:
    """Q-table implementation with discretization"""

    def __init__(self, state_bins: Dict[str, int], n_actions: int):
        self.state_bins = state_bins
        self.n_actions = n_actions
        self.q_table = defaultdict(lambda: np.zeros(n_actions))

        # Discretization ranges (will be set during initialization)
        self.state_ranges = {}

    def discretize_state(self, state: TradingState) -> Tuple:
        """Discretize continuous state into discrete bins"""
        discretized = []

        state_dict = {
            'price': state.price,
            'returns': state.returns,
            'volatility': state.volatility,
            'volume': state.volume,
            'rsi': state.rsi,
            'macd': state.macd,
            'bollinger_position': state.bollinger_position,
            'cash': state.cash,
            'position': state.position,
            'portfolio_value': state.portfolio_value,
            'unrealized_pnl': state.unrealized_pnl,
            'hour_of_day': state.hour_of_day,
            'day_of_week': state.day_of_week
        }

        for feature, value in state_dict.items():
            if feature in self.state_ranges:
                min_val, max_val = self.state_ranges[feature]
                bins = np.linspace(min_val, max_val, self.state_bins.get(feature, 10) + 1)
                discretized_val = np.digitize(value, bins) - 1
                discretized_val = np.clip(discretized_val, 0, self.state_bins[feature] - 1)
                discretized.append(discretized_val)
            else:
                discretized.append(0)  # Default bin

        return tuple(discretized)

    def update_ranges(self, states: List[TradingState]):
        """Update discretization ranges based on observed states"""
        if not states:
            return

        state_arrays = [state.to_array() for state in states]
        state_matrix = np.array(state_arrays)

        feature_names = [
            'price', 'returns', 'volatility', 'volume', 'rsi', 'macd', 'bollinger_position',
            'cash', 'position', 'portfolio_value', 'unrealized_pnl', 'regime_bull',
            'regime_bear', 'hour_of_day', 'day_of_week'
        ]

        for i, feature in enumerate(feature_names):
            if feature in self.state_bins:
                values = state_matrix[:, i]
                self.state_ranges[feature] = (np.min(values), np.max(values))

    def get_q_value(self, state: TradingState, action_idx: int) -> float:
        """Get Q-value for state-action pair"""
        discrete_state = self.discretize_state(state)
        return self.q_table[discrete_state][action_idx]

    def set_q_value(self, state: TradingState, action_idx: int, value: float):
        """Set Q-value for state-action pair"""
        discrete_state = self.discretize_state(state)
        self.q_table[discrete_state][action_idx] = value

    def get_best_action(self, state: TradingState) -> int:
        """Get best action for given state"""
        discrete_state = self.discretize_state(state)
        return np.argmax(self.q_table[discrete_state])


class LinearQApproximation:
    """Linear function approximation for Q-values"""

    def __init__(self, n_features: int, n_actions: int, learning_rate: float = 0.01):
        self.n_features = n_features
        self.n_actions = n_actions
        self.learning_rate = learning_rate

        # Initialize weights for each action
        self.weights = np.random.normal(0, 0.1, (n_actions, n_features + 1))  # +1 for bias

    def featurize_state(self, state: TradingState) -> np.ndarray:
        """Convert state to feature vector"""
        features = state.to_array()
        # Add bias term
        return np.concatenate([[1.0], features])

    def predict(self, state: TradingState) -> np.ndarray:
        """Predict Q-values for all actions"""
        features = self.featurize_state(state)
        return np.dot(self.weights, features)

    def update(self, state: TradingState, action: int, target: float):
        """Update weights using TD learning"""
        features = self.featurize_state(state)
        prediction = np.dot(self.weights[action], features)
        error = target - prediction

        # Update weights
        self.weights[action] += self.learning_rate * error * features

    def get_best_action(self, state: TradingState) -> int:
        """Get best action based on current approximation"""
        q_values = self.predict(state)
        return np.argmax(q_values)


class ExperienceReplay:
    """Experience replay buffer for stable learning"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.position = 0

    def push(self, state: TradingState, action: int, reward: float,
             next_state: TradingState, done: bool):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> List[Tuple]:
        """Sample random batch from buffer"""
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[idx] for idx in indices]

    def __len__(self) -> int:
        return len(self.buffer)


class TradingRewardFunction:
    """Reward function specifically designed for trading"""

    def __init__(self, config: QLearningConfig):
        self.config = config

    def calculate_reward(self, state: TradingState, action: TradingAction,
                        next_state: TradingState, done: bool) -> float:
        """Calculate reward for state-action-next_state transition"""

        reward = 0.0

        # Profit/Loss reward
        pnl_change = next_state.unrealized_pnl - state.unrealized_pnl
        reward += pnl_change * 100  # Scale up for learning

        # Risk-adjusted reward (Sharpe-like)
        if next_state.volatility > 0:
            risk_adjusted_return = pnl_change / next_state.volatility
            reward += risk_adjusted_return * 10

        # Transaction cost penalty
        if action.action_type in ["buy", "sell"] and action.position_size > 0:
            transaction_cost = abs(action.position_size) * state.price * self.config.transaction_cost
            reward -= transaction_cost * 100  # Penalty for trading

        # Risk management penalties
        portfolio_value_change = next_state.portfolio_value - state.portfolio_value
        if portfolio_value_change < 0:  # Loss
            loss_penalty = abs(portfolio_value_change) / state.portfolio_value
            reward -= loss_penalty * 50  # Extra penalty for losses

        # Position size incentives (prefer moderate positions)
        optimal_position = 0.5  # Optimal position size
        position_penalty = abs(action.position_size - optimal_position) * 10
        reward -= position_penalty

        # Market timing bonus
        if action.action_type == "buy" and next_state.returns > 0:
            reward += 20  # Bonus for correct timing
        elif action.action_type == "sell" and next_state.returns < 0:
            reward += 20  # Bonus for correct timing

        # Drawdown penalty
        if next_state.portfolio_value < state.portfolio_value * (1 - self.config.max_drawdown_limit):
            reward -= 100  # Heavy penalty for excessive drawdown

        return reward


class TabularQLearning:
    """Tabular Q-learning implementation for trading"""

    def __init__(self, config: QLearningConfig):
        self.config = config
        self.q_table = QTable(
            state_bins={
                'price': 20, 'returns': 10, 'volatility': 10, 'volume': 10,
                'rsi': 10, 'macd': 10, 'bollinger_position': 10,
                'cash': 15, 'position': 10, 'portfolio_value': 15,
                'unrealized_pnl': 10, 'hour_of_day': 6, 'day_of_week': 5
            },
            n_actions=30  # 3 actions (hold/buy/sell) x 10 position sizes
        )

        self.reward_function = TradingRewardFunction(config)
        self.exploration_rate = config.exploration_rate

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.q_table_updates = 0

    def select_action(self, state: TradingState, training: bool = True) -> TradingAction:
        """Select action using epsilon-greedy policy"""

        if training and np.random.random() < self.exploration_rate:
            # Random action
            action_idx = np.random.randint(30)
        else:
            # Best action
            action_idx = self.q_table.get_best_action(state)

        return TradingAction.from_index(action_idx)

    def update_q_table(self, state: TradingState, action: TradingAction,
                      reward: float, next_state: TradingState, done: bool):
        """Update Q-table using Q-learning update rule"""

        action_idx = action.to_index()

        # Current Q-value
        current_q = self.q_table.get_q_value(state, action_idx)

        # Next best Q-value
        if done:
            next_max_q = 0.0
        else:
            next_action_idx = self.q_table.get_best_action(next_state)
            next_max_q = self.q_table.get_q_value(next_state, next_action_idx)

        # Q-learning update
        target_q = reward + self.config.discount_factor * next_max_q
        new_q = current_q + self.config.learning_rate * (target_q - current_q)

        # Update Q-table
        self.q_table.set_q_value(state, action_idx, new_q)
        self.q_table_updates += 1

    def train_episode(self, env) -> Tuple[List[float], int]:
        """Train for one episode"""

        state = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False

        while not done and steps < self.config.max_steps_per_episode:
            # Select and execute action
            action = self.select_action(state, training=True)
            next_state, reward, done, info = env.step(action)

            # Calculate trading-specific reward
            reward = self.reward_function.calculate_reward(state, action, next_state, done)

            # Update Q-table
            self.update_q_table(state, action, reward, next_state, done)

            episode_reward += reward
            state = next_state
            steps += 1

        # Decay exploration rate
        self.exploration_rate = max(
            self.config.min_exploration_rate,
            self.exploration_rate * self.config.exploration_decay
        )

        return episode_reward, steps

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the Q-learning agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting Q-learning training for {n_episodes} episodes...")

        for episode in range(n_episodes):
            episode_reward, episode_length = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)

            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(self.episode_rewards[-100:])
                avg_length = np.mean(self.episode_lengths[-100:])
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}, "
                      f"Exploration Rate = {self.exploration_rate:.3f}")

            # Check for convergence
            if len(self.episode_rewards) >= self.config.early_stopping_patience:
                recent_rewards = self.episode_rewards[-self.config.early_stopping_patience:]
                if np.std(recent_rewards) < self.config.convergence_threshold:
                    print(f"Converged after {episode + 1} episodes")
                    break

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "final_exploration_rate": self.exploration_rate,
            "q_table_updates": self.q_table_updates
        }

    def predict(self, state: TradingState) -> TradingAction:
        """Predict best action for given state (no exploration)"""
        return self.select_action(state, training=False)


class ApproximateQLearning:
    """Q-learning with function approximation"""

    def __init__(self, config: QLearningConfig):
        self.config = config
        self.approximator = LinearQApproximation(
            n_features=15,  # State features
            n_actions=30,   # Action space
            learning_rate=config.learning_rate
        )

        self.reward_function = TradingRewardFunction(config)
        self.replay_buffer = ExperienceReplay(config.replay_buffer_size)
        self.exploration_rate = config.exploration_rate

        # Target network for stability
        self.target_approximator = LinearQApproximation(
            n_features=15, n_actions=30, learning_rate=config.learning_rate
        )
        self.update_target_network()

        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.updates_count = 0

    def update_target_network(self):
        """Update target network weights"""
        self.target_approximator.weights = self.approximator.weights.copy()

    def select_action(self, state: TradingState, training: bool = True) -> TradingAction:
        """Select action using epsilon-greedy policy"""

        if training and np.random.random() < self.exploration_rate:
            # Random action
            action_idx = np.random.randint(30)
        else:
            # Best action from approximator
            action_idx = self.approximator.get_best_action(state)

        return TradingAction.from_index(action_idx)

    def store_experience(self, state: TradingState, action: TradingAction,
                        reward: float, next_state: TradingState, done: bool):
        """Store experience in replay buffer"""
        action_idx = action.to_index()
        self.replay_buffer.push(state, action_idx, reward, next_state, done)

    def train_on_batch(self):
        """Train on a batch of experiences"""

        if len(self.replay_buffer) < self.config.batch_size:
            return

        # Sample batch
        batch = self.replay_buffer.sample(self.config.batch_size)

        for state, action_idx, reward, next_state, done in batch:
            # Current Q-value
            current_q = self.approximator.predict(state)[action_idx]

            # Target Q-value
            if done:
                target_q = reward
            else:
                next_q_values = self.target_approximator.predict(next_state)
                target_q = reward + self.config.discount_factor * np.max(next_q_values)

            # Update approximator
            self.approximator.update(state, action_idx, target_q)
            self.updates_count += 1

        # Update target network periodically
        if self.updates_count % self.config.target_update_frequency == 0:
            self.update_target_network()

    def train_episode(self, env) -> Tuple[float, int]:
        """Train for one episode with experience replay"""

        state = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False

        while not done and steps < self.config.max_steps_per_episode:
            # Select and execute action
            action = self.select_action(state, training=True)
            next_state, raw_reward, done, info = env.step(action)

            # Calculate trading-specific reward
            reward = self.reward_function.calculate_reward(state, action, next_state, done)

            # Store experience
            self.store_experience(state, action, reward, next_state, done)

            # Train on batch
            self.train_on_batch()

            episode_reward += reward
            state = next_state
            steps += 1

        # Decay exploration rate
        self.exploration_rate = max(
            self.config.min_exploration_rate,
            self.exploration_rate * self.config.exploration_decay
        )

        return episode_reward, steps

    def train(self, env, n_episodes: Optional[int] = None) -> Dict[str, List]:
        """Train the approximate Q-learning agent"""

        n_episodes = n_episodes or self.config.max_episodes

        print(f"Starting approximate Q-learning training for {n_episodes} episodes...")

        for episode in range(n_episodes):
            episode_reward, episode_length = self.train_episode(env)

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)

            if (episode + 1) % 50 == 0:
                avg_reward = np.mean(self.episode_rewards[-50:])
                avg_length = np.mean(self.episode_lengths[-50:])
                print(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, "
                      f"Avg Length = {avg_length:.1f}, "
                      f"Exploration Rate = {self.exploration_rate:.3f}, "
                      f"Buffer Size = {len(self.replay_buffer)}")

        return {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "final_exploration_rate": self.exploration_rate,
            "updates_count": self.updates_count,
            "buffer_size": len(self.replay_buffer)
        }

    def predict(self, state: TradingState) -> TradingAction:
        """Predict best action for given state"""
        return self.select_action(state, training=False)


# Trading Environment Interface
class TradingEnvironment:
    """Abstract base class for trading environments"""

    @abstractmethod
    def reset(self) -> TradingState:
        """Reset environment and return initial state"""
        pass

    @abstractmethod
    def step(self, action: TradingAction) -> Tuple[TradingState, float, bool, Dict]:
        """Execute action and return next state, reward, done, info"""
        pass

    @abstractmethod
    def get_available_actions(self) -> List[TradingAction]:
        """Get list of available actions"""
        pass


class HistoricalTradingEnvironment(TradingEnvironment):
    """Trading environment using historical data"""

    def __init__(self, data: pd.DataFrame, initial_cash: float = 10000.0):
        self.data = data.copy()
        self.initial_cash = initial_cash
        self.current_step = 0
        self.cash = initial_cash
        self.position = 0
        self.trades = []

        # Pre-calculate indicators
        self._prepare_indicators()

    def _prepare_indicators(self):
        """Calculate technical indicators"""
        # RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = self.data['close'].ewm(span=12).mean()
        ema26 = self.data['close'].ewm(span=26).mean()
        self.data['macd'] = ema12 - ema26

        # Bollinger Bands
        sma20 = self.data['close'].rolling(window=20).mean()
        std20 = self.data['close'].rolling(window=20).std()
        self.data['bollinger_position'] = (self.data['close'] - sma20) / (2 * std20)

        # Volatility
        self.data['volatility'] = self.data['close'].pct_change().rolling(window=20).std()

        # Fill NaN values
        self.data = self.data.fillna(method='bfill').fillna(method='ffill').fillna(0)

    def reset(self) -> TradingState:
        """Reset environment"""
        self.current_step = 0
        self.cash = self.initial_cash
        self.position = 0
        self.trades = []
        return self._get_current_state()

    def step(self, action: TradingAction) -> Tuple[TradingState, float, bool, Dict]:
        """Execute trading action"""

        current_price = self.data.iloc[self.current_step]['close']
        next_price = self.data.iloc[min(self.current_step + 1, len(self.data) - 1)]['close']

        # Execute trade
        if action.action_type == "buy" and self.cash > 0:
            # Buy with position size
            max_buy = self.cash / current_price
            shares_to_buy = max_buy * action.position_size
            cost = shares_to_buy * current_price * 1.001  # Include transaction cost

            if cost <= self.cash:
                self.position += shares_to_buy
                self.cash -= cost
                self.trades.append({
                    'step': self.current_step,
                    'type': 'buy',
                    'shares': shares_to_buy,
                    'price': current_price,
                    'cost': cost
                })

        elif action.action_type == "sell" and self.position > 0:
            # Sell with position size
            shares_to_sell = self.position * action.position_size
            revenue = shares_to_sell * current_price * 0.999  # Include transaction cost

            self.position -= shares_to_sell
            self.cash += revenue
            self.trades.append({
                'step': self.current_step,
                'type': 'sell',
                'shares': shares_to_sell,
                'price': current_price,
                'revenue': revenue
            })

        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1

        next_state = self._get_current_state()

        # Simple reward based on portfolio value change
        portfolio_value = self.cash + self.position * next_price
        reward = portfolio_value - self.initial_cash

        info = {
            'portfolio_value': portfolio_value,
            'trades_executed': len(self.trades),
            'current_price': current_price
        }

        return next_state, reward, done, info

    def _get_current_state(self) -> TradingState:
        """Get current trading state"""
        row = self.data.iloc[self.current_step]

        portfolio_value = self.cash + self.position * row['close']
        unrealized_pnl = portfolio_value - self.initial_cash

        # Determine market regime
        returns = row.get('close', 0) / row.get('open', 1) - 1
        if returns > 0.01:
            regime = "bull"
        elif returns < -0.01:
            regime = "bear"
        else:
            regime = "sideways"

        return TradingState(
            price=row['close'],
            returns=returns,
            volatility=row.get('volatility', 0),
            volume=row.get('volume', 1000),
            rsi=row.get('rsi', 50),
            macd=row.get('macd', 0),
            bollinger_position=row.get('bollinger_position', 0),
            cash=self.cash,
            position=self.position,
            portfolio_value=portfolio_value,
            unrealized_pnl=unrealized_pnl,
            regime=regime,
            hour_of_day=self.current_step % 24,
            day_of_week=self.current_step % 7
        )

    def get_available_actions(self) -> List[TradingAction]:
        """Get all possible actions"""
        actions = []
        for action_type in ["hold", "buy", "sell"]:
            for size in np.linspace(0, 1, 10):
                actions.append(TradingAction(action_type, size))
        return actions


def create_q_learning_trader(config: Optional[QLearningConfig] = None) -> TabularQLearning:
    """Factory function for Q-learning trader"""
    if config is None:
        config = QLearningConfig()
    return TabularQLearning(config)


def create_approximate_q_learning_trader(config: Optional[QLearningConfig] = None) -> ApproximateQLearning:
    """Factory function for approximate Q-learning trader"""
    if config is None:
        config = QLearningConfig()
    return ApproximateQLearning(config)


def train_q_learning_agent(data: pd.DataFrame, config: Optional[QLearningConfig] = None,
                          agent_type: str = "tabular") -> Union[TabularQLearning, ApproximateQLearning]:
    """Train a Q-learning agent on historical data"""

    if config is None:
        config = QLearningConfig()

    # Create environment
    env = HistoricalTradingEnvironment(data)

    # Create agent
    if agent_type == "tabular":
        agent = TabularQLearning(config)
    elif agent_type == "approximate":
        agent = ApproximateQLearning(config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    # Train agent
    training_stats = agent.train(env)

    print(f"Training completed: {training_stats}")

    return agent


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=1000, freq="1H")
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.0001, 0.01, 1000)))
    volumes = np.random.normal(1000, 200, 1000)

    data = pd.DataFrame({
        'open': prices * 0.99,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': volumes
    }, index=dates)

    # Test Q-learning
    config = QLearningConfig(max_episodes=10)  # Short training for demo
    agent = train_q_learning_agent(data, config, agent_type="tabular")

    # Test prediction
    test_state = TradingState(
        price=100.0, returns=0.01, volatility=0.02, volume=1000,
        rsi=60, macd=0.5, bollinger_position=0.1,
        cash=5000, position=50, portfolio_value=10000, unrealized_pnl=0,
        regime="bull", hour_of_day=10, day_of_week=1
    )

    action = agent.predict(test_state)
    print(f"Predicted action: {action.action_type} with size {action.position_size:.2f}")
