"""Advanced benchmarking and performance analysis tools for qantify.signals."""

from __future__ import annotations

import gc
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from .indicators import (
    atr,
    bollinger_bands,
    ema,
    rolling_volatility,
    rsi,
    sma,
    macd,
    stochastic,
    ichimoku,
    supertrend,
    keltner_channels,
    adx,
    cci,
    mfi,
    pivot_points,
    williams_r,
    ultimate_oscillator,
    chaikin_money_flow,
    aroon,
    elder_ray,
    force_index,
    ease_of_movement,
    volume_price_trend,
    accumulation_distribution,
    chaikin_oscillator,
    chande_momentum_oscillator,
    psychological_line,
    vertical_horizontal_filter,
    trend_intensity_index,
    trix,
    vidya,
    alma,
    frama,
    gma,
    jma,
    lsma,
    mcginley_dynamic,
    median_price,
    typical_price,
    weighted_close_price,
    price_channel,
    regression_channel,
    standard_error_channel,
    andrews_pitchfork,
    fibonacci_retracements,
    fibonacci_extensions,
    head_shoulders_patterns,
    double_top_bottom,
    wedge_patterns,
    triangle_patterns,
    flag_patterns,
    cup_handle_patterns,
    advanced_head_shoulders,
    complex_harmonic_patterns,
    advanced_wedge_patterns,
    advanced_triangle_patterns,
    rectangle_box_patterns,
    diamond_patterns,
    broadening_patterns,
    contracting_patterns,
    advanced_flag_patterns,
    pennant_patterns,
    inverse_head_shoulders,
    rounding_patterns,
    ascending_channel,
    descending_channel,
    clustering_market_regime_signals,
    autoencoder_anomaly_signals,
    lstm_price_prediction_signals,
    reinforcement_learning_signals,
    neural_network_regime_classifier,
    ensemble_ml_signals,
    feature_importance_signals,
    anomaly_detection_signals,
    time_series_forecast_signals,
    value_at_risk_signals,
    drawdown_risk_signals,
    volatility_adjusted_signals,
    kelly_criterion_signals,
    conditional_value_at_risk_signals,
    risk_parity_signals,
    stress_testing_signals,
    liquidity_risk_signals,
    concentration_risk_signals,
    margin_risk_signals,
    resample_to_timeframe,
    align_multiple_timeframes,
    cross_timeframe_correlation_signals,
    hierarchical_signal_synthesis,
    multi_timeframe_momentum_signals,
    timeframe_synchronization_signals,
    multi_timeframe_pattern_recognition,
    hierarchical_signal_aggregation,
    multi_timeframe_volatility_signals,
)


@dataclass(slots=True)
class BenchmarkResult:
    name: str
    duration_ms: float
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    iterations_per_second: float = 0.0
    error_rate: float = 0.0
    scalability_score: float = 0.0

    def __str__(self) -> str:  # pragma: no cover - human friendly output
        return f"{self.name}: {self.duration_ms:.2f} ms, {self.memory_usage_mb:.1f} MB, {self.iterations_per_second:.0f} iter/s"

    def to_dict(self) -> Dict[str, Union[str, float]]:
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_percent": self.cpu_percent,
            "iterations_per_second": self.iterations_per_second,
            "error_rate": self.error_rate,
            "scalability_score": self.scalability_score,
        }


@dataclass(slots=True)
class BenchmarkSuite:
    name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: BenchmarkResult) -> None:
        self.results.append(result)

    def get_fastest(self) -> Optional[BenchmarkResult]:
        return min(self.results, key=lambda x: x.duration_ms) if self.results else None

    def get_slowest(self) -> Optional[BenchmarkResult]:
        return max(self.results, key=lambda x: x.duration_ms) if self.results else None

    def get_average_duration(self) -> float:
        return np.mean([r.duration_ms for r in self.results]) if self.results else 0.0

    def get_memory_efficient(self) -> Optional[BenchmarkResult]:
        return min(self.results, key=lambda x: x.memory_usage_mb) if self.results else None

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([r.to_dict() for r in self.results])


@dataclass(slots=True)
class PerformanceProfile:
    function_name: str
    execution_time: float
    memory_peak: float
    cpu_usage: float
    input_size: int
    output_size: int
    error_count: int = 0
    warnings_count: int = 0

    def efficiency_score(self) -> float:
        """Calculate overall efficiency score (0-100)."""
        if self.execution_time <= 0:
            return 0.0

        # Normalize metrics to 0-1 scale and combine
        time_score = min(1.0, 1000.0 / self.execution_time)  # Faster is better
        memory_score = min(1.0, 100.0 / self.memory_peak) if self.memory_peak > 0 else 1.0  # Less memory is better
        error_score = max(0.0, 1.0 - (self.error_count * 0.1))  # Fewer errors is better

        return (time_score * 0.5 + memory_score * 0.3 + error_score * 0.2) * 100


@dataclass(slots=True)
class BenchmarkConfig:
    iterations: int = 5
    warm_up_iterations: int = 2
    enable_memory_profiling: bool = True
    enable_cpu_profiling: bool = True
    data_sizes: List[int] = field(default_factory=lambda: [1000, 10000, 100000])
    parallel_execution: bool = False
    max_workers: int = None


def generate_price_series(rows: int = 1_000_000, seed: int = 7) -> pd.Series:
    """Generate a synthetic price series for benchmarking."""

    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0002, scale=0.01, size=rows)
    price = 100 * np.exp(np.cumsum(returns))
    index = pd.date_range("2020-01-01", periods=rows, freq="T", tz="UTC")
    return pd.Series(price, index=index, name="close")


def generate_ohlcv_data(rows: int = 100000, seed: int = 7) -> pd.DataFrame:
    """Generate synthetic OHLCV data for comprehensive benchmarking."""

    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0002, scale=0.015, size=rows)

    # Generate base price series
    close = 100 * np.exp(np.cumsum(returns))

    # Generate OHLC with realistic spreads
    high = close * (1 + rng.exponential(0.005, rows))
    low = close * (1 - rng.exponential(0.005, rows))
    open_price = close * (1 + rng.normal(0, 0.002, rows))
    volume = rng.lognormal(10, 1, rows)  # Realistic volume distribution

    index = pd.date_range("2020-01-01", periods=rows, freq="5T", tz="UTC")

    return pd.DataFrame({
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    }, index=index)


def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        import psutil
        return psutil.cpu_percent(interval=0.1)
    except ImportError:
        return 0.0


def profile_function_execution(
    func: Callable,
    *args,
    iterations: int = 5,
    warm_up: int = 2,
    **kwargs
) -> PerformanceProfile:
    """Profile function execution with detailed metrics."""

    function_name = getattr(func, '__name__', str(func))
    input_size = len(args[0]) if args and hasattr(args[0], '__len__') else 0

    # Warm-up runs
    for _ in range(warm_up):
        try:
            func(*args, **kwargs)
        except:
            pass

    # Profile execution
    execution_times = []
    memory_usages = []
    cpu_usages = []
    error_count = 0

    for _ in range(iterations):
        # Memory before
        mem_before = get_memory_usage()
        cpu_before = get_cpu_usage()

        # Execute function
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            error_count += 1
            result = None
        end_time = time.perf_counter()

        # Memory after
        mem_after = get_memory_usage()
        cpu_after = get_cpu_usage()

        execution_times.append((end_time - start_time) * 1000)  # Convert to ms
        memory_usages.append(mem_after - mem_before)
        cpu_usages.append(cpu_after)

    # Calculate averages
    avg_execution_time = np.mean(execution_times)
    avg_memory_usage = max(0, np.mean(memory_usages))
    avg_cpu_usage = np.mean(cpu_usages)

    # Calculate output size
    output_size = 0
    if result is not None:
        if hasattr(result, 'shape'):
            output_size = result.shape[0] if hasattr(result.shape, '__len__') else result.shape
        elif hasattr(result, '__len__'):
            output_size = len(result)

    return PerformanceProfile(
        function_name=function_name,
        execution_time=avg_execution_time,
        memory_peak=avg_memory_usage,
        cpu_usage=avg_cpu_usage,
        input_size=input_size,
        output_size=output_size,
        error_count=error_count,
    )


def run_benchmark(
    cases: Dict[str, Callable[[pd.Series], None]],
    *,
    rows: int = 1_000_000,
    config: Optional[BenchmarkConfig] = None
) -> List[BenchmarkResult]:
    """Execute provided callables against a generated price series with advanced profiling."""

    if config is None:
        config = BenchmarkConfig()

    series = generate_price_series(rows=rows)
    results: List[BenchmarkResult] = []

    for name, func in cases.items():
        try:
            # Profile the function
            profile = profile_function_execution(
                func,
                series,
                iterations=config.iterations,
                warm_up=config.warm_up_iterations
            )

            # Calculate iterations per second
            iterations_per_second = 1000 / profile.execution_time if profile.execution_time > 0 else 0

            # Calculate error rate
            error_rate = profile.error_count / config.iterations if config.iterations > 0 else 0

            # Calculate scalability score (simplified)
            scalability_score = profile.efficiency_score()

            result = BenchmarkResult(
                name=name,
                duration_ms=profile.execution_time,
                memory_usage_mb=profile.memory_peak,
                cpu_percent=profile.cpu_usage,
                iterations_per_second=iterations_per_second,
                error_rate=error_rate,
                scalability_score=scalability_score,
            )

            results.append(result)

        except Exception as e:
            # Fallback result for failed benchmarks
            results.append(BenchmarkResult(
                name=name,
                duration_ms=float('inf'),
                error_rate=1.0,
            ))

    return results


def run_parallel_benchmark(
    cases: Dict[str, Callable[[pd.Series], None]],
    *,
    rows: int = 1_000_000,
    config: Optional[BenchmarkConfig] = None,
    max_workers: Optional[int] = None
) -> List[BenchmarkResult]:
    """Run benchmarks in parallel for better performance."""

    if config is None:
        config = BenchmarkConfig()

    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), len(cases))

    series = generate_price_series(rows=rows)

    def benchmark_single_case(name: str, func: Callable) -> BenchmarkResult:
        """Benchmark a single case."""
        try:
            profile = profile_function_execution(
                func,
                series,
                iterations=config.iterations,
                warm_up=config.warm_up_iterations
            )

            iterations_per_second = 1000 / profile.execution_time if profile.execution_time > 0 else 0
            error_rate = profile.error_count / config.iterations if config.iterations > 0 else 0
            scalability_score = profile.efficiency_score()

            return BenchmarkResult(
                name=name,
                duration_ms=profile.execution_time,
                memory_usage_mb=profile.memory_peak,
                cpu_percent=profile.cpu_usage,
                iterations_per_second=iterations_per_second,
                error_rate=error_rate,
                scalability_score=scalability_score,
            )
        except Exception:
            return BenchmarkResult(
                name=name,
                duration_ms=float('inf'),
                error_rate=1.0,
            )

    # Run benchmarks in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(benchmark_single_case, name, func)
            for name, func in cases.items()
        ]

        for future in as_completed(futures):
            results.append(future.result())

    return results


def run_scalability_benchmark(
    func: Callable[[pd.Series], Any],
    *,
    data_sizes: List[int] = None,
    config: Optional[BenchmarkConfig] = None
) -> Dict[int, PerformanceProfile]:
    """Test function scalability across different data sizes."""

    if data_sizes is None:
        data_sizes = [1000, 10000, 100000, 1000000]

    if config is None:
        config = BenchmarkConfig()

    scalability_results = {}

    for size in data_sizes:
        series = generate_price_series(rows=size)

        profile = profile_function_execution(
            func,
            series,
            iterations=config.iterations,
            warm_up=config.warm_up_iterations
        )

        scalability_results[size] = profile

    return scalability_results


def compare_implementations(
    implementations: Dict[str, Callable[[pd.Series], Any]],
    *,
    data_size: int = 100000,
    config: Optional[BenchmarkConfig] = None
) -> BenchmarkSuite:
    """Compare different implementations of the same functionality."""

    if config is None:
        config = BenchmarkConfig()

    series = generate_price_series(rows=data_size)
    suite = BenchmarkSuite(name=f"Implementation Comparison ({data_size} rows)")

    for name, func in implementations.items():
        try:
            profile = profile_function_execution(
                func,
                series,
                iterations=config.iterations,
                warm_up=config.warm_up_iterations
            )

            iterations_per_second = 1000 / profile.execution_time if profile.execution_time > 0 else 0
            error_rate = profile.error_count / config.iterations if config.iterations > 0 else 0
            scalability_score = profile.efficiency_score()

            result = BenchmarkResult(
                name=name,
                duration_ms=profile.execution_time,
                memory_usage_mb=profile.memory_peak,
                cpu_percent=profile.cpu_usage,
                iterations_per_second=iterations_per_second,
                error_rate=error_rate,
                scalability_score=scalability_score,
            )

            suite.add_result(result)

        except Exception as e:
            suite.add_result(BenchmarkResult(
                name=name,
                duration_ms=float('inf'),
                error_rate=1.0,
            ))

    return suite


def generate_benchmark_report(
    suite: BenchmarkSuite,
    *,
    output_format: str = "text",
    include_charts: bool = False
) -> str:
    """Generate a comprehensive benchmark report."""

    if not suite.results:
        return "No benchmark results to report."

    # Sort results by duration
    sorted_results = sorted(suite.results, key=lambda x: x.duration_ms)

    report_lines = []
    report_lines.append(f"📊 Benchmark Report: {suite.name}")
    report_lines.append("=" * 60)
    report_lines.append("")

    # Summary statistics
    valid_results = [r for r in suite.results if r.duration_ms != float('inf')]
    if valid_results:
        avg_duration = np.mean([r.duration_ms for r in valid_results])
        avg_memory = np.mean([r.memory_usage_mb for r in valid_results])
        avg_cpu = np.mean([r.cpu_percent for r in valid_results])

        report_lines.append("📈 Summary Statistics:")
        report_lines.append(f"   • Average Duration: {avg_duration:.2f} ms")
        report_lines.append(f"   • Average Memory Usage: {avg_memory:.2f} MB")
        report_lines.append(f"   • Average CPU Usage: {avg_cpu:.1f}%")
        report_lines.append("")

    # Individual results
    report_lines.append("🏁 Individual Results:")
    report_lines.append("-" * 40)

    for i, result in enumerate(sorted_results, 1):
        status = "✅" if result.duration_ms != float('inf') else "❌"
        report_lines.append(f"{i:2d}. {status} {result}")

        if result.error_rate > 0:
            report_lines.append(f"      ⚠️  Error Rate: {result.error_rate:.1%}")
    report_lines.append("")

    # Performance analysis
    if len(valid_results) > 1:
        report_lines.append("🎯 Performance Analysis:")
        report_lines.append("-" * 40)

        fastest = min(valid_results, key=lambda x: x.duration_ms)
        slowest = max(valid_results, key=lambda x: x.duration_ms)
        most_memory_efficient = min(valid_results, key=lambda x: x.memory_usage_mb)

        speedup = slowest.duration_ms / fastest.duration_ms if fastest.duration_ms > 0 else 0

        report_lines.append(f"   • Fastest: {fastest.name} ({fastest.duration_ms:.2f} ms)")
        report_lines.append(f"   • Slowest: {slowest.name} ({slowest.duration_ms:.2f} ms)")
        report_lines.append(f"   • Best Speedup: {speedup:.1f}x")
        report_lines.append(f"   • Most Memory Efficient: {most_memory_efficient.name} ({most_memory_efficient.memory_usage_mb:.2f} MB)")

    return "\n".join(report_lines)


def default_benchmark_suite() -> Dict[str, Callable[[pd.Series], None]]:
    """Return a default suite of benchmarkable indicator callables."""

    def runner_sma(series: pd.Series) -> None:
        sma(series, window=50)

    def runner_ema(series: pd.Series) -> None:
        ema(series, period=50)

    def runner_rsi(series: pd.Series) -> None:
        rsi(series, period=14)

    def runner_vol(series: pd.Series) -> None:
        rolling_volatility(series, window=60)

    def runner_boll(series: pd.Series) -> None:
        frame = pd.DataFrame({"close": series})
        bollinger_bands(frame, window=20)

    def runner_atr(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        atr(frame)

    return {
        "sma_50": runner_sma,
        "ema_50": runner_ema,
        "rsi_14": runner_rsi,
        "vol_60": runner_vol,
        "boll_20": runner_boll,
        "atr_14": runner_atr,
    }


def comprehensive_benchmark_suite() -> Dict[str, Callable[[pd.Series], None]]:
    """Return a comprehensive benchmark suite with all major indicators."""

    def runner_sma(series: pd.Series) -> None:
        sma(series, window=50)

    def runner_ema(series: pd.Series) -> None:
        ema(series, period=50)

    def runner_rsi(series: pd.Series) -> None:
        rsi(series, period=14)

    def runner_macd(series: pd.Series) -> None:
        macd(series)

    def runner_bollinger(series: pd.Series) -> None:
        frame = pd.DataFrame({"close": series})
        bollinger_bands(frame)

    def runner_stochastic(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        stochastic(frame)

    def runner_ichimoku(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        ichimoku(frame)

    def runner_supertrend(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        supertrend(frame)

    def runner_keltner(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        keltner_channels(frame)

    def runner_adx(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        adx(frame)

    def runner_cci(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        cci(frame)

    def runner_mfi(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series, "volume": np.random.randint(1000, 5000, len(series))})
        mfi(frame)

    def runner_pivot_points(series: pd.Series) -> None:
        frame = pd.DataFrame({"high": series * 1.01, "low": series * 0.99, "close": series})
        pivot_points(frame)

    return {
        "sma_50": runner_sma,
        "ema_50": runner_ema,
        "rsi_14": runner_rsi,
        "macd": runner_macd,
        "bollinger_bands": runner_bollinger,
        "stochastic": runner_stochastic,
        "ichimoku": runner_ichimoku,
        "supertrend": runner_supertrend,
        "keltner_channels": runner_keltner,
        "adx": runner_adx,
        "cci": runner_cci,
        "mfi": runner_mfi,
        "pivot_points": runner_pivot_points,
    }


def ml_benchmark_suite() -> Dict[str, Callable[[pd.DataFrame], None]]:
    """Return ML-specific benchmark suite."""

    def runner_clustering_regime(data: pd.DataFrame) -> None:
        clustering_market_regime_signals(data, lookback=50)

    def runner_rl_signals(data: pd.DataFrame) -> None:
        reinforcement_learning_signals(data)

    def runner_nn_regime(data: pd.DataFrame) -> None:
        neural_network_regime_classifier(data, lookback=50)

    def runner_anomaly_detection(data: pd.DataFrame) -> None:
        anomaly_detection_signals(data)

    return {
        "clustering_regime": runner_clustering_regime,
        "reinforcement_learning": runner_rl_signals,
        "neural_network_regime": runner_nn_regime,
        "anomaly_detection": runner_anomaly_detection,
    }


def risk_benchmark_suite() -> Dict[str, Callable[[pd.DataFrame], None]]:
    """Return risk management specific benchmark suite."""

    def runner_var(data: pd.DataFrame) -> None:
        value_at_risk_signals(data, lookback=50)

    def runner_drawdown(data: pd.DataFrame) -> None:
        drawdown_risk_signals(data)

    def runner_vol_adj(data: pd.DataFrame) -> None:
        volatility_adjusted_signals(data)

    def runner_kelly(data: pd.DataFrame) -> None:
        kelly_criterion_signals(data, lookback=50)

    def runner_stress(data: pd.DataFrame) -> None:
        stress_testing_signals(data)

    return {
        "value_at_risk": runner_var,
        "drawdown_analysis": runner_drawdown,
        "volatility_adjusted": runner_vol_adj,
        "kelly_criterion": runner_kelly,
        "stress_testing": runner_stress,
    }


def pattern_recognition_benchmark_suite() -> Dict[str, Callable[[pd.DataFrame], None]]:
    """Return pattern recognition specific benchmark suite."""

    def runner_head_shoulders(data: pd.DataFrame) -> None:
        advanced_head_shoulders(data, lookback=50)

    def runner_harmonic(data: pd.DataFrame) -> None:
        complex_harmonic_patterns(data, pattern_type="gartley")

    def runner_wedge(data: pd.DataFrame) -> None:
        advanced_wedge_patterns(data)

    def runner_triangle(data: pd.DataFrame) -> None:
        advanced_triangle_patterns(data)

    def runner_rectangle(data: pd.DataFrame) -> None:
        rectangle_box_patterns(data)

    return {
        "head_shoulders": runner_head_shoulders,
        "harmonic_patterns": runner_harmonic,
        "wedge_patterns": runner_wedge,
        "triangle_patterns": runner_triangle,
        "rectangle_patterns": runner_rectangle,
    }


def multi_timeframe_benchmark_suite() -> Dict[str, Callable[[pd.DataFrame], None]]:
    """Return multi-timeframe specific benchmark suite."""

    def runner_timeframe_alignment(data: pd.DataFrame) -> None:
        align_multiple_timeframes(data, timeframes=["1H", "4H"])

    def runner_cross_correlation(data: pd.DataFrame) -> None:
        cross_timeframe_correlation_signals(data, timeframes=["1H", "4H"], correlation_window=20)

    def runner_hierarchical_synthesis(data: pd.DataFrame) -> None:
        hierarchical_signal_synthesis(data, timeframes=["15T", "1H", "4H"])

    def runner_mtf_momentum(data: pd.DataFrame) -> None:
        multi_timeframe_momentum_signals(data, timeframes=["1H", "4H"])

    def runner_mtf_volatility(data: pd.DataFrame) -> None:
        multi_timeframe_volatility_signals(data, timeframes=["15T", "1H"])

    return {
        "timeframe_alignment": runner_timeframe_alignment,
        "cross_correlation": runner_cross_correlation,
        "hierarchical_synthesis": runner_hierarchical_synthesis,
        "mtf_momentum": runner_mtf_momentum,
        "mtf_volatility": runner_mtf_volatility,
    }


__all__ = [
    # Core classes
    "BenchmarkResult",
    "BenchmarkSuite",
    "PerformanceProfile",
    "BenchmarkConfig",

    # Data generation
    "generate_price_series",
    "generate_ohlcv_data",

    # Profiling utilities
    "get_memory_usage",
    "get_cpu_usage",
    "profile_function_execution",

    # Benchmark execution
    "run_benchmark",
    "run_parallel_benchmark",
    "run_scalability_benchmark",
    "compare_implementations",
    "generate_benchmark_report",

    # Benchmark suites
    "default_benchmark_suite",
    "comprehensive_benchmark_suite",
    "ml_benchmark_suite",
    "risk_benchmark_suite",
    "pattern_recognition_benchmark_suite",
    "multi_timeframe_benchmark_suite",
]
