"""
Multi-Agent Systems for Trading
===============================

This module implements multi-agent reinforcement learning systems specifically designed for algorithmic trading.
Includes cooperative and competitive agent frameworks, market simulation, and collective intelligence.

Key Features:
- Multi-agent reinforcement learning (MARL) frameworks
- Cooperative and competitive trading agents
- Market microstructure simulation
- Collective intelligence and swarm trading
- Agent communication and coordination
- Risk-sharing and portfolio optimization
- Evolutionary agent populations
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Neural network dependencies
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.distributions import Normal, Categorical
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

# Import existing modules
try:
    from .q_learning import QLearningConfig, TradingState, TradingAction
    from .dqn_trading import DQNConfig, DQNTrader
    from .policy_gradients import PolicyGradientConfig, PPOAgent
except ImportError:
    # Fallback for standalone testing
    QLearningConfig = None
    TradingState = None
    TradingAction = None
    DQNConfig = None
    DQNTrader = None
    PolicyGradientConfig = None
    PPOAgent = None


@dataclass
class MultiAgentConfig:
    """Configuration for multi-agent systems"""

    # Agent population
    n_agents: int = 10
    agent_types: List[str] = field(default_factory=lambda: ["q_learning", "dqn", "ppo"])
    agent_distribution: Dict[str, float] = field(default_factory=lambda: {
        "q_learning": 0.4, "dqn": 0.4, "ppo": 0.2
    })

    # Communication and coordination
    communication_enabled: bool = True
    communication_range: float = 0.1  # Fraction of total capital
    coordination_mechanism: str = "consensus"  # "consensus", "auction", "voting"
    information_sharing: bool = True

    # Market simulation
    market_impact_model: str = "collective"  # "individual", "collective", "none"
    price_impact_decay: float = 0.9
    liquidity_model: str = "endogenous"

    # Risk management
    systemic_risk_threshold: float = 0.1
    correlation_penalty: float = 0.1
    diversification_bonus: float = 0.05

    # Evolution and adaptation
    evolution_enabled: bool = True
    mutation_rate: float = 0.1
    crossover_rate: float = 0.2
    selection_pressure: float = 2.0

    # Collective intelligence
    swarm_intelligence: bool = True
    pheromone_decay: float = 0.95
    pheromone_strength: float = 1.0

    # Training parameters
    max_episodes: int = 1000
    episode_length: int = 1000
    evaluation_frequency: int = 50

    # Hardware and parallelization
    parallel_training: bool = True
    n_worker_processes: int = 4


@dataclass
class AgentState:
    """State of an individual agent"""

    agent_id: int
    position: float
    cash: float
    portfolio_value: float
    fitness_score: float
    strategy_type: str
    last_action: Optional[TradingAction] = None
    communication_history: List[Dict] = field(default_factory=list)

    def to_array(self) -> np.ndarray:
        """Convert agent state to array"""
        return np.array([
            self.position,
            self.cash,
            self.portfolio_value,
            self.fitness_score,
            1 if self.strategy_type == "q_learning" else 0,
            1 if self.strategy_type == "dqn" else 0,
            1 if self.strategy_type == "ppo" else 0
        ])


@dataclass
class MarketState:
    """Global market state for multi-agent system"""

    price: float
    volume: float
    bid_ask_spread: float
    market_depth: Dict[str, float]  # Level 1, 2, 3 depths
    agent_positions: Dict[int, float]  # Agent ID -> position
    total_volume: float
    volatility: float
    trend_strength: float

    def to_array(self) -> np.ndarray:
        """Convert market state to array"""
        depths = [self.market_depth.get(f'level_{i}', 0) for i in range(1, 4)]
        return np.array([
            self.price,
            self.volume,
            self.bid_ask_spread,
            self.total_volume,
            self.volatility,
            self.trend_strength
        ] + depths)


class CommunicationProtocol:
    """Communication protocol for agent coordination"""

    def __init__(self, config: MultiAgentConfig):
        self.config = config
        self.message_queue = deque(maxlen=1000)
        self.agent_reputations = defaultdict(lambda: 1.0)

    def send_message(self, sender_id: int, receiver_id: int, message: Dict):
        """Send message between agents"""
        if not self.config.communication_enabled:
            return

        message_entry = {
            'sender': sender_id,
            'receiver': receiver_id,
            'timestamp': time.time(),
            'content': message,
            'reputation_weight': self.agent_reputations[sender_id]
        }
        self.message_queue.append(message_entry)

    def broadcast_message(self, sender_id: int, message: Dict):
        """Broadcast message to all agents"""
        for receiver_id in range(self.config.n_agents):
            if receiver_id != sender_id:
                self.send_message(sender_id, receiver_id, message)

    def get_messages_for_agent(self, agent_id: int) -> List[Dict]:
        """Get all messages for a specific agent"""
        return [msg for msg in self.message_queue if msg['receiver'] == agent_id]

    def update_reputation(self, agent_id: int, performance: float):
        """Update agent reputation based on performance"""
        self.agent_reputations[agent_id] = 0.9 * self.agent_reputations[agent_id] + 0.1 * performance


class ConsensusMechanism:
    """Consensus-based decision making for agent coordination"""

    def __init__(self, config: MultiAgentConfig):
        self.config = config
        self.opinions = {}
        self.confidence_levels = defaultdict(lambda: 1.0)

    def collect_opinions(self, agent_states: Dict[int, AgentState]) -> Dict[str, float]:
        """Collect trading opinions from all agents"""

        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        total_confidence = 0

        for agent_id, state in agent_states.items():
            confidence = self.confidence_levels[agent_id]

            if state.last_action:
                if state.last_action.action_type == "buy":
                    buy_signals += confidence
                elif state.last_action.action_type == "sell":
                    sell_signals += confidence
                else:
                    hold_signals += confidence

            total_confidence += confidence

        if total_confidence == 0:
            return {"buy": 0.33, "sell": 0.33, "hold": 0.34}

        return {
            "buy": buy_signals / total_confidence,
            "sell": sell_signals / total_confidence,
            "hold": hold_signals / total_confidence
        }

    def reach_consensus(self, opinions: Dict[str, float], threshold: float = 0.6) -> Optional[str]:
        """Determine if consensus is reached"""
        max_opinion = max(opinions.values())
        if max_opinion >= threshold:
            return max(opinions.keys(), key=lambda k: opinions[k])
        return None

    def update_confidence(self, agent_id: int, correctness: float):
        """Update agent confidence based on prediction correctness"""
        self.confidence_levels[agent_id] = 0.95 * self.confidence_levels[agent_id] + 0.05 * correctness


class MarketSimulator:
    """Multi-agent market simulator"""

    def __init__(self, config: MultiAgentConfig, initial_price: float = 100.0):
        self.config = config
        self.price = initial_price
        self.price_history = [initial_price]
        self.volume_history = []
        self.agent_orders = defaultdict(list)
        self.market_depth = {'level_1': 1000, 'level_2': 2000, 'level_3': 3000}
        self.spread = 0.01  # 1 cent spread

        # Market impact tracking
        self.cumulative_market_impact = 0.0
        self.last_agent_actions = defaultdict(lambda: None)

    def process_agent_orders(self, agent_actions: Dict[int, TradingAction]) -> Dict[str, float]:
        """Process orders from all agents and update market"""

        buy_orders = []
        sell_orders = []

        # Collect orders
        for agent_id, action in agent_actions.items():
            if action.action_type == "buy":
                buy_orders.append((agent_id, action.position_size))
            elif action.action_type == "sell":
                sell_orders.append((agent_id, action.position_size))

        # Calculate market impact
        total_buy_volume = sum(size for _, size in buy_orders)
        total_sell_volume = sum(size for _, size in sell_orders)
        net_order_flow = total_buy_volume - total_sell_volume

        # Update market price based on order flow
        if self.config.market_impact_model == "collective":
            price_impact = net_order_flow * 0.001  # 0.1% impact per unit
            self.cumulative_market_impact = (self.cumulative_market_impact * self.config.price_impact_decay +
                                           price_impact)
            self.price *= (1 + self.cumulative_market_impact)
        elif self.config.market_impact_model == "individual":
            # Individual impact model would be more complex
            pass

        # Update market depth
        self.market_depth['level_1'] = max(100, self.market_depth['level_1'] +
                                         100 * (total_buy_volume - total_sell_volume))

        # Add some random noise
        self.price *= np.random.normal(1.0, 0.001)

        # Ensure price stays positive
        self.price = max(0.01, self.price)

        # Update history
        self.price_history.append(self.price)
        self.volume_history.append(total_buy_volume + total_sell_volume)

        return {
            'new_price': self.price,
            'price_change': self.price - self.price_history[-2] if len(self.price_history) > 1 else 0,
            'total_volume': total_buy_volume + total_sell_volume,
            'buy_volume': total_buy_volume,
            'sell_volume': total_sell_volume,
            'market_impact': self.cumulative_market_impact
        }

    def get_market_state(self) -> MarketState:
        """Get current market state"""
        return MarketState(
            price=self.price,
            volume=self.volume_history[-1] if self.volume_history else 0,
            bid_ask_spread=self.spread,
            market_depth=self.market_depth.copy(),
            agent_positions={},  # To be filled by caller
            total_volume=sum(self.volume_history[-100:]) if self.volume_history else 0,
            volatility=np.std(self.price_history[-20:]) / np.mean(self.price_history[-20:]) if len(self.price_history) >= 20 else 0,
            trend_strength=self._calculate_trend_strength()
        )

    def _calculate_trend_strength(self) -> float:
        """Calculate trend strength indicator"""
        if len(self.price_history) < 20:
            return 0.0

        recent_prices = np.array(self.price_history[-20:])
        slope, _, _, _, _ = stats.linregress(range(20), recent_prices)
        return slope / np.mean(recent_prices)  # Normalized slope


class TradingAgent:
    """Individual trading agent with different strategies"""

    def __init__(self, agent_id: int, strategy_type: str, config: MultiAgentConfig):
        self.agent_id = agent_id
        self.strategy_type = strategy_type
        self.config = config

        # Agent state
        self.cash = 10000.0
        self.position = 0.0
        self.portfolio_value = self.cash
        self.fitness_score = 0.0

        # Initialize specific strategy
        self._initialize_strategy()

        # Communication
        self.message_buffer = deque(maxlen=100)
        self.neighbors = set()

    def _initialize_strategy(self):
        """Initialize the specific trading strategy"""

        if self.strategy_type == "q_learning":
            from .q_learning import TabularQLearning, QLearningConfig
            strategy_config = QLearningConfig(max_episodes=100)
            self.strategy = TabularQLearning(strategy_config)

        elif self.strategy_type == "dqn":
            from .dqn_trading import DQNTrader, DQNConfig
            strategy_config = DQNConfig(max_episodes=100)
            self.strategy = DQNTrader(strategy_config, state_dim=15, action_dim=30)

        elif self.strategy_type == "ppo":
            from .policy_gradients import PPOAgent, PolicyGradientConfig
            strategy_config = PolicyGradientConfig(max_episodes=100)
            self.strategy = PPOAgent(strategy_config, state_dim=15, action_dim=30)

        else:
            raise ValueError(f"Unknown strategy type: {self.strategy_type}")

    def observe_state(self, market_state: MarketState, agent_states: Dict[int, AgentState]) -> TradingState:
        """Observe the current state and create trading state"""

        # Create local trading state
        trading_state = TradingState(
            price=market_state.price,
            returns=market_state.price / self.price_history[-1] - 1 if hasattr(self, 'price_history') and self.price_history else 0,
            volatility=market_state.volatility,
            volume=market_state.volume,
            rsi=50.0,  # Simplified
            macd=0.0,  # Simplified
            bollinger_position=0.0,  # Simplified
            cash=self.cash,
            position=self.position,
            portfolio_value=self.portfolio_value,
            unrealized_pnl=self.portfolio_value - 10000.0,
            regime="sideways",  # Simplified
            hour_of_day=12,  # Simplified
            day_of_week=1     # Simplified
        )

        # Update price history
        if not hasattr(self, 'price_history'):
            self.price_history = deque(maxlen=100)
        self.price_history.append(market_state.price)

        return trading_state

    def decide_action(self, trading_state: TradingState, consensus_opinion: Optional[Dict] = None) -> TradingAction:
        """Decide on trading action"""

        # Get base action from strategy
        if hasattr(self.strategy, 'predict'):
            action_idx = self.strategy.predict(trading_state.to_array())
            action = TradingAction.from_index(action_idx)
        else:
            # Fallback random action
            action = TradingAction("hold", 0.0)

        # Incorporate consensus if available
        if consensus_opinion and self.config.coordination_mechanism == "consensus":
            consensus_action = max(consensus_opinion.keys(), key=lambda k: consensus_opinion[k])
            if consensus_opinion[consensus_action] > 0.6:  # Strong consensus
                action.action_type = consensus_action

        return action

    def update_fitness(self, reward: float):
        """Update agent fitness score"""
        self.fitness_score = 0.95 * self.fitness_score + 0.05 * reward

    def communicate(self, communication_protocol: CommunicationProtocol,
                   market_state: MarketState, agent_states: Dict[int, AgentState]):
        """Send communication messages to other agents"""

        if not self.config.communication_enabled:
            return

        # Send position and prediction information
        message = {
            'position': self.position,
            'portfolio_value': self.portfolio_value,
            'fitness': self.fitness_score,
            'market_prediction': 'bull' if market_state.trend_strength > 0 else 'bear'
        }

        communication_protocol.broadcast_message(self.agent_id, message)

    def receive_messages(self, communication_protocol: CommunicationProtocol):
        """Receive and process messages from other agents"""

        messages = communication_protocol.get_messages_for_agent(self.agent_id)
        self.message_buffer.extend(messages)

        # Process recent messages (last 10)
        recent_messages = list(self.message_buffer)[-10:]

        # Update neighbors based on communication
        self.neighbors = set(msg['sender'] for msg in recent_messages)

    def mutate(self, mutation_rate: float):
        """Apply mutation to agent parameters"""
        if np.random.random() < mutation_rate:
            # Randomly adjust some parameters
            if hasattr(self.strategy, 'exploration_rate'):
                self.strategy.exploration_rate *= np.random.normal(1.0, 0.1)


class MultiAgentSystem:
    """Multi-agent trading system"""

    def __init__(self, config: MultiAgentConfig):
        self.config = config

        # Initialize components
        self.market_simulator = MarketSimulator(config)
        self.communication_protocol = CommunicationProtocol(config)
        self.consensus_mechanism = ConsensusMechanism(config)

        # Initialize agents
        self.agents = self._initialize_agents()

        # System state
        self.episode_count = 0
        self.system_performance = []

    def _initialize_agents(self) -> Dict[int, TradingAgent]:
        """Initialize agent population"""

        agents = {}

        for i in range(self.config.n_agents):
            # Select strategy type based on distribution
            strategy_type = np.random.choice(
                list(self.config.agent_distribution.keys()),
                p=list(self.config.agent_distribution.values())
            )

            agent = TradingAgent(i, strategy_type, self.config)
            agents[i] = agent

        return agents

    def step(self) -> Dict[str, Any]:
        """Execute one step of the multi-agent system"""

        # Get current market state
        market_state = self.market_simulator.get_market_state()
        market_state.agent_positions = {aid: agent.position for aid, agent in self.agents.items()}

        # Create agent states
        agent_states = {}
        for aid, agent in self.agents.items():
            agent_states[aid] = AgentState(
                agent_id=aid,
                position=agent.position,
                cash=agent.cash,
                portfolio_value=agent.portfolio_value,
                fitness_score=agent.fitness_score,
                strategy_type=agent.strategy_type
            )

        # Communication phase
        for agent in self.agents.values():
            agent.receive_messages(self.communication_protocol)
            agent.communicate(self.communication_protocol, market_state, agent_states)

        # Decision phase
        consensus_opinion = self.consensus_mechanism.collect_opinions(agent_states)
        agent_actions = {}

        for aid, agent in self.agents.items():
            trading_state = agent.observe_state(market_state, agent_states)
            action = agent.decide_action(trading_state, consensus_opinion)
            agent_actions[aid] = action
            agent_states[aid].last_action = action

        # Market update phase
        market_update = self.market_simulator.process_agent_orders(agent_actions)

        # Update agents
        total_system_value = 0
        for aid, agent in self.agents.items():
            action = agent_actions[aid]

            # Calculate individual reward
            old_value = agent.portfolio_value
            # Update position and cash based on action and market
            agent.portfolio_value = agent.cash + agent.position * market_update['new_price']
            reward = agent.portfolio_value - old_value

            agent.update_fitness(reward)
            total_system_value += agent.portfolio_value

        # Update consensus mechanism
        market_direction = "bull" if market_update['price_change'] > 0 else "bear"
        consensus_correct = consensus_opinion.get(market_direction, 0) > 0.5
        for aid in self.agents.keys():
            self.consensus_mechanism.update_confidence(aid, 1.0 if consensus_correct else 0.0)

        # Update communication reputations
        for aid, agent in self.agents.items():
            self.communication_protocol.update_reputation(aid, agent.fitness_score)

        self.episode_count += 1

        return {
            'market_update': market_update,
            'agent_actions': agent_actions,
            'consensus_opinion': consensus_opinion,
            'total_system_value': total_system_value,
            'agent_fitnesses': {aid: agent.fitness_score for aid, agent in self.agents.items()}
        }

    def evolve_population(self):
        """Evolve agent population using genetic algorithms"""

        if not self.config.evolution_enabled:
            return

        # Sort agents by fitness
        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1].fitness_score, reverse=True)

        # Keep top performers
        n_elite = int(0.2 * self.config.n_agents)  # Top 20%
        elite_agents = dict(sorted_agents[:n_elite])

        # Create new population
        new_agents = elite_agents.copy()

        # Generate offspring through crossover and mutation
        while len(new_agents) < self.config.n_agents:
            # Select parents (tournament selection)
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            # Crossover
            if np.random.random() < self.config.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1

            # Mutation
            child.mutate(self.config.mutation_rate)

            new_agents[len(new_agents)] = child

        self.agents = new_agents

    def _tournament_selection(self) -> TradingAgent:
        """Tournament selection for genetic algorithm"""
        tournament_size = 3
        candidates = np.random.choice(list(self.agents.values()), tournament_size, replace=False)
        return max(candidates, key=lambda x: x.fitness_score)

    def _crossover(self, parent1: TradingAgent, parent2: TradingAgent) -> TradingAgent:
        """Crossover between two parent agents"""
        # Create child with mixed parameters
        child_id = max(self.agents.keys()) + 1
        strategy_type = parent1.strategy_type if np.random.random() < 0.5 else parent2.strategy_type

        child = TradingAgent(child_id, strategy_type, self.config)

        # Mix some parameters
        if hasattr(child.strategy, 'exploration_rate'):
            child.strategy.exploration_rate = (parent1.strategy.exploration_rate +
                                             parent2.strategy.exploration_rate) / 2

        return child

    def train(self, n_episodes: int) -> Dict[str, List]:
        """Train the multi-agent system"""

        print(f"Starting multi-agent training for {n_episodes} episodes...")
        print(f"Number of agents: {self.config.n_agents}")
        print(f"Agent distribution: {self.config.agent_distribution}")
        print(f"Communication enabled: {self.config.communication_enabled}")
        print(f"Evolution enabled: {self.config.evolution_enabled}")

        performance_history = []

        for episode in range(n_episodes):
            episode_performance = []

            for step in range(self.config.episode_length):
                step_result = self.step()
                episode_performance.append(step_result)

            # Calculate episode metrics
            total_system_value = episode_performance[-1]['total_system_value']
            avg_agent_fitness = np.mean(list(episode_performance[-1]['agent_fitnesses'].values()))

            performance_history.append({
                'episode': episode,
                'total_system_value': total_system_value,
                'avg_agent_fitness': avg_agent_fitness,
                'consensus_strength': max(episode_performance[-1]['consensus_opinion'].values()),
                'market_price': self.market_simulator.price
            })

            # Evolution
            if (episode + 1) % 100 == 0 and self.config.evolution_enabled:
                self.evolve_population()

            if (episode + 1) % 50 == 0:
                print(f"Episode {episode + 1}: System Value = {total_system_value:.2f}, "
                      f"Avg Fitness = {avg_agent_fitness:.4f}")

        return {
            'performance_history': performance_history,
            'final_agents': self.agents,
            'market_history': self.market_simulator.price_history
        }

    def get_system_metrics(self) -> Dict[str, float]:
        """Get comprehensive system metrics"""

        agent_fitnesses = [agent.fitness_score for agent in self.agents.values()]
        agent_positions = [agent.position for agent in self.agents.values()]

        return {
            'total_system_value': sum(agent.portfolio_value for agent in self.agents.values()),
            'avg_agent_fitness': np.mean(agent_fitnesses),
            'fitness_std': np.std(agent_fitnesses),
            'position_diversity': np.std(agent_positions),
            'communication_volume': len(self.communication_protocol.message_queue),
            'market_volatility': self.market_simulator.get_market_state().volatility,
            'agent_strategy_diversity': len(set(agent.strategy_type for agent in self.agents.values())),
            'consensus_effectiveness': np.mean([
                max(self.consensus_mechanism.confidence_levels[aid] for aid in self.agents.keys())
            ])
        }


def create_multi_agent_system(config: Optional[MultiAgentConfig] = None) -> MultiAgentSystem:
    """Factory function for multi-agent trading system"""
    if config is None:
        config = MultiAgentConfig()
    return MultiAgentSystem(config)


def simulate_swarm_trading(market_data: pd.DataFrame, n_agents: int = 20) -> Dict[str, Any]:
    """Simulate swarm trading on historical data"""

    config = MultiAgentConfig(
        n_agents=n_agents,
        communication_enabled=True,
        swarm_intelligence=True,
        evolution_enabled=True
    )

    system = create_multi_agent_system(config)

    # Run simulation
    results = system.train(n_episodes=100)

    return {
        'system_performance': results['performance_history'],
        'final_metrics': system.get_system_metrics(),
        'market_impact': system.market_simulator.cumulative_market_impact,
        'agent_diversity': len(set(agent.strategy_type for agent in system.agents.values()))
    }


# Example usage and testing
if __name__ == "__main__":
    # Test multi-agent system
    print("Testing Multi-Agent Trading System...")

    config = MultiAgentConfig(
        n_agents=5,  # Small system for testing
        max_episodes=10,
        communication_enabled=True,
        evolution_enabled=False  # Disable for short test
    )

    system = create_multi_agent_system(config)

    print(f"Created multi-agent system with {config.n_agents} agents")
    print(f"Agent types: {config.agent_types}")
    print(f"Communication: {config.communication_enabled}")
    print(f"Evolution: {config.evolution_enabled}")

    # Run short simulation
    print("\nRunning simulation...")
    results = system.train(n_episodes=5)

    final_metrics = system.get_system_metrics()
    print("
Final system metrics:")
    for key, value in final_metrics.items():
        print(f"  {key}: {value:.4f}")

    print(f"\nSimulation completed with {len(results['performance_history'])} episodes")
