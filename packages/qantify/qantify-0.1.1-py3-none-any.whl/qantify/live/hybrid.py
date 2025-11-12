"""Hybrid live trading system with backtest-to-live bridges and warm start capabilities."""

from __future__ import annotations

import asyncio
import logging
import pickle
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import uuid

import pandas as pd
import numpy as np

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.portfolio import Portfolio
from qantify.backtest.types import OrderSide
from qantify.live.engine import LiveEngine, LiveOrder
from qantify.live.adapters import ExecutionReport, RestExchangeAdapter, WebsocketExchangeAdapter
from qantify.live.order_manager import LiveOrderManager
from qantify.live.risk import RiskConfig, RiskGuardrails
from qantify.strategy import Strategy
from qantify.data.streaming import EventQueue, StreamEvent
# from qantify.data import DataPipeline  # Not available

logger = logging.getLogger(__name__)


class TransitionProtocol(Protocol):
    """Protocol for backtest-to-live transitions."""

    async def prepare_transition(self) -> Dict[str, Any]:
        """Prepare state for transition."""
        ...

    async def execute_transition(self, state: Dict[str, Any]) -> bool:
        """Execute the transition to live trading."""
        ...


@dataclass(slots=True)
class WarmStartState:
    """State information for warm starting a strategy."""

    strategy_state: Dict[str, Any]
    portfolio_state: Dict[str, Any]
    market_state: Dict[str, Any]
    timestamp: datetime
    strategy_name: str
    backtest_result: Optional[EventBacktestResult] = None
    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save state to a pickle file."""
        filepath = Path(filepath)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        logger.info(f"Warm start state saved to {filepath}")

    @classmethod
    def load_from_file(cls, filepath: Union[str, Path]) -> WarmStartState:
        """Load state from a pickle file."""
        filepath = Path(filepath)
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        logger.info(f"Warm start state loaded from {filepath}")
        return state


@dataclass(slots=True)
class HybridConfig:
    """Configuration for hybrid live/backtest operation."""

    enable_paper_trading: bool = True
    enable_live_bridge: bool = False
    warm_start_enabled: bool = True
    incremental_evaluation: bool = True
    evaluation_interval_minutes: int = 15
    max_transition_attempts: int = 3
    transition_timeout_seconds: int = 30
    state_persistence_path: Optional[Path] = None
    risk_config: Optional[RiskConfig] = None


@dataclass(slots=True)
class IncrementalMetrics:
    """Metrics computed incrementally during live operation."""

    timestamp: datetime
    portfolio_value: float
    daily_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    active_positions: int
    unrealized_pnl: float
    realized_pnl: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'portfolio_value': self.portfolio_value,
            'daily_return': self.daily_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'active_positions': self.active_positions,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
        }


class StateManager:
    """Manages persistence and restoration of trading state."""

    def __init__(self, persistence_path: Optional[Path] = None):
        self.persistence_path = persistence_path or Path("./warm_start_states")
        self.persistence_path.mkdir(exist_ok=True)
        self.states: Dict[str, WarmStartState] = {}

    def save_state(self, strategy_name: str, state: WarmStartState) -> str:
        """Save a warm start state."""
        filename = f"{strategy_name}_{state.timestamp.strftime('%Y%m%d_%H%M%S')}_{state.transition_id[:8]}.pkl"
        filepath = self.persistence_path / filename

        state.save_to_file(filepath)
        self.states[state.transition_id] = state

        logger.info(f"State saved: {strategy_name} at {state.timestamp}")
        return state.transition_id

    def load_state(self, transition_id: str) -> Optional[WarmStartState]:
        """Load a warm start state."""
        if transition_id in self.states:
            return self.states[transition_id]

        # Try to load from file
        pattern = f"*_{transition_id[:8]}.pkl"
        for filepath in self.persistence_path.glob(pattern):
            try:
                state = WarmStartState.load_from_file(filepath)
                self.states[transition_id] = state
                return state
            except Exception as e:
                logger.warning(f"Failed to load state from {filepath}: {e}")

        return None

    def list_available_states(self, strategy_name: Optional[str] = None) -> List[WarmStartState]:
        """List all available warm start states."""
        states = list(self.states.values())

        # Also check filesystem
        for filepath in self.persistence_path.glob("*.pkl"):
            try:
                state = WarmStartState.load_from_file(filepath)
                if state.transition_id not in [s.transition_id for s in states]:
                    states.append(state)
            except Exception as e:
                logger.warning(f"Failed to load state from {filepath}: {e}")

        if strategy_name:
            states = [s for s in states if s.strategy_name == strategy_name]

        return sorted(states, key=lambda x: x.timestamp, reverse=True)

    def cleanup_old_states(self, keep_last_n: int = 10, older_than_days: int = 30) -> int:
        """Clean up old state files."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        # Get all state files
        state_files = list(self.persistence_path.glob("*.pkl"))

        # Sort by modification time (newest first)
        state_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Keep only the most recent files
        files_to_delete = state_files[keep_last_n:]

        for filepath in files_to_delete:
            try:
                # Check if file is older than cutoff
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff_date:
                    filepath.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {filepath}: {e}")

        logger.info(f"Cleaned up {deleted_count} old state files")
        return deleted_count


class IncrementalEvaluator:
    """Provides incremental performance evaluation during live operation."""

    def __init__(self, evaluation_window_days: int = 30):
        self.evaluation_window_days = evaluation_window_days
        self.metrics_history: List[IncrementalMetrics] = []
        self.portfolio_history: List[Tuple[datetime, float]] = []
        self.trade_history: List[Dict[str, Any]] = []

    def update_portfolio_value(self, timestamp: datetime, portfolio_value: float) -> None:
        """Update portfolio value for incremental calculations."""
        self.portfolio_history.append((timestamp, portfolio_value))

        # Keep only recent history
        cutoff = timestamp - timedelta(days=self.evaluation_window_days)
        self.portfolio_history = [
            (ts, val) for ts, val in self.portfolio_history
            if ts >= cutoff
        ]

    def record_trade(self, trade_data: Dict[str, Any]) -> None:
        """Record a trade for performance calculations."""
        self.trade_history.append(trade_data)

        # Keep only recent trades
        cutoff = datetime.now() - timedelta(days=self.evaluation_window_days)
        self.trade_history = [
            trade for trade in self.trade_history
            if trade.get('timestamp', datetime.min) >= cutoff
        ]

    def calculate_incremental_metrics(self, current_timestamp: datetime) -> IncrementalMetrics:
        """Calculate current incremental performance metrics."""
        if not self.portfolio_history:
            return self._create_empty_metrics(current_timestamp)

        # Get recent portfolio values
        recent_values = [
            val for ts, val in self.portfolio_history
            if ts <= current_timestamp
        ]

        if len(recent_values) < 2:
            return self._create_empty_metrics(current_timestamp)

        # Calculate returns
        portfolio_values = pd.Series(recent_values)
        returns = portfolio_values.pct_change().dropna()

        # Calculate metrics
        portfolio_value = recent_values[-1]
        daily_return = returns.iloc[-1] if len(returns) > 0 else 0.0

        # Sharpe ratio (annualized)
        if len(returns) > 1:
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        else:
            sharpe_ratio = 0.0

        # Max drawdown
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = drawdown.min()

        # Win rate from trades
        if self.trade_history:
            winning_trades = sum(1 for trade in self.trade_history if trade.get('pnl', 0) > 0)
            win_rate = winning_trades / len(self.trade_history)
        else:
            win_rate = 0.0

        # Position and P&L calculations
        total_trades = len(self.trade_history)
        active_positions = 0  # Would need position data
        unrealized_pnl = 0.0  # Would need position data
        realized_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history)

        metrics = IncrementalMetrics(
            timestamp=current_timestamp,
            portfolio_value=portfolio_value,
            daily_return=daily_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=total_trades,
            active_positions=active_positions,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
        )

        self.metrics_history.append(metrics)
        return metrics

    def _create_empty_metrics(self, timestamp: datetime) -> IncrementalMetrics:
        """Create empty metrics when insufficient data is available."""
        return IncrementalMetrics(
            timestamp=timestamp,
            portfolio_value=0.0,
            daily_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            active_positions=0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
        )

    def get_metrics_history(self, hours_back: int = 24) -> List[IncrementalMetrics]:
        """Get metrics history for the specified time period."""
        cutoff = datetime.now() - timedelta(hours=hours_back)
        return [m for m in self.metrics_history if m.timestamp >= cutoff]

    def export_metrics_report(self, filepath: Union[str, Path]) -> None:
        """Export metrics history to CSV."""
        if not self.metrics_history:
            logger.warning("No metrics history to export")
            return

        df = pd.DataFrame([m.to_dict() for m in self.metrics_history])
        df.to_csv(filepath, index=False)
        logger.info(f"Metrics report exported to {filepath}")


class BacktestLiveBridge:
    """Bridge between backtesting and live trading environments."""

    def __init__(
        self,
        backtest_result: EventBacktestResult,
        live_adapter: RestExchangeAdapter,
        config: HybridConfig
    ):
        self.backtest_result = backtest_result
        self.live_adapter = live_adapter
        self.config = config
        self.state_manager = StateManager(config.state_persistence_path)
        self.evaluator = IncrementalEvaluator()
        self.transition_state: Optional[Dict[str, Any]] = None

    async def prepare_warm_start(self, strategy: Strategy) -> WarmStartState:
        """Prepare strategy and portfolio state for warm start."""
        logger.info("Preparing warm start state...")

        # Extract strategy state
        strategy_state = {
            'indicators': {},
            'rules': [rule.name for rule in strategy._rules],
            'last_signals': getattr(strategy, '_last_signals', {}),
        }

        # Extract portfolio state from backtest result
        portfolio_state = {
            'cash': self.backtest_result.final_portfolio_value,
            'positions': {},  # Would need to extract from backtest trades
            'equity_curve': self.backtest_result.equity_curve.tolist(),
        }

        # Extract market state
        market_state = {
            'last_update': datetime.now(),
            'backtest_end_date': self.backtest_result.trades[-1].timestamp if self.backtest_result.trades else None,
        }

        # Create warm start state
        state = WarmStartState(
            strategy_state=strategy_state,
            portfolio_state=portfolio_state,
            market_state=market_state,
            timestamp=datetime.now(),
            strategy_name=strategy.__class__.__name__,
            backtest_result=self.backtest_result,
        )

        # Save state if persistence is enabled
        if self.config.state_persistence_path:
            self.state_manager.save_state(strategy.__class__.__name__, state)

        logger.info("Warm start state prepared")
        return state

    async def execute_transition_to_live(
        self,
        strategy: Strategy,
        warm_start_state: WarmStartState
    ) -> LiveEngine:
        """Execute transition from backtest to live trading."""
        logger.info("Executing transition to live trading...")

        # Create live portfolio with warm start values
        portfolio = Portfolio(
            cash=warm_start_state.portfolio_state['cash'],
            positions={},  # Start with no positions for safety
        )

        # Create live engine
        engine = LiveEngine(
            strategy=strategy,
            adapter=self.live_adapter,
            portfolio=portfolio,
            risk_config=self.config.risk_config,
        )

        # Restore strategy state if possible
        try:
            if hasattr(strategy, 'warm_start'):
                await strategy.warm_start(warm_start_state.strategy_state)
                logger.info("Strategy warm-started successfully")
        except Exception as e:
            logger.warning(f"Strategy warm-start failed: {e}")

        # Start live engine
        await engine.start()
        logger.info("Live engine started with warm start")

        return engine

    async def validate_transition(self, live_engine: LiveEngine) -> bool:
        """Validate that the transition was successful."""
        try:
            # Check if engine is running
            if not live_engine._running:
                return False

            # Check portfolio state
            if live_engine.portfolio.cash <= 0:
                logger.warning("Invalid portfolio cash after transition")
                return False

            # Check adapter connectivity
            # This would depend on the specific adapter implementation

            logger.info("Transition validation successful")
            return True

        except Exception as e:
            logger.error(f"Transition validation failed: {e}")
            return False


class PaperTradingBridge:
    """Paper trading environment that mirrors live trading."""

    def __init__(self, config: HybridConfig):
        self.config = config
        self.live_engines: Dict[str, LiveEngine] = {}
        self.paper_portfolios: Dict[str, Portfolio] = {}
        self.evaluators: Dict[str, IncrementalEvaluator] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

    async def create_paper_engine(
        self,
        strategy: Strategy,
        symbol: str,
        initial_capital: float = 10000.0
    ) -> str:
        """Create a paper trading engine for a strategy."""
        engine_id = str(uuid.uuid4())

        # Create paper portfolio
        portfolio = Portfolio(cash=initial_capital)

        # Create mock adapter for paper trading
        adapter = PaperTradingAdapter()

        # Create live engine (but in paper mode)
        engine = LiveEngine(
            strategy=strategy,
            adapter=adapter,
            portfolio=portfolio,
            risk_config=self.config.risk_config,
        )

        # Create evaluator
        evaluator = IncrementalEvaluator()

        # Store components
        self.live_engines[engine_id] = engine
        self.paper_portfolios[engine_id] = portfolio
        self.evaluators[engine_id] = evaluator

        logger.info(f"Created paper trading engine: {engine_id}")
        return engine_id

    async def start_paper_trading(self, engine_id: str) -> bool:
        """Start paper trading for a specific engine."""
        if engine_id not in self.live_engines:
            logger.error(f"Engine {engine_id} not found")
            return False

        engine = self.live_engines[engine_id]

        try:
            await engine.start()
            logger.info(f"Started paper trading for engine {engine_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start paper trading for {engine_id}: {e}")
            return False

    def start_monitoring(self) -> None:
        """Start background monitoring of paper trading engines."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return

        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        logger.info("Started paper trading monitoring")

    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Stopped paper trading monitoring")

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self.running:
            try:
                # Update metrics for all engines
                current_time = datetime.now()

                for engine_id, evaluator in self.evaluators.items():
                    if engine_id in self.paper_portfolios:
                        portfolio = self.paper_portfolios[engine_id]
                        portfolio_value = portfolio.total_value()

                        evaluator.update_portfolio_value(current_time, portfolio_value)
                        metrics = evaluator.calculate_incremental_metrics(current_time)

                        # Log significant changes
                        if abs(metrics.daily_return) > 0.01:  # 1% change
                            logger.info(f"Daily return: {metrics.daily_return:.2f}")
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            # Sleep for evaluation interval
            threading.Event().wait(self.config.evaluation_interval_minutes * 60)

    def get_paper_metrics(self, engine_id: str) -> Optional[IncrementalMetrics]:
        """Get current metrics for a paper trading engine."""
        if engine_id not in self.evaluators:
            return None

        evaluator = self.evaluators[engine_id]
        return evaluator.calculate_incremental_metrics(datetime.now())

    def export_paper_report(self, engine_id: str, filepath: Union[str, Path]) -> bool:
        """Export paper trading report."""
        if engine_id not in self.evaluators:
            return False

        evaluator = self.evaluators[engine_id]
        try:
            evaluator.export_metrics_report(filepath)
            return True
        except Exception as e:
            logger.error(f"Failed to export paper report: {e}")
            return False


class PaperTradingAdapter(RestExchangeAdapter):
    """Mock adapter for paper trading that simulates live exchange behavior."""

    def __init__(self):
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, float] = {}
        self.order_counter = 0

    async def submit_order(self, **kwargs) -> str:
        """Submit a paper trading order."""
        order_id = f"paper_{self.order_counter}"
        self.order_counter += 1

        self.orders[order_id] = {
            'id': order_id,
            'status': 'filled',  # Paper trades are always filled instantly
            'submitted_at': datetime.now(),
            **kwargs
        }

        # Update positions (simplified)
        symbol = kwargs.get('symbol', '')
        side = kwargs.get('side', '')
        quantity = kwargs.get('quantity', 0)
        price = kwargs.get('price', 0)

        if side.lower() == 'buy':
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        elif side.lower() == 'sell':
            self.positions[symbol] = self.positions.get(symbol, 0) - quantity

        return order_id

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a paper trading order."""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'cancelled'
            return True
        return False

    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a paper trading order."""
        return self.orders.get(order_id)

    async def get_positions(self) -> Dict[str, float]:
        """Get current paper trading positions."""
        return self.positions.copy()

    async def get_account_balance(self) -> Dict[str, float]:
        """Get paper trading account balance."""
        return {'cash': 10000.0, 'total': 10000.0}  # Mock balance


class HybridManager:
    """Main manager for hybrid live/backtest operations."""

    def __init__(self, config: HybridConfig):
        self.config = config
        self.bridge = None
        self.paper_bridge = PaperTradingBridge(config)
        self.state_manager = StateManager(config.state_persistence_path)
        self.active_engines: Dict[str, LiveEngine] = {}

    async def transition_to_live(
        self,
        backtest_result: EventBacktestResult,
        strategy: Strategy,
        live_adapter: RestExchangeAdapter
    ) -> Optional[LiveEngine]:
        """Transition from backtest to live trading."""
        logger.info("Starting backtest-to-live transition...")

        # Create bridge
        self.bridge = BacktestLiveBridge(backtest_result, live_adapter, self.config)

        try:
            # Prepare warm start
            warm_start_state = await self.bridge.prepare_warm_start(strategy)

            # Execute transition
            live_engine = await self.bridge.execute_transition_to_live(strategy, warm_start_state)

            # Validate transition
            if await self.bridge.validate_transition(live_engine):
                engine_id = str(uuid.uuid4())
                self.active_engines[engine_id] = live_engine
                logger.info("Transition to live trading completed successfully")
                return live_engine
            else:
                logger.error("Transition validation failed")
                return None

        except Exception as e:
            logger.error(f"Transition failed: {e}")
            return None

    async def start_paper_trading(
        self,
        strategy: Strategy,
        symbol: str,
        initial_capital: float = 10000.0
    ) -> Optional[str]:
        """Start paper trading for a strategy."""
        try:
            engine_id = await self.paper_bridge.create_paper_engine(
                strategy, symbol, initial_capital
            )

            success = await self.paper_bridge.start_paper_trading(engine_id)

            if success:
                self.paper_bridge.start_monitoring()
                return engine_id
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to start paper trading: {e}")
            return None

    def get_incremental_metrics(self, engine_id: str) -> Optional[IncrementalMetrics]:
        """Get incremental metrics for an engine."""
        return self.paper_bridge.get_paper_metrics(engine_id)

    async def export_hybrid_report(
        self,
        engine_id: str,
        filepath: Union[str, Path]
    ) -> bool:
        """Export hybrid trading report."""
        return self.paper_bridge.export_paper_report(engine_id, filepath)

    def list_warm_start_states(self, strategy_name: Optional[str] = None) -> List[WarmStartState]:
        """List available warm start states."""
        return self.state_manager.list_available_states(strategy_name)

    def cleanup_states(self) -> int:
        """Clean up old state files."""
        return self.state_manager.cleanup_old_states()


# Convenience functions
async def create_hybrid_setup(
    backtest_result: EventBacktestResult,
    strategy: Strategy,
    live_adapter: Optional[RestExchangeAdapter] = None,
    enable_paper_trading: bool = True,
    enable_live_bridge: bool = False
) -> HybridManager:
    """Create a hybrid trading setup."""
    config = HybridConfig(
        enable_paper_trading=enable_paper_trading,
        enable_live_bridge=enable_live_bridge,
        warm_start_enabled=True,
        incremental_evaluation=True,
    )

    manager = HybridManager(config)

    if enable_paper_trading:
        # Start paper trading automatically
        await manager.start_paper_trading(strategy, "HYBRID")

    if enable_live_bridge and live_adapter:
        await manager.transition_to_live(backtest_result, strategy, live_adapter)

    return manager


__all__ = [
    "HybridManager",
    "HybridConfig",
    "WarmStartState",
    "IncrementalMetrics",
    "BacktestLiveBridge",
    "PaperTradingBridge",
    "PaperTradingAdapter",
    "StateManager",
    "IncrementalEvaluator",
    "TransitionProtocol",
    "create_hybrid_setup",
]
