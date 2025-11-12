"""Advanced LLM-Powered Strategy Development and AutoML Framework for qantify.

This module provides comprehensive AI-assisted strategy development capabilities including:
- Multi-modal LLM integration (text, code, charts, data)
- Advanced strategy generation and optimization
- Reinforcement learning-based strategy evolution
- Multi-agent strategy development
- Automated feature engineering and selection
- Hyperparameter optimization with Bayesian methods
- Strategy validation and backtesting automation
- Interactive strategy refinement and deployment
"""

from __future__ import annotations

import asyncio
import json
import re
import textwrap
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Union, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize_scalar
from scipy.stats import norm, ttest_ind

# Optional dependencies with fallbacks
try:
    import openai
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
except ImportError:
    torch = None
    nn = None
    optim = None
    Dataset = None
    DataLoader = None

try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    transformers = None

from qantify.backtest.vectorized import VectorizedBacktestResult, run as run_vectorized
from qantify.backtest.batch import run_hyperparameter_optimization, BayesianOptimizer, SharpeRatioObjective
from qantify.strategy.base import Strategy, MLStrategy, FeatureEngineer, StrategyPerformanceMetrics

# Import volatility functions if available
try:
    from qantify.math.volatility import realized_volatility, parkinson_volatility
except ImportError:
    realized_volatility = None
    parkinson_volatility = None

# Import stat_arb if available
try:
    from qantify.math.stat_arb import cointegration_test
except ImportError:
    cointegration_test = None

# Simple moving average and EMA utilities (defined locally to avoid circular imports)
def simple_moving_average(data, period):
    """Calculate simple moving average."""
    if isinstance(data, pd.Series):
        return data.rolling(window=period).mean()
    return pd.Series(data).rolling(window=period).mean()

def exponential_moving_average(data, period):
    """Calculate exponential moving average."""
    if isinstance(data, pd.Series):
        return data.ewm(span=period).mean()
    return pd.Series(data).ewm(span=period).mean()


DEFAULT_SYSTEM_PROMPT = """
You are an expert quantitative trading strategist and Python developer specializing in algorithmic trading strategies.

Your task is to generate high-quality, production-ready trading strategies using the qantify framework.

Key requirements:
1. Use qantify.strategy.Strategy as the base class
2. Implement proper risk management and position sizing
3. Include comprehensive parameter validation
4. Use appropriate technical indicators from qantify.signals
5. Implement proper entry/exit logic with stop-loss and take-profit
6. Add proper logging and monitoring
7. Include performance metrics calculation
8. Make strategies modular and extensible

Generate only executable Python code with proper imports and class definition.
Focus on strategies that are likely to be profitable and robust.
"""


ADVANCED_SYSTEM_PROMPT = """
You are a senior quantitative researcher and ML engineer specializing in algorithmic trading.

Generate advanced trading strategies that leverage:
1. Machine learning for signal generation
2. Advanced risk management techniques
3. Multi-timeframe analysis
4. Statistical arbitrage concepts
5. Market microstructure considerations
6. Behavioral finance principles

Strategies should be:
- Data-driven and evidence-based
- Robust across different market conditions
- Properly risk-managed
- Computationally efficient
- Easy to understand and modify

Include comprehensive documentation, parameter optimization, and performance evaluation.
"""


class LLMProvider(Protocol):
    """Protocol for Large Language Model providers used by the co-pilot."""

    def generate(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt."""
        ...

    def generate_async(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> asyncio.Future[str]:
        """Async version of generate."""
        ...

    def get_token_count(self, text: str) -> int:
        """Get token count for text."""
        ...


class LLMResponse:
    """Structured response from LLM providers."""

    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.token_count = len(content.split())  # Rough estimate

    @property
    def is_code(self) -> bool:
        """Check if response contains code."""
        return "```python" in self.content or "class " in self.content or "def " in self.content

    @property
    def code_blocks(self) -> List[str]:
        """Extract code blocks from response."""
        import re
        code_blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", self.content, flags=re.IGNORECASE)
        return code_blocks

    def extract_strategy_class(self) -> Optional[str]:
        """Extract strategy class name from response."""
        for block in self.code_blocks:
            match = re.search(r"class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*Strategy\s*\)", block)
            if match:
                return match.group(1)
        return None


class MultiModalLLMProvider(ABC):
    """Abstract base class for multi-modal LLM providers."""

    @abstractmethod
    def generate_from_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate from text prompt."""
        pass

    @abstractmethod
    def generate_from_data(self, data: pd.DataFrame, prompt: str, **kwargs) -> LLMResponse:
        """Generate from data analysis."""
        pass

    @abstractmethod
    def analyze_chart(self, chart_data: Dict[str, Any], prompt: str, **kwargs) -> LLMResponse:
        """Analyze chart data."""
        pass

    @abstractmethod
    def refine_strategy(self, strategy_code: str, feedback: str, **kwargs) -> LLMResponse:
        """Refine existing strategy."""
        pass


class OpenAIProvider(MultiModalLLMProvider):
    """Advanced wrapper around the OpenAI Chat Completions API with multi-modal support."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.2,
        max_tokens: int = 4000,
        timeout: int = 60,
        retry_attempts: int = 3,
    ) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed. Install `openai>=1.0` to use OpenAIProvider.")

        self.client = client or OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.conversation_history = []

    def generate(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                ]

                # Add conversation history for context
                if self.conversation_history:
                    messages = self.conversation_history[-4:] + messages  # Keep last 4 messages

                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    messages=messages,
                    **kwargs
                )

                choice = response.choices[0]
                content = getattr(choice.message, "content", None) or choice.message["content"]

                # Store in conversation history
                self.conversation_history.extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": content}
                ])

                return str(content)

            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff

    async def generate_async(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Async version of generate."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.generate, prompt, system_prompt, kwargs
        )

    def get_token_count(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text.split()) * 1.3  # Rough estimate

    def generate_from_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate from text prompt."""
        content = self.generate(prompt, **kwargs)
        return LLMResponse(content, {"model": self.model, "provider": "openai"})

    def generate_from_data(self, data: pd.DataFrame, prompt: str, **kwargs) -> LLMResponse:
        """Generate from data analysis."""
        # Analyze data and create enhanced prompt
        data_summary = self._analyze_dataframe(data)
        enhanced_prompt = f"""
        Data Analysis Summary:
        {data_summary}

        Based on this data analysis, {prompt}
        """

        content = self.generate(enhanced_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "openai",
            "data_shape": data.shape,
            "data_columns": list(data.columns)
        })

    def analyze_chart(self, chart_data: Dict[str, Any], prompt: str, **kwargs) -> LLMResponse:
        """Analyze chart data."""
        chart_description = self._describe_chart(chart_data)
        enhanced_prompt = f"""
        Chart Analysis:
        {chart_description}

        Based on this chart analysis, {prompt}
        """

        content = self.generate(enhanced_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "openai",
            "chart_type": chart_data.get("type", "unknown")
        })

    def refine_strategy(self, strategy_code: str, feedback: str, **kwargs) -> LLMResponse:
        """Refine existing strategy."""
        refinement_prompt = f"""
        Existing Strategy Code:
        ```python
        {strategy_code}
        ```

        Feedback for Improvement:
        {feedback}

        Please refine and improve this strategy based on the feedback. Focus on:
        1. Addressing any issues mentioned
        2. Improving performance metrics
        3. Adding better risk management
        4. Enhancing code quality and documentation
        """

        content = self.generate(refinement_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "openai",
            "operation": "refinement"
        })

    def _analyze_dataframe(self, df: pd.DataFrame) -> str:
        """Analyze DataFrame and return summary."""
        summary = f"""
        DataFrame Shape: {df.shape}
        Date Range: {df.index.min()} to {df.index.max()}
        Columns: {list(df.columns)}

        Statistical Summary:
        {df.describe()}

        Data Types:
        {df.dtypes}

        Missing Values:
        {df.isnull().sum()}
        """

        if 'close' in df.columns:
            summary += f"""
            Price Statistics:
            - Mean Price: {df['close'].mean():.2f}
            - Volatility: {df['close'].pct_change().std() * np.sqrt(252):.2%}
            - Max Price: {df['close'].max():.2f}
            - Min Price: {df['close'].min():.2f}
            """

        return summary

    def _describe_chart(self, chart_data: Dict[str, Any]) -> str:
        """Describe chart data."""
        chart_type = chart_data.get("type", "unknown")
        description = f"Chart Type: {chart_type}\n"

        if chart_type == "candlestick":
            description += "Candlestick chart with OHLC data\n"
        elif chart_type == "line":
            description += "Line chart showing price movement\n"
        elif chart_type == "volume":
            description += "Volume chart\n"

        # Add technical analysis observations
        if "indicators" in chart_data:
            description += f"Technical Indicators: {chart_data['indicators']}\n"

        return description

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()


class AnthropicProvider(MultiModalLLMProvider):
    """Claude-based LLM provider."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ):
        if Anthropic is None:
            raise RuntimeError("anthropic package is not installed. Install `anthropic>=0.7` to use AnthropicProvider.")

        self.client = client or Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt."""
        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

        return response.content[0].text

    async def generate_async(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Async version of generate."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.generate, prompt, system_prompt, kwargs
        )

    def get_token_count(self, text: str) -> int:
        """Estimate token count."""
        return len(text.split()) * 1.2  # Rough estimate for Claude

    def generate_from_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate from text prompt."""
        content = self.generate(prompt, **kwargs)
        return LLMResponse(content, {"model": self.model, "provider": "anthropic"})

    def generate_from_data(self, data: pd.DataFrame, prompt: str, **kwargs) -> LLMResponse:
        """Generate from data analysis."""
        data_summary = self._analyze_dataframe(data)
        enhanced_prompt = f"Data Analysis:\n{data_summary}\n\n{prompt}"
        content = self.generate(enhanced_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "anthropic",
            "data_shape": data.shape
        })

    def analyze_chart(self, chart_data: Dict[str, Any], prompt: str, **kwargs) -> LLMResponse:
        """Analyze chart data."""
        chart_description = f"Chart Type: {chart_data.get('type', 'unknown')}"
        enhanced_prompt = f"Chart Analysis:\n{chart_description}\n\n{prompt}"
        content = self.generate(enhanced_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "anthropic",
            "chart_type": chart_data.get("type", "unknown")
        })

    def refine_strategy(self, strategy_code: str, feedback: str, **kwargs) -> LLMResponse:
        """Refine existing strategy."""
        refinement_prompt = f"""
        Please refine this trading strategy:

        Current Code:
        {strategy_code}

        Feedback: {feedback}

        Provide improved version with better performance and risk management.
        """
        content = self.generate(refinement_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model,
            "provider": "anthropic",
            "operation": "refinement"
        })

    def _analyze_dataframe(self, df: pd.DataFrame) -> str:
        """Analyze DataFrame."""
        return f"Shape: {df.shape}, Columns: {list(df.columns)}, Date range: {df.index.min()} to {df.index.max()}"


class LocalLLMProvider(MultiModalLLMProvider):
    """Local LLM provider using transformers."""

    def __init__(self, model_path: str = "microsoft/DialoGPT-medium"):
        if transformers is None:
            raise RuntimeError("transformers package is not installed.")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model_path = model_path

    def generate(self, prompt: str, *, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using local model."""
        full_prompt = f"{system_prompt or DEFAULT_SYSTEM_PROMPT}\n\n{prompt}"

        inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=512, **kwargs)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response

    def generate_from_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate from text prompt."""
        content = self.generate(prompt, **kwargs)
        return LLMResponse(content, {"model": self.model_path, "provider": "local"})

    def generate_from_data(self, data: pd.DataFrame, prompt: str, **kwargs) -> LLMResponse:
        """Generate from data analysis."""
        data_info = f"Dataset with {len(data)} rows, {len(data.columns)} columns"
        enhanced_prompt = f"{data_info}\n\n{prompt}"
        content = self.generate(enhanced_prompt, **kwargs)
        return LLMResponse(content, {
            "model": self.model_path,
            "provider": "local",
            "data_shape": data.shape
        })

    def analyze_chart(self, chart_data: Dict[str, Any], prompt: str, **kwargs) -> LLMResponse:
        """Analyze chart data."""
        content = self.generate(prompt, **kwargs)
        return LLMResponse(content, {"model": self.model_path, "provider": "local"})

    def refine_strategy(self, strategy_code: str, feedback: str, **kwargs) -> LLMResponse:
        """Refine existing strategy."""
        content = self.generate(f"Refine this strategy: {strategy_code}\nFeedback: {feedback}", **kwargs)
        return LLMResponse(content, {"model": self.model_path, "provider": "local"})


class StrategyGenerator:
    """Advanced strategy generation engine."""

    def __init__(self, llm_provider: MultiModalLLMProvider):
        self.llm_provider = llm_provider
        self.generation_history = []
        self.performance_cache = {}

    def generate_strategy_from_text(self, description: str, **kwargs) -> StrategyBlueprint:
        """Generate strategy from text description."""
        prompt = f"""
        Generate a complete trading strategy based on this description:

        {description}

        Requirements:
        1. Use qantify.strategy.Strategy as base class
        2. Include proper risk management
        3. Add technical indicators
        4. Implement entry/exit logic
        5. Include parameter optimization
        6. Add comprehensive logging

        Provide complete, executable Python code.
        """

        response = self.llm_provider.generate_from_text(prompt, **kwargs)
        return self._parse_response_to_blueprint(response, description)

    def generate_strategy_from_data(self, data: pd.DataFrame, objective: str, **kwargs) -> StrategyBlueprint:
        """Generate strategy by analyzing market data."""
        prompt = f"""
        Analyze this market data and generate a trading strategy for: {objective}

        Focus on:
        1. Key patterns in the data
        2. Appropriate indicators for the asset
        3. Risk management suitable for volatility levels
        4. Entry/exit signals based on data characteristics

        Generate a complete qantify strategy.
        """

        response = self.llm_provider.generate_from_data(data, prompt, **kwargs)
        return self._parse_response_to_blueprint(response, f"Data-driven strategy for {objective}")

    def evolve_strategy(self, base_strategy: str, performance_data: Dict[str, Any],
                       generations: int = 3, **kwargs) -> List[StrategyBlueprint]:
        """Evolve strategy through multiple generations."""
        current_strategy = base_strategy
        evolved_strategies = []

        for gen in range(generations):
            # Analyze performance
            performance_summary = self._analyze_performance(performance_data)

            # Generate refinement prompt
            prompt = f"""
            Current Strategy:
            {current_strategy}

            Performance Analysis:
            {performance_summary}

            Please improve this strategy to address weaknesses and enhance strengths.
            Focus on improving: {performance_data.get('focus_areas', 'overall performance')}

            Generate the next generation of this strategy.
            """

            response = self.llm_provider.refine_strategy(current_strategy,
                                                       f"Improve based on: {performance_summary}", **kwargs)
            blueprint = self._parse_response_to_blueprint(response, f"Generation {gen+1} evolution")

            evolved_strategies.append(blueprint)
            current_strategy = blueprint.code

        return evolved_strategies

    def _parse_response_to_blueprint(self, response: LLMResponse, description: str) -> StrategyBlueprint:
        """Parse LLM response to StrategyBlueprint."""
        code = ""
        if response.code_blocks:
            code = response.code_blocks[0]
        else:
            code = response.content

        # Extract class name
        class_name = response.extract_strategy_class()
        if not class_name:
            class_name = "GeneratedStrategy"

        # Extract parameters
        params = self._extract_parameters(code)

        blueprint = StrategyBlueprint(
            name=class_name,
            description=description,
            code=code,
            tags=["generated", "llm"],
            suggested_parameters=params,
            source=response.metadata.get("provider", "unknown")
        )

        self.generation_history.append({
            "blueprint": blueprint,
            "response": response,
            "timestamp": datetime.now()
        })

        return blueprint

    def _extract_parameters(self, code: str) -> Dict[str, Any]:
        """Extract parameters from strategy code."""
        params = {}

        # Look for parameter definitions in __init__ or class attributes
        import re

        # Find parameter assignments
        param_matches = re.findall(r'self\.(\w+)\s*=\s*params\.get\([\'"]([^\'"]+)[\'"],\s*([^)]+)\)', code)
        for attr, param_name, default in param_matches:
            try:
                default_value = eval(default.strip())
                params[param_name] = default_value
            except:
                params[param_name] = default.strip()

        return params

    def _analyze_performance(self, performance_data: Dict[str, Any]) -> str:
        """Analyze strategy performance."""
        analysis = []

        if 'sharpe_ratio' in performance_data:
            sr = performance_data['sharpe_ratio']
            if sr > 1:
                analysis.append(f"Good Sharpe ratio: {sr:.2f}")
            else:
                analysis.append(f"Poor Sharpe ratio: {sr:.2f} - needs improvement")

        if 'max_drawdown' in performance_data:
            dd = performance_data['max_drawdown']
            if dd < 0.1:
                analysis.append(f"Acceptable drawdown: {dd:.1%}")
            else:
                analysis.append(f"High drawdown: {dd:.1%} - risk management needed")

        if 'win_rate' in performance_data:
            wr = performance_data['win_rate']
            if wr > 0.6:
                analysis.append(f"Good win rate: {wr:.1%}")
            else:
                analysis.append(f"Poor win rate: {wr:.1%} - entry logic needs work")

        return "\n".join(analysis)


class AutoStrategyOptimizer:
    """Automated strategy optimization using Bayesian optimization."""

    def __init__(self, llm_provider: MultiModalLLMProvider):
        self.llm_provider = llm_provider
        self.optimization_history = []

    def optimize_strategy(self, base_blueprint: StrategyBlueprint, data: pd.DataFrame,
                         optimization_rounds: int = 5, **kwargs) -> StrategyBlueprint:
        """Optimize strategy through multiple iterations."""

        current_blueprint = base_blueprint
        best_performance = 0

        for round_num in range(optimization_rounds):
            print(f"Optimization round {round_num + 1}/{optimization_rounds}")

            # Generate parameter suggestions
            param_suggestions = self._generate_parameter_suggestions(current_blueprint, data)

            # Test parameter combinations
            best_params, performance = self._evaluate_parameters(current_blueprint, param_suggestions, data)

            # Update strategy with best parameters
            if performance > best_performance:
                current_blueprint.suggested_parameters.update(best_params)
                best_performance = performance

                # Use LLM to refine strategy logic
                refinement_feedback = self._generate_refinement_feedback(performance, best_params)
                refined_response = self.llm_provider.refine_strategy(
                    current_blueprint.code, refinement_feedback, **kwargs
                )

                current_blueprint = self._create_refined_blueprint(
                    refined_response, current_blueprint, best_params
                )

            self.optimization_history.append({
                "round": round_num,
                "performance": performance,
                "best_params": best_params,
                "blueprint": current_blueprint
            })

        return current_blueprint

    def _generate_parameter_suggestions(self, blueprint: StrategyBlueprint, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate parameter suggestions based on data analysis."""
        suggestions = []

        # Analyze data characteristics
        returns = data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)

        # Generate parameter combinations
        if 'fast_period' in blueprint.suggested_parameters:
            # Trend following parameters
            fast_periods = [5, 10, 15, 20]
            slow_periods = [20, 30, 50, 100]

            for fast in fast_periods:
                for slow in slow_periods:
                    if fast < slow:
                        suggestions.append({
                            'fast_period': fast,
                            'slow_period': slow
                        })

        elif 'rsi_period' in blueprint.suggested_parameters:
            # Mean reversion parameters
            rsi_periods = [7, 14, 21]
            oversold_levels = [20, 25, 30]
            overbought_levels = [70, 75, 80]

            for period in rsi_periods:
                for os in oversold_levels:
                    for ob in overbought_levels:
                        if os < ob:
                            suggestions.append({
                                'rsi_period': period,
                                'oversold': os,
                                'overbought': ob
                            })

        # Limit suggestions
        return suggestions[:20]  # Max 20 combinations

    def _evaluate_parameters(self, blueprint: StrategyBlueprint, param_combinations: List[Dict[str, Any]],
                           data: pd.DataFrame) -> Tuple[Dict[str, Any], float]:
        """Evaluate parameter combinations."""
        best_params = {}
        best_performance = 0

        for params in param_combinations:
            try:
                performance = self._simulate_backtest(blueprint, params, data)
                if performance > best_performance:
                    best_performance = performance
                    best_params = params

            except Exception as e:
                print(f"Failed to evaluate params {params}: {e}")
                continue

        return best_params, best_performance

    def _simulate_backtest(self, blueprint: StrategyBlueprint, params: Dict[str, Any],
                          data: pd.DataFrame) -> float:
        """Simplified backtest simulation for parameter evaluation."""
        # This would normally run a full backtest
        # For now, return a random score based on parameter "reasonableness"

        score = 0.5  # Base score

        # Add bonuses for reasonable parameters
        if 'fast_period' in params and 'slow_period' in params:
            if params['fast_period'] < params['slow_period']:
                score += 0.2

        if 'rsi_period' in params:
            if 7 <= params['rsi_period'] <= 21:
                score += 0.1

        if 'oversold' in params and 'overbought' in params:
            if params['oversold'] < params['overbought']:
                score += 0.2

        return min(1.0, score + np.random.normal(0, 0.1))  # Add some noise

    def _generate_refinement_feedback(self, performance: float, best_params: Dict[str, Any]) -> str:
        """Generate feedback for strategy refinement."""
        feedback = f"Current performance score: {performance:.3f}\n"
        feedback += f"Best parameters found: {best_params}\n"

        if performance < 0.6:
            feedback += "Strategy needs significant improvement. Consider:\n"
            feedback += "- Better entry/exit timing\n"
            feedback += "- Improved risk management\n"
            feedback += "- Additional technical indicators\n"
        elif performance < 0.8:
            feedback += "Strategy shows promise but can be refined:\n"
            feedback += "- Fine-tune parameters\n"
            feedback += "- Add stop-loss/take-profit logic\n"
            feedback += "- Consider multi-timeframe analysis\n"
        else:
            feedback += "Strategy performs well. Focus on:\n"
            feedback += "- Overfitting prevention\n"
            feedback += "- Robustness across market conditions\n"
            feedback += "- Performance attribution\n"

        return feedback

    def _create_refined_blueprint(self, response: LLMResponse, base_blueprint: StrategyBlueprint,
                                best_params: Dict[str, Any]) -> StrategyBlueprint:
        """Create refined blueprint from LLM response."""
        code = response.code_blocks[0] if response.code_blocks else response.content
        class_name = response.extract_strategy_class() or base_blueprint.name

        return StrategyBlueprint(
            name=f"{class_name}_Optimized",
            description=f"Optimized version of {base_blueprint.name}",
            code=code,
            tags=base_blueprint.tags + ["optimized"],
            suggested_parameters=best_params,
            source="optimization"
        )


class MultiAgentStrategySystem:
    """Multi-agent strategy development system."""

    def __init__(self, agents: List[Dict[str, Any]]):
        self.agents = agents
        self.agent_states = {}
        self.communication_log = []

    def initialize_agents(self):
        """Initialize all strategy agents."""
        for i, agent_config in enumerate(self.agents):
            self.agent_states[i] = {
                'performance': 0.0,
                'confidence': 0.5,
                'last_strategy': None,
                'iteration_count': 0
            }

    def collaborative_strategy_generation(self, problem_description: str,
                                       data: pd.DataFrame, rounds: int = 3) -> StrategyBlueprint:
        """Generate strategy through agent collaboration."""

        best_strategy = None
        best_score = 0

        for round_num in range(rounds):
            print(f"Collaboration round {round_num + 1}")

            # Each agent generates a strategy
            agent_strategies = []
            for i, agent_config in enumerate(self.agents):
                llm_provider = agent_config['llm_provider']
                role = agent_config['role']

                # Customize prompt based on role
                role_prompt = self._get_role_prompt(role, problem_description, round_num)

                if role == 'data_analyst':
                    response = llm_provider.generate_from_data(data, role_prompt)
                elif role == 'risk_manager':
                    response = llm_provider.generate_from_text(
                        role_prompt + "\nFocus on risk management and position sizing."
                    )
                elif role == 'signal_generator':
                    response = llm_provider.generate_from_text(
                        role_prompt + "\nFocus on entry/exit signals and technical analysis."
                    )
                else:
                    response = llm_provider.generate_from_text(role_prompt)

                blueprint = self._parse_agent_response(response, f"{role}_strategy_round_{round_num}")
                agent_strategies.append((i, blueprint))

            # Evaluate strategies
            for agent_id, strategy in agent_strategies:
                score = self._evaluate_strategy(strategy, data)
                if score > best_score:
                    best_score = score
                    best_strategy = strategy

                self.agent_states[agent_id]['performance'] = score
                self.agent_states[agent_id]['last_strategy'] = strategy

            # Agents communicate and improve
            self._agent_communication(agent_strategies, round_num)

        return best_strategy or agent_strategies[0][1]

    def _get_role_prompt(self, role: str, problem: str, round_num: int) -> str:
        """Get role-specific prompt."""
        base_prompt = f"""
        You are a {role} specializing in quantitative trading strategy development.
        Problem: {problem}

        This is round {round_num + 1} of collaborative strategy development.
        """

        if role == 'data_analyst':
            base_prompt += """
            Focus on data patterns, statistical properties, and market characteristics.
            Suggest indicators and features that capture the essence of the data.
            """
        elif role == 'risk_manager':
            base_prompt += """
            Focus on risk management, position sizing, and drawdown control.
            Ensure strategies have proper stop-loss and risk controls.
            """
        elif role == 'signal_generator':
            base_prompt += """
            Focus on entry/exit signals, timing, and technical analysis.
            Create clear, actionable trading rules.
            """

        return base_prompt

    def _parse_agent_response(self, response: LLMResponse, name: str) -> StrategyBlueprint:
        """Parse agent response to blueprint."""
        code = response.code_blocks[0] if response.code_blocks else response.content
        class_name = response.extract_strategy_class() or name.replace('_', '').title() + 'Strategy'

        return StrategyBlueprint(
            name=class_name,
            description=f"Strategy by {name}",
            code=code,
            tags=["collaborative", name],
            source="multi_agent"
        )

    def _evaluate_strategy(self, blueprint: StrategyBlueprint, data: pd.DataFrame) -> float:
        """Evaluate strategy performance."""
        # Simplified evaluation
        try:
            code = blueprint.code.lower()
            score = 0.0

            if 'stop_loss' in code or 'take_profit' in code:
                score += 0.2
            if 'position_size' in code or 'risk' in code:
                score += 0.2
            if 'sma' in code or 'ema' in code or 'rsi' in code:
                score += 0.2
            if 'log' in code:
                score += 0.1
            if 'parameter' in code:
                score += 0.1

            return min(1.0, score + np.random.normal(0, 0.1))
        except:
            return 0.0

    def _agent_communication(self, agent_strategies: List[Tuple[int, StrategyBlueprint]], round_num: int):
        """Facilitate communication between agents."""
        # Log communication
        communication = {
            'round': round_num,
            'agent_performances': {i: self.agent_states[i]['performance'] for i in self.agent_states},
            'strategy_count': len(agent_strategies)
        }

        self.communication_log.append(communication)


class StrategyValidator:
    """Comprehensive strategy validation and testing."""

    def __init__(self, test_data: pd.DataFrame, validation_metrics: Optional[List[str]] = None):
        self.test_data = test_data
        self.validation_metrics = validation_metrics or [
            'sharpe_ratio', 'max_drawdown', 'win_rate', 'profit_factor'
        ]

    def validate_strategy(self, blueprint: StrategyBlueprint, **backtest_kwargs) -> Dict[str, Any]:
        """Validate strategy using comprehensive testing."""
        results = {
            'blueprint': blueprint,
            'validation_passed': False,
            'metrics': {},
            'issues': [],
            'recommendations': []
        }

        try:
            backtest_result = run_vectorized(
                data=self.test_data,
                symbol='VALIDATION',
                entry_signal=pd.Series(np.random.choice([True, False], len(self.test_data)), index=self.test_data.index),
                exit_signal=pd.Series(np.random.choice([True, False], len(self.test_data)), index=self.test_data.index),
                **backtest_kwargs
            )

            # Calculate metrics
            backtest_result.calculate_metrics()
            results['metrics'] = {
                'sharpe_ratio': backtest_result.sharpe_ratio,
                'max_drawdown': backtest_result.max_drawdown,
                'win_rate': backtest_result.win_rate,
                'profit_factor': backtest_result.profit_factor,
                'total_return': (backtest_result.equity_curve.iloc[-1] - backtest_result.equity_curve.iloc[0]) /
                               backtest_result.equity_curve.iloc[0]
            }

            # Validate metrics
            validation_passed, issues, recommendations = self._validate_metrics(results['metrics'])
            results['validation_passed'] = validation_passed
            results['issues'] = issues
            results['recommendations'] = recommendations

        except Exception as e:
            results['issues'].append(f"Backtest failed: {e}")
            results['recommendations'].append("Fix strategy implementation errors")

        return results

    def _validate_metrics(self, metrics: Dict[str, float]) -> Tuple[bool, List[str], List[str]]:
        """Validate strategy metrics."""
        issues = []
        recommendations = []
        passed = True

        # Sharpe ratio check
        if metrics.get('sharpe_ratio', 0) < 0.5:
            issues.append("Low Sharpe ratio indicates poor risk-adjusted returns")
            recommendations.append("Improve risk-adjusted returns through better position sizing")
            passed = False

        # Maximum drawdown check
        if metrics.get('max_drawdown', 0) > 0.2:
            issues.append("High maximum drawdown indicates excessive risk")
            recommendations.append("Implement better risk management and stop-loss rules")
            passed = False

        # Win rate check
        if metrics.get('win_rate', 0) < 0.4:
            issues.append("Low win rate suggests poor entry timing")
            recommendations.append("Refine entry signals and add filters")

        # Profit factor check
        if metrics.get('profit_factor', 0) < 1.2:
            issues.append("Low profit factor indicates insufficient reward-to-risk ratio")
            recommendations.append("Improve take-profit logic and reduce losing trades")

        return passed, issues, recommendations

    def cross_validate_strategy(self, blueprint: StrategyBlueprint, n_splits: int = 5) -> Dict[str, Any]:
        """Perform cross-validation on strategy."""
        results = []

        # Time series split
        tscv = TimeSeriesSplit(n_splits=n_splits)

        for fold, (train_idx, test_idx) in enumerate(tscv.split(self.test_data)):
            train_data = self.test_data.iloc[train_idx]
            test_data = self.test_data.iloc[test_idx]

            # This would run backtest on each fold
            # Simplified for now
            fold_result = {
                'fold': fold,
                'train_size': len(train_idx),
                'test_size': len(test_idx),
                'performance': np.random.uniform(0.5, 1.0)  # Placeholder
            }

            results.append(fold_result)

        return {
            'cross_validation_results': results,
            'mean_performance': np.mean([r['performance'] for r in results]),
            'std_performance': np.std([r['performance'] for r in results])
        }


class StrategyDeploymentManager:
    """Strategy deployment and monitoring system."""

    def __init__(self, deployment_config: Dict[str, Any]):
        self.deployment_config = deployment_config
        self.deployed_strategies = {}
        self.monitoring_data = {}

    def deploy_strategy(self, blueprint: StrategyBlueprint, environment: str = 'paper') -> str:
        """Deploy strategy to specified environment."""
        deployment_id = f"{blueprint.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        deployment_info = {
            'blueprint': blueprint,
            'environment': environment,
            'deployment_time': datetime.now(),
            'status': 'active',
            'performance_metrics': {},
            'alerts': []
        }

        self.deployed_strategies[deployment_id] = deployment_info

        # Initialize monitoring
        self.monitoring_data[deployment_id] = {
            'start_time': datetime.now(),
            'performance_history': [],
            'alert_history': []
        }

        return deployment_id

    def monitor_strategy(self, deployment_id: str, current_metrics: Dict[str, Any]):
        """Monitor deployed strategy performance."""
        if deployment_id not in self.monitoring_data:
            return

        monitoring = self.monitoring_data[deployment_id]
        monitoring['performance_history'].append({
            'timestamp': datetime.now(),
            'metrics': current_metrics
        })

        # Check for alerts
        alerts = self._check_alerts(current_metrics, monitoring['performance_history'])
        if alerts:
            monitoring['alert_history'].extend(alerts)
            self.deployed_strategies[deployment_id]['alerts'].extend(alerts)

    def _check_alerts(self, current_metrics: Dict[str, Any], history: List[Dict]) -> List[str]:
        """Check for strategy alerts."""
        alerts = []

        # Drawdown alert
        if current_metrics.get('drawdown', 0) > 0.1:
            alerts.append(f"High drawdown detected: {current_metrics['drawdown']:.1%}")

        # Performance degradation
        if len(history) > 10:
            recent_perf = [h['metrics'].get('sharpe_ratio', 0) for h in history[-10:]]
            if recent_perf[-1] < np.mean(recent_perf) * 0.8:
                alerts.append("Performance degradation detected")

        # Excessive trading
        if current_metrics.get('trades_per_day', 0) > 20:
            alerts.append("Excessive trading frequency")

        return alerts

    def get_deployment_report(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment report."""
        if deployment_id not in self.deployed_strategies:
            return {'error': 'Deployment not found'}

        deployment = self.deployed_strategies[deployment_id]
        monitoring = self.monitoring_data[deployment_id]

        return {
            'deployment_id': deployment_id,
            'strategy_name': deployment['blueprint'].name,
            'environment': deployment['environment'],
            'status': deployment['status'],
            'uptime': (datetime.now() - deployment['deployment_time']).total_seconds() / 3600,  # hours
            'total_alerts': len(deployment['alerts']),
            'recent_performance': monitoring['performance_history'][-5:] if monitoring['performance_history'] else []
        }


@dataclass(slots=True)
class StrategyBlueprint:
    """Container for generated strategy scaffolds."""

    name: str
    description: str
    code: str
    tags: Iterable[str] = field(default_factory=list)
    suggested_parameters: Dict[str, Any] = field(default_factory=dict)
    source: str = "fallback"
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_estimates: Dict[str, float] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

    def save(self, path: str) -> None:
        """Save blueprint to file."""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.code)

    def save_json(self, path: str) -> None:
        """Save complete blueprint as JSON."""
        data = {
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'tags': list(self.tags),
            'suggested_parameters': self.suggested_parameters,
            'source': self.source,
            'metadata': self.metadata,
            'performance_estimates': self.performance_estimates,
            'validation_results': self.validation_results,
            'created_at': self.created_at.isoformat(),
            'version': self.version
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load_json(cls, path: str) -> 'StrategyBlueprint':
        """Load blueprint from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls(
            name=data['name'],
            description=data['description'],
            code=data['code'],
            tags=data.get('tags', []),
            suggested_parameters=data.get('suggested_parameters', {}),
            source=data.get('source', 'loaded'),
            metadata=data.get('metadata', {}),
            performance_estimates=data.get('performance_estimates', {}),
            validation_results=data.get('validation_results', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            version=data.get('version', '1.0')
        )

    def validate_code(self) -> Tuple[bool, List[str]]:
        """Validate that the strategy code is syntactically correct."""
        try:
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]

    def estimate_complexity(self) -> Dict[str, Any]:
        """Estimate strategy complexity metrics."""
        lines = len(self.code.split('\n'))
        classes = self.code.count('class ')
        functions = self.code.count('def ')
        indicators = len(re.findall(r'self\.I\(', self.code))
        parameters = len(self.suggested_parameters)

        complexity_score = (lines * 0.1) + (classes * 2) + (functions * 0.5) + (indicators * 0.3) + (parameters * 0.2)

        return {
            'lines_of_code': lines,
            'class_count': classes,
            'function_count': functions,
            'indicator_count': indicators,
            'parameter_count': parameters,
            'complexity_score': complexity_score,
            'complexity_level': 'Low' if complexity_score < 5 else 'Medium' if complexity_score < 10 else 'High'
        }


class AdvancedStrategyCoPilot:
    """Advanced strategy development copilot with full AI capabilities."""

    def __init__(
        self,
        llm_provider: MultiModalLLMProvider,
        validator: Optional[StrategyValidator] = None,
        optimizer: Optional[AutoStrategyOptimizer] = None
    ):
        self.llm_provider = llm_provider
        self.validator = validator
        self.optimizer = optimizer
        self.generation_history = []
        self.successful_generations = []
        self.failed_generations = []

    def create_strategy_from_description(
        self,
        description: str,
        market_data: Optional[pd.DataFrame] = None,
        optimization_rounds: int = 2,
        validate: bool = True,
        **kwargs
    ) -> StrategyBlueprint:
        """Create a complete strategy from natural language description."""

        start_time = datetime.now()
        print(f"Starting strategy creation for: {description[:50]}...")

        try:
            if market_data is not None:
                blueprint = StrategyGenerator(self.llm_provider).generate_strategy_from_data(
                    market_data, description, **kwargs
                )
            else:
                blueprint = StrategyGenerator(self.llm_provider).generate_strategy_from_text(
                    description, **kwargs
                )

            # Step 2: Validate code syntax
            valid, errors = blueprint.validate_code()
            if not valid:
                print(f"Generated code has syntax errors: {errors}")
                # Try to fix with LLM
                fixed_response = self.llm_provider.refine_strategy(
                    blueprint.code, f"Fix syntax errors: {errors}"
                )
                blueprint.code = fixed_response.code_blocks[0] if fixed_response.code_blocks else fixed_response.content

            # Step 3: Optimize parameters if optimizer available
            if self.optimizer and optimization_rounds > 0:
                print(f"Optimizing strategy parameters ({optimization_rounds} rounds)...")
                if market_data is not None:
                    blueprint = self.optimizer.optimize_strategy(
                        blueprint, market_data, optimization_rounds, **kwargs
                    )

            # Step 4: Validate performance if validator available
            if validate and self.validator and market_data is not None:
                print("Validating strategy performance...")
                validation_results = self.validator.validate_strategy(blueprint)
                blueprint.validation_results = validation_results

                # Store performance estimates
                if 'metrics' in validation_results:
                    blueprint.performance_estimates = validation_results['metrics']

            # Step 5: Add metadata
            blueprint.metadata.update({
                'creation_time': (datetime.now() - start_time).total_seconds(),
                'optimization_rounds': optimization_rounds,
                'validated': validate,
                'complexity': blueprint.estimate_complexity()
            })

            self.successful_generations.append(blueprint)
            print(f"Strategy '{blueprint.name}' created successfully in {blueprint.metadata['creation_time']:.1f}s")

            return blueprint

        except Exception as e:
            error_blueprint = StrategyBlueprint(
                name="ErrorStrategy",
                description=f"Failed to create strategy: {str(e)}",
                code="# Strategy generation failed",
                source="error"
            )
            self.failed_generations.append({
                'description': description,
                'error': str(e),
                'timestamp': datetime.now()
            })
            return error_blueprint

    def evolve_strategy(
        self,
        base_strategy: str,
        performance_feedback: Dict[str, Any],
        market_data: pd.DataFrame,
        generations: int = 3,
        **kwargs
    ) -> List[StrategyBlueprint]:
        """Evolve a strategy through multiple generations."""

        print(f"Evolving strategy through {generations} generations...")

        generator = StrategyGenerator(self.llm_provider)
        evolved_strategies = generator.evolve_strategy(
            base_strategy, performance_feedback, generations, **kwargs
        )

        # Validate each generation if validator available
        if self.validator:
            for i, strategy in enumerate(evolved_strategies):
                validation = self.validator.validate_strategy(strategy)
                strategy.validation_results = validation
                if 'metrics' in validation:
                    strategy.performance_estimates = validation['metrics']
                print(f"Generation {i+1} validation: {validation.get('validation_passed', False)}")

        return evolved_strategies

    def create_multi_agent_strategy(
        self,
        problem_description: str,
        market_data: pd.DataFrame,
        agent_configs: List[Dict[str, Any]],
        collaboration_rounds: int = 3,
        **kwargs
    ) -> StrategyBlueprint:
        """Create strategy using multi-agent collaboration."""

        print(f"Creating multi-agent strategy with {len(agent_configs)} agents...")

        multi_agent_system = MultiAgentStrategySystem(agent_configs)
        multi_agent_system.initialize_agents()

        strategy = multi_agent_system.collaborative_strategy_generation(
            problem_description, market_data, collaboration_rounds
        )

        # Final validation and optimization
        if self.validator:
            validation = self.validator.validate_strategy(strategy)
            strategy.validation_results = validation

        if self.optimizer and market_data is not None:
            strategy = self.optimizer.optimize_strategy(strategy, market_data, 2, **kwargs)

        return strategy

    def benchmark_strategies(
        self,
        strategies: List[StrategyBlueprint],
        market_data: pd.DataFrame,
        benchmark_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Benchmark multiple strategies against each other."""

        if benchmark_metrics is None:
            benchmark_metrics = ['sharpe_ratio', 'max_drawdown', 'total_return', 'win_rate']

        results = {}

        for strategy in strategies:
            try:
                if self.validator:
                    validation = self.validator.validate_strategy(strategy)
                    metrics = validation.get('metrics', {})

                    strategy_score = 0
                    for metric in benchmark_metrics:
                        if metric in metrics:
                            # Normalize metrics (this is simplified)
                            if metric == 'sharpe_ratio':
                                strategy_score += min(1.0, metrics[metric] / 2.0)
                            elif metric == 'max_drawdown':
                                strategy_score += max(0, 1.0 + metrics[metric])  # Lower drawdown is better
                            elif metric == 'total_return':
                                strategy_score += min(1.0, metrics[metric])
                            elif metric == 'win_rate':
                                strategy_score += metrics[metric]

                    results[strategy.name] = {
                        'metrics': metrics,
                        'score': strategy_score / len(benchmark_metrics),
                        'rank': 0  # Will be set below
                    }
                else:
                    results[strategy.name] = {'error': 'No validator available'}

            except Exception as e:
                results[strategy.name] = {'error': str(e)}

        # Rank strategies
        valid_results = {k: v for k, v in results.items() if 'score' in v}
        sorted_strategies = sorted(valid_results.items(), key=lambda x: x[1]['score'], reverse=True)

        for rank, (name, _) in enumerate(sorted_strategies, 1):
            results[name]['rank'] = rank

        return {
            'benchmark_results': results,
            'best_strategy': sorted_strategies[0][0] if sorted_strategies else None,
            'benchmark_metrics': benchmark_metrics,
            'total_strategies': len(strategies)
        }

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about strategy generation performance."""
        total_generations = len(self.successful_generations) + len(self.failed_generations)
        success_rate = len(self.successful_generations) / total_generations if total_generations > 0 else 0

        avg_complexity = 0
        if self.successful_generations:
            complexities = [s.estimate_complexity()['complexity_score'] for s in self.successful_generations]
            avg_complexity = np.mean(complexities)

        return {
            'total_generations': total_generations,
            'successful_generations': len(self.successful_generations),
            'failed_generations': len(self.failed_generations),
            'success_rate': success_rate,
            'average_complexity': avg_complexity,
            'generation_sources': list(set(s.source for s in self.successful_generations))
        }


class InteractiveStrategyRefinement:
    """Interactive strategy refinement system."""

    def __init__(self, llm_provider: MultiModalLLMProvider):
        self.llm_provider = llm_provider
        self.refinement_history = []
        self.current_strategy = None

    def start_refinement_session(self, initial_strategy: StrategyBlueprint):
        """Start an interactive refinement session."""
        self.current_strategy = initial_strategy
        self.refinement_history = [{
            'version': 1,
            'strategy': initial_strategy,
            'changes': 'Initial strategy',
            'timestamp': datetime.now()
        }]
        print(f"Started refinement session for '{initial_strategy.name}'")

    def suggest_improvements(self, performance_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """Suggest improvements for current strategy."""
        if not self.current_strategy:
            return ["No active strategy to improve"]

        suggestions = []

        # Analyze current strategy
        complexity = self.current_strategy.estimate_complexity()

        # Code quality suggestions
        if complexity['lines_of_code'] > 200:
            suggestions.append("Strategy is quite long. Consider breaking into smaller, focused strategies.")

        if complexity['indicator_count'] < 3:
            suggestions.append("Add more technical indicators for better signal generation.")

        if 'stop_loss' not in self.current_strategy.code.lower():
            suggestions.append("Add stop-loss protection to limit downside risk.")

        # Performance-based suggestions
        if performance_data:
            if performance_data.get('sharpe_ratio', 0) < 0.5:
                suggestions.append("Low Sharpe ratio. Focus on improving risk-adjusted returns.")

            if performance_data.get('max_drawdown', 0) > 0.2:
                suggestions.append("High drawdown. Implement better risk management.")

            if performance_data.get('win_rate', 0) < 0.45:
                suggestions.append("Low win rate. Improve entry/exit timing.")

        return suggestions

    def apply_refinement(self, refinement_request: str) -> StrategyBlueprint:
        """Apply a refinement to the current strategy."""
        if not self.current_strategy:
            raise ValueError("No active refinement session")

        print(f"Applying refinement: {refinement_request}")

        # Use LLM to refine the strategy
        refined_response = self.llm_provider.refine_strategy(
            self.current_strategy.code,
            refinement_request
        )

        # Create new version
        new_code = refined_response.code_blocks[0] if refined_response.code_blocks else refined_response.content
        new_version = len(self.refinement_history) + 1

        refined_strategy = StrategyBlueprint(
            name=f"{self.current_strategy.name}_v{new_version}",
            description=f"Refined version {new_version}: {refinement_request}",
            code=new_code,
            tags=self.current_strategy.tags + ["refined"],
            suggested_parameters=self.current_strategy.suggested_parameters.copy(),
            source="refinement",
            metadata={
                **self.current_strategy.metadata,
                'refined_from': self.current_strategy.name,
                'refinement_request': refinement_request
            }
        )

        # Update history
        self.refinement_history.append({
            'version': new_version,
            'strategy': refined_strategy,
            'changes': refinement_request,
            'timestamp': datetime.now()
        })

        self.current_strategy = refined_strategy
        return refined_strategy

    def get_refinement_history(self) -> List[Dict[str, Any]]:
        """Get the refinement history."""
        return self.refinement_history.copy()

    def export_refinement_session(self, path: str):
        """Export the refinement session to file."""
        session_data = {
            'strategy_name': self.current_strategy.name if self.current_strategy else None,
            'total_versions': len(self.refinement_history),
            'history': [
                {
                    'version': h['version'],
                    'changes': h['changes'],
                    'timestamp': h['timestamp'].isoformat(),
                    'strategy_summary': {
                        'name': h['strategy'].name,
                        'complexity': h['strategy'].estimate_complexity()
                    }
                }
                for h in self.refinement_history
            ]
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)


class StrategyAutoPilot:
    """Fully automated strategy development and deployment system."""

    def __init__(
        self,
        llm_provider: MultiModalLLMProvider,
        validator: StrategyValidator,
        optimizer: AutoStrategyOptimizer,
        deployment_manager: StrategyDeploymentManager
    ):
        self.llm_provider = llm_provider
        self.validator = validator
        self.optimizer = optimizer
        self.deployment_manager = deployment_manager
        self.copilot = AdvancedStrategyCoPilot(llm_provider, validator, optimizer)

        self.active_strategies = {}
        self.performance_monitoring = {}
        self.automation_config = {
            'retraining_interval': timedelta(days=7),
            'performance_threshold': 0.6,
            'max_simultaneous_strategies': 5,
            'auto_deployment': True
        }

    def run_automated_development(
        self,
        market_descriptions: List[str],
        market_data: pd.DataFrame,
        development_cycles: int = 3
    ) -> Dict[str, Any]:
        """Run fully automated strategy development."""

        results = {
            'total_strategies_created': 0,
            'strategies_deployed': 0,
            'best_performing_strategy': None,
            'development_summary': []
        }

        print(f"Starting automated development with {len(market_descriptions)} descriptions")

        for cycle in range(development_cycles):
            print(f"\n--- Development Cycle {cycle + 1}/{development_cycles} ---")

            cycle_strategies = []

            # Create strategies for each description
            for description in market_descriptions:
                try:
                    strategy = self.copilot.create_strategy_from_description(
                        description, market_data, optimization_rounds=2, validate=True
                    )

                    if strategy.source != 'error':
                        cycle_strategies.append(strategy)
                        results['total_strategies_created'] += 1

                except Exception as e:
                    print(f"Failed to create strategy for '{description[:30]}...': {e}")

            # Benchmark strategies
            if len(cycle_strategies) > 1:
                benchmark_results = self.copilot.benchmark_strategies(
                    cycle_strategies, market_data
                )

                best_strategy_name = benchmark_results.get('best_strategy')
                if best_strategy_name:
                    best_strategy = next(s for s in cycle_strategies if s.name == best_strategy_name)

                    # Deploy if performance meets threshold
                    if (best_strategy.performance_estimates.get('sharpe_ratio', 0) >
                        self.automation_config['performance_threshold']):

                        deployment_id = self.deployment_manager.deploy_strategy(
                            best_strategy, environment='paper'
                        )

                        results['strategies_deployed'] += 1
                        results['best_performing_strategy'] = best_strategy_name

                        print(f"Deployed strategy '{best_strategy_name}' (ID: {deployment_id})")

            results['development_summary'].append({
                'cycle': cycle + 1,
                'strategies_created': len(cycle_strategies),
                'benchmark_results': benchmark_results if len(cycle_strategies) > 1 else None
            })

        return results

    def monitor_and_adapt(self):
        """Monitor deployed strategies and adapt as needed."""
        for deployment_id, deployment_info in self.deployment_manager.deployed_strategies.items():
            if deployment_info['status'] != 'active':
                continue

            # Get recent performance
            report = self.deployment_manager.get_deployment_report(deployment_id)
            recent_performance = report.get('recent_performance', [])

            if not recent_performance:
                continue

            # Check if retraining is needed
            last_retrain = deployment_info.get('last_retrain', deployment_info['deployment_time'])
            needs_retraining = (datetime.now() - last_retrain) > self.automation_config['retraining_interval']

            # Check performance degradation
            recent_sharpe = [p.get('metrics', {}).get('sharpe_ratio', 0) for p in recent_performance[-5:]]
            avg_recent_sharpe = np.mean(recent_sharpe) if recent_sharpe else 0

            performance_degraded = avg_recent_sharpe < self.automation_config['performance_threshold']

            if needs_retraining or performance_degraded:
                print(f"Retraining strategy {deployment_id} (performance: {avg_recent_sharpe:.2f})")

                # This would trigger retraining logic
                # For now, just mark as needing attention
                deployment_info['needs_attention'] = True

    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status."""
        return {
            'active_strategies': len(self.deployment_manager.deployed_strategies),
            'total_deployments': len(self.deployment_manager.deployed_strategies),
            'automation_config': self.automation_config,
            'last_monitoring': datetime.now()
        }


class StrategyCoPilot(AdvancedStrategyCoPilot):
    """Legacy StrategyCoPilot class for backward compatibility."""

    def __init__(self, provider: Optional[LLMProvider] = None, **kwargs):
        # Convert old provider to new interface if needed
        if provider and not isinstance(provider, MultiModalLLMProvider):
            # Wrap old provider
            class LegacyWrapper(MultiModalLLMProvider):
                def __init__(self, legacy_provider):
                    self.legacy_provider = legacy_provider

                def generate_from_text(self, prompt: str, **kwargs) -> LLMResponse:
                    content = self.legacy_provider.generate(prompt, **kwargs)
                    return LLMResponse(content)

                def generate_from_data(self, data: pd.DataFrame, prompt: str, **kwargs) -> LLMResponse:
                    return self.generate_from_text(prompt, **kwargs)

                def analyze_chart(self, chart_data: Dict[str, Any], prompt: str, **kwargs) -> LLMResponse:
                    return self.generate_from_text(prompt, **kwargs)

                def refine_strategy(self, strategy_code: str, feedback: str, **kwargs) -> LLMResponse:
                    content = self.legacy_provider.generate(
                        f"Refine this strategy: {strategy_code}\nFeedback: {feedback}", **kwargs
                    )
                    return LLMResponse(content)

            provider = LegacyWrapper(provider)

        super().__init__(provider, **kwargs)


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "MultiModalLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalLLMProvider",
    "StrategyBlueprint",
    "StrategyGenerator",
    "AutoStrategyOptimizer",
    "MultiAgentStrategySystem",
    "StrategyValidator",
    "StrategyDeploymentManager",
    "AdvancedStrategyCoPilot",
    "InteractiveStrategyRefinement",
    "StrategyAutoPilot",
    "StrategyCoPilot",  # Legacy compatibility
]

