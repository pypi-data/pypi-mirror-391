"""Advanced scenario orchestration for multi-asset, multi-strategy batch execution."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence, Set, Tuple, Type, Union
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import multiprocessing as mp

import pandas as pd
import numpy as np

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.types import OrderSide
from qantify.strategy import Strategy
# from qantify.data import DataPipeline, DataClient  # Temporarily commented out

logger = logging.getLogger(__name__)


class StrategyFactory(Protocol):
    """Protocol for strategy instantiation."""

    def __call__(self, **kwargs) -> Strategy:
        ...


@dataclass(slots=True)
class AssetConfig:
    """Configuration for a single asset in the orchestration."""

    symbol: str
    data_client: Optional[DataClient] = None
    data_params: Dict[str, Any] = field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = "UTC"


@dataclass(slots=True)
class StrategyConfig:
    """Configuration for a single strategy in the orchestration."""

    name: str
    strategy_cls: Type[Strategy]
    params: Dict[str, Any] = field(default_factory=dict)
    asset_filter: Optional[Callable[[str], bool]] = None  # Filter assets for this strategy
    weight: float = 1.0  # Relative weight in portfolio allocation
    enabled: bool = True


@dataclass(slots=True)
class EventInjection:
    """Configuration for injecting events into the data stream."""

    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    affected_assets: Set[str] = field(default_factory=set)
    description: str = ""


@dataclass(slots=True)
class OrchestrationResult:
    """Result from a complete orchestration run."""

    strategy_results: Dict[str, Dict[str, EventBacktestResult]]  # strategy -> asset -> result
    portfolio_metrics: pd.DataFrame
    execution_time: float
    event_log: List[Dict[str, Any]]
    total_trades: int
    start_time: datetime
    end_time: datetime


@dataclass(slots=True)
class OrchestrationConfig:
    """Configuration for the entire orchestration run."""

    assets: List[AssetConfig]
    strategies: List[StrategyConfig]
    initial_capital: float = 100_000.0
    max_parallel_assets: int = 4
    max_parallel_strategies: int = 2
    enable_progress_tracking: bool = True
    event_injections: List[EventInjection] = field(default_factory=list)
    risk_limits: Dict[str, float] = field(default_factory=dict)
    commission_model: Optional[Any] = None
    slippage_model: Optional[Any] = None


class DataLoader:
    """Asynchronous data loading manager."""

    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def load_asset_data(self, config: AssetConfig) -> Tuple[str, pd.DataFrame]:
        """Load data for a single asset."""
        async with self.semaphore:
            try:
                if config.data_client is None:
                    raise ValueError(f"No data client for {config.symbol}")

                # Build query parameters
                params = config.data_params.copy()
                if config.start_date:
                    params.setdefault('start_date', config.start_date)
                if config.end_date:
                    params.setdefault('end_date', config.end_date)

                # Load data
                data = await config.data_client.get_historical_data(config.symbol, **params)

                # Ensure proper datetime index
                if not isinstance(data.index, pd.DatetimeIndex):
                    data.index = pd.to_datetime(data.index)

                if config.timezone != "UTC":
                    data.index = data.index.tz_convert(config.timezone)
                elif data.index.tz is None:
                    data.index = data.index.tz_localize('UTC')

                logger.info(f"Loaded {len(data)} bars for {config.symbol}")
                return config.symbol, data

            except Exception as e:
                logger.error(f"Failed to load data for {config.symbol}: {e}")
                raise


class EventInjector:
    """Handles injection of events into data streams."""

    @staticmethod
    def inject_events(data: pd.DataFrame, events: List[EventInjection]) -> pd.DataFrame:
        """Inject events into the data stream."""
        modified_data = data.copy()

        for event in events:
            if event.timestamp in modified_data.index:
                # Modify existing row
                for key, value in event.data.items():
                    if key in modified_data.columns:
                        modified_data.loc[event.timestamp, key] = value
            else:
                # Insert new row
                new_row = pd.DataFrame(event.data, index=[event.timestamp])
                modified_data = pd.concat([modified_data, new_row]).sort_index()

        return modified_data

    @staticmethod
    def create_earnings_event(
        symbol: str,
        timestamp: datetime,
        earnings_surprise: float,
        volatility_multiplier: float = 2.0
    ) -> EventInjection:
        """Create an earnings event injection."""
        return EventInjection(
            timestamp=timestamp,
            event_type="earnings",
            data={
                "earnings_surprise": earnings_surprise,
                "volatility_spike": True,
                "volume_multiplier": volatility_multiplier
            },
            affected_assets={symbol},
            description=f"Earnings surprise for {symbol}: {earnings_surprise:.2%}"
        )


class StrategyRunner:
    """Manages execution of strategies across assets."""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.data_loader = DataLoader(max_concurrent=config.max_parallel_assets)

    async def run_strategy_on_asset(
        self,
        strategy_config: StrategyConfig,
        asset_config: AssetConfig,
        data: pd.DataFrame
    ) -> Tuple[str, str, EventBacktestResult]:
        """Run a single strategy on a single asset."""
        try:
            # Inject events if any
            if self.config.event_injections:
                relevant_events = [
                    event for event in self.config.event_injections
                    if not event.affected_assets or asset_config.symbol in event.affected_assets
                ]
                if relevant_events:
                    data = EventInjector.inject_events(data, relevant_events)

            # Create strategy instance
            strategy = strategy_config.strategy_cls(**strategy_config.params)

            # Configure backtester
            backtest_kwargs = {
                'initial_cash': self.config.initial_capital * strategy_config.weight,
                'commission_model': self.config.commission_model,
                'slippage_model': self.config.slippage_model,
            }

            # Run backtest
            engine = EventBacktester(
                data,
                symbol=asset_config.symbol,
                strategy=strategy,
                **backtest_kwargs
            )

            result = engine.run()

            logger.info(f"Completed {strategy_config.name} on {asset_config.symbol}")
            return strategy_config.name, asset_config.symbol, result

        except Exception as e:
            logger.error(f"Failed {strategy_config.name} on {asset_config.symbol}: {e}")
            raise

    async def run_strategy_matrix(
        self,
        strategy_configs: List[StrategyConfig],
        asset_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, EventBacktestResult]]:
        """Run multiple strategies across multiple assets."""
        tasks = []

        for strategy_config in strategy_configs:
            if not strategy_config.enabled:
                continue

            for asset_symbol, data in asset_data.items():
                # Apply asset filter if specified
                if strategy_config.asset_filter and not strategy_config.asset_filter(asset_symbol):
                    continue

                task = self.run_strategy_on_asset(strategy_config, asset_symbol, data)
                tasks.append(task)

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Organize results
        strategy_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed: {result}")
                continue

            strategy_name, asset_symbol, backtest_result = result
            if strategy_name not in strategy_results:
                strategy_results[strategy_name] = {}
            strategy_results[strategy_name][asset_symbol] = backtest_result

        return strategy_results


class PortfolioAggregator:
    """Aggregates results from multiple strategies/assets into portfolio metrics."""

    @staticmethod
    def combine_results(
        strategy_results: Dict[str, Dict[str, EventBacktestResult]],
        weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """Combine individual backtest results into portfolio-level metrics."""
        if not strategy_results:
            return pd.DataFrame()

        # Collect all equity curves
        equity_curves = {}
        for strategy_name, asset_results in strategy_results.items():
            for asset_symbol, result in asset_results.items():
                key = f"{strategy_name}_{asset_symbol}"
                equity_curves[key] = result.equity_curve

        if not equity_curves:
            return pd.DataFrame()

        # Create combined DataFrame
        combined_df = pd.DataFrame(equity_curves)

        # Calculate portfolio metrics
        portfolio_df = pd.DataFrame(index=combined_df.index)

        if weights:
            # Weighted portfolio
            total_weight = sum(weights.values())
            normalized_weights = {k: v/total_weight for k, v in weights.items()}

            weighted_equity = pd.Series(0.0, index=combined_df.index)
            for key, equity in equity_curves.items():
                strategy_name = key.split('_')[0]
                weight = normalized_weights.get(strategy_name, 1.0 / len(strategy_results))
                weighted_equity += equity * weight

            portfolio_df['portfolio_equity'] = weighted_equity
        else:
            # Equal weighted portfolio
            portfolio_df['portfolio_equity'] = combined_df.mean(axis=1)

        # Calculate returns
        portfolio_df['portfolio_returns'] = portfolio_df['portfolio_equity'].pct_change()

        # Calculate drawdowns
        portfolio_df['portfolio_peak'] = portfolio_df['portfolio_equity'].expanding().max()
        portfolio_df['portfolio_drawdown'] = (
            portfolio_df['portfolio_equity'] - portfolio_df['portfolio_peak']
        ) / portfolio_df['portfolio_peak']

        return portfolio_df

    @staticmethod
    def aggregate_statistics(results: Dict[str, Dict[str, EventBacktestResult]]) -> Dict[str, Any]:
        """Aggregate key statistics across all results."""
        stats = {
            'total_strategies': len(results),
            'total_assets': sum(len(asset_results) for asset_results in results.values()),
            'total_trades': 0,
            'avg_sharpe': 0.0,
            'max_drawdown': 0.0,
            'avg_win_rate': 0.0,
        }

        sharpe_ratios = []
        drawdowns = []
        win_rates = []

        for strategy_results in results.values():
            for result in strategy_results.values():
                stats['total_trades'] += len(result.trades)
                sharpe_ratios.append(result.sharpe_ratio)
                drawdowns.append(result.max_drawdown)
                win_rates.append(result.win_rate)

        if sharpe_ratios:
            stats['avg_sharpe'] = np.mean(sharpe_ratios)
        if drawdowns:
            stats['max_drawdown'] = max(drawdowns)
        if win_rates:
            stats['avg_win_rate'] = np.mean(win_rates)

        return stats


class Orchestrator:
    """Main orchestration engine for multi-asset, multi-strategy execution."""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.strategy_runner = StrategyRunner(config)
        self.portfolio_aggregator = PortfolioAggregator()
        self.start_time = None
        self.end_time = None

    async def run_async(self) -> OrchestrationResult:
        """Run the complete orchestration asynchronously."""
        import time
        start_time = time.time()
        self.start_time = datetime.now()

        try:
            # Load all asset data
            logger.info(f"Loading data for {len(self.config.assets)} assets...")
            data_tasks = [
                self.strategy_runner.data_loader.load_asset_data(asset)
                for asset in self.config.assets
            ]

            asset_data_results = await asyncio.gather(*data_tasks, return_exceptions=True)
            asset_data = {}

            for result in asset_data_results:
                if isinstance(result, Exception):
                    logger.error(f"Data loading failed: {result}")
                    continue
                symbol, data = result
                asset_data[symbol] = data

            if not asset_data:
                raise ValueError("No asset data could be loaded")

            # Run all strategies
            logger.info(f"Running {len(self.config.strategies)} strategies across {len(asset_data)} assets...")
            strategy_results = await self.strategy_runner.run_strategy_matrix(
                self.config.strategies,
                asset_data
            )

            # Aggregate portfolio metrics
            strategy_weights = {
                strategy.name: strategy.weight
                for strategy in self.config.strategies
                if strategy.enabled
            }

            portfolio_metrics = self.portfolio_aggregator.combine_results(
                strategy_results,
                strategy_weights
            )

            # Collect event log
            event_log = [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type,
                    'description': event.description,
                    'affected_assets': list(event.affected_assets)
                }
                for event in self.config.event_injections
            ]

            execution_time = time.time() - start_time
            self.end_time = datetime.now()

            # Calculate total trades
            total_trades = sum(
                len(result.trades)
                for strategy_results in strategy_results.values()
                for result in strategy_results.values()
            )

            logger.info(f"Orchestration completed in {execution_time:.2f}s with {total_trades} total trades")

            return OrchestrationResult(
                strategy_results=strategy_results,
                portfolio_metrics=portfolio_metrics,
                execution_time=execution_time,
                event_log=event_log,
                total_trades=total_trades,
                start_time=self.start_time,
                end_time=self.end_time
            )

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            raise

    def run(self) -> OrchestrationResult:
        """Run the complete orchestration synchronously."""
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(self.run_async())
        except Exception as e:
            logger.error(f"Synchronous orchestration failed: {e}")
            raise


# Convenience functions for common use cases
async def run_multi_asset_backtest(
    assets: List[str],
    strategies: List[StrategyConfig],
    data_clients: Dict[str, DataClient],
    **kwargs
) -> OrchestrationResult:
    """Convenience function for running strategies across multiple assets."""
    asset_configs = [
        AssetConfig(symbol=asset, data_client=data_clients.get(asset))
        for asset in assets
    ]

    config = OrchestrationConfig(
        assets=asset_configs,
        strategies=strategies,
        **kwargs
    )

    orchestrator = Orchestrator(config)
    return await orchestrator.run_async()


def run_parallel_orchestrations(
    configs: List[OrchestrationConfig],
    max_workers: int = 4
) -> List[OrchestrationResult]:
    """Run multiple orchestrations in parallel."""
    def run_single_config(config: OrchestrationConfig) -> OrchestrationResult:
        orchestrator = Orchestrator(config)
        return orchestrator.run()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_single_config, configs))

    return results


__all__ = [
    "Orchestrator",
    "OrchestrationConfig",
    "OrchestrationResult",
    "AssetConfig",
    "StrategyConfig",
    "EventInjection",
    "StrategyFactory",
    "DataLoader",
    "EventInjector",
    "StrategyRunner",
    "PortfolioAggregator",
    "run_multi_asset_backtest",
    "run_parallel_orchestrations",
]
