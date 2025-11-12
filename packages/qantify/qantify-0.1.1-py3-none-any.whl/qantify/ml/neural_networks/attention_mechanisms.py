"""
Advanced Attention Mechanisms for Financial Time Series
=====================================================

This module implements state-of-the-art attention mechanisms specifically designed for financial data analysis.
Includes temporal attention, multi-head attention, self-attention, and cross-modal attention for trading signals.

Key Features:
- Temporal attention for time series patterns
- Multi-head self-attention for market microstructure
- Hierarchical attention for multi-timeframe analysis
- Cross-attention between different asset classes
- Sparse attention for efficient long-range dependencies
- Attention-based feature selection
- Risk-aware attention weights
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Neural network dependencies
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None


@dataclass
class AttentionConfig:
    """Configuration for attention mechanisms"""

    # Architecture
    d_model: int = 128  # Model dimension
    n_heads: int = 8    # Number of attention heads
    d_k: int = 16       # Key dimension per head
    d_v: int = 16       # Value dimension per head
    dropout: float = 0.1

    # Sequence parameters
    max_seq_len: int = 1000
    use_relative_positional_encoding: bool = True
    positional_encoding_type: str = "sinusoidal"  # "sinusoidal", "learned", "none"

    # Attention types
    attention_type: str = "multihead"  # "multihead", "temporal", "sparse", "hierarchical"
    use_masking: bool = True
    causal_masking: bool = False  # For autoregressive models

    # Advanced features
    use_layer_norm: bool = True
    use_residual: bool = True
    use_feedforward: bool = True
    feedforward_dim: int = 256

    # Sparse attention
    sparsity_factor: float = 0.1  # Fraction of connections to keep
    block_size: int = 32  # For block sparse attention

    # Training
    use_gpu: bool = True
    device: Optional[str] = None


class ScaledDotProductAttention(nn.Module if TORCH_AVAILABLE else object):
    """Scaled dot-product attention mechanism"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for ScaledDotProductAttention")

        super().__init__()
        self.config = config
        self.dropout = nn.Dropout(config.dropout)
        self.scale = np.sqrt(config.d_k)

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query: (batch_size, n_heads, seq_len, d_k)
            key: (batch_size, n_heads, seq_len, d_k)
            value: (batch_size, n_heads, seq_len, d_v)
            mask: (batch_size, seq_len, seq_len) or None

        Returns:
            attended_output: (batch_size, n_heads, seq_len, d_v)
            attention_weights: (batch_size, n_heads, seq_len, seq_len)
        """

        # Compute attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / self.scale

        # Apply mask
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Softmax and dropout
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention to values
        attended_output = torch.matmul(attention_weights, value)

        return attended_output, attention_weights


class MultiHeadAttention(nn.Module if TORCH_AVAILABLE else object):
    """Multi-head attention mechanism"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for MultiHeadAttention")

        super().__init__()
        self.config = config
        self.n_heads = config.n_heads
        self.d_model = config.d_model
        self.d_k = config.d_k
        self.d_v = config.d_v

        # Linear layers for Q, K, V
        self.w_q = nn.Linear(config.d_model, config.n_heads * config.d_k)
        self.w_k = nn.Linear(config.d_model, config.n_heads * config.d_k)
        self.w_v = nn.Linear(config.d_model, config.n_heads * config.d_v)
        self.w_o = nn.Linear(config.n_heads * config.d_v, config.d_model)

        # Attention mechanism
        self.attention = ScaledDotProductAttention(config)

        # Layer norm and dropout
        if config.use_layer_norm:
            self.layer_norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query: (batch_size, seq_len, d_model)
            key: (batch_size, seq_len, d_model)
            value: (batch_size, seq_len, d_model)
            mask: (batch_size, seq_len, seq_len) or None

        Returns:
            output: (batch_size, seq_len, d_model)
            attention_weights: (batch_size, n_heads, seq_len, seq_len)
        """

        batch_size = query.size(0)

        # Linear transformations and reshape
        Q = self.w_q(query).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.n_heads, self.d_v).transpose(1, 2)

        # Apply attention
        attended_output, attention_weights = self.attention(Q, K, V, mask)

        # Concatenate heads and final linear layer
        attended_output = attended_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.n_heads * self.d_v)
        output = self.w_o(attended_output)

        # Residual connection and layer norm
        if self.config.use_residual:
            output = output + query  # Residual with original query

        if self.config.use_layer_norm:
            output = self.layer_norm(output)

        output = self.dropout(output)

        return output, attention_weights


class TemporalAttention(nn.Module if TORCH_AVAILABLE else object):
    """Temporal attention for time series patterns"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for TemporalAttention")

        super().__init__()
        self.config = config

        # Time encoding
        self.time_encoding = nn.Linear(1, config.d_model)

        # Attention layers
        self.self_attention = MultiHeadAttention(config)

        # Feed-forward network
        if config.use_feedforward:
            self.feedforward = nn.Sequential(
                nn.Linear(config.d_model, config.feedforward_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout),
                nn.Linear(config.feedforward_dim, config.d_model)
            )

        # Positional encoding
        if config.use_relative_positional_encoding:
            self.positional_encoding = self._create_positional_encoding()

    def _create_positional_encoding(self) -> torch.Tensor:
        """Create sinusoidal positional encoding"""
        position = torch.arange(0, self.config.max_seq_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, self.config.d_model, 2).float() *
                           (-np.log(10000.0) / self.config.d_model))

        pos_encoding = torch.zeros(self.config.max_seq_len, self.config.d_model)
        pos_encoding[:, 0::2] = torch.sin(position * div_term)
        pos_encoding[:, 1::2] = torch.cos(position * div_term)

        return pos_encoding.unsqueeze(0)  # Add batch dimension

    def forward(self, x: torch.Tensor, timestamps: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch_size, seq_len, d_model)
            timestamps: (batch_size, seq_len) or None

        Returns:
            output: (batch_size, seq_len, d_model)
            attention_weights: (batch_size, n_heads, seq_len, seq_len)
        """

        batch_size, seq_len, _ = x.size()

        # Add positional encoding
        if self.config.use_relative_positional_encoding and hasattr(self, 'positional_encoding'):
            pos_encoding = self.positional_encoding[:, :seq_len, :].to(x.device)
            x = x + pos_encoding

        # Add temporal features
        if timestamps is not None:
            time_features = self.time_encoding(timestamps.unsqueeze(-1))
            x = x + time_features

        # Self-attention
        attended_output, attention_weights = self.self_attention(x, x, x)

        # Feed-forward network
        if self.config.use_feedforward:
            ff_output = self.feedforward(attended_output)

            # Residual connection
            if self.config.use_residual:
                ff_output = ff_output + attended_output

            if self.config.use_layer_norm:
                ff_output = nn.LayerNorm(self.config.d_model).to(x.device)(ff_output)

            attended_output = ff_output

        return attended_output, attention_weights


class SparseAttention(nn.Module if TORCH_AVAILABLE else object):
    """Sparse attention for efficient long-range dependencies"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for SparseAttention")

        super().__init__()
        self.config = config

        # Sparse attention parameters
        self.sparsity_factor = config.sparsity_factor
        self.block_size = config.block_size

        # Standard attention for comparison
        self.attention = ScaledDotProductAttention(config)

    def _create_sparse_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create sparse attention mask"""

        # Random sparse pattern
        mask = torch.rand(seq_len, seq_len, device=device) < self.sparsity_factor
        mask = mask.float()

        # Ensure self-attention (diagonal)
        diag_mask = torch.eye(seq_len, device=device)
        mask = torch.maximum(mask, diag_mask)

        return mask

    def _create_block_sparse_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create block sparse attention mask"""

        mask = torch.zeros(seq_len, seq_len, device=device)

        for i in range(0, seq_len, self.block_size):
            for j in range(0, seq_len, self.block_size):
                if abs(i - j) <= self.block_size:  # Adjacent blocks
                    block_i_end = min(i + self.block_size, seq_len)
                    block_j_end = min(j + self.block_size, seq_len)
                    mask[i:block_i_end, j:block_j_end] = 1.0

        return mask

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query: (batch_size, n_heads, seq_len, d_k)
            key: (batch_size, n_heads, seq_len, d_k)
            value: (batch_size, n_heads, seq_len, d_v)

        Returns:
            attended_output: (batch_size, n_heads, seq_len, d_v)
            attention_weights: (batch_size, n_heads, seq_len, seq_len)
        """

        batch_size, n_heads, seq_len, _ = query.size()
        device = query.device

        # Create sparse mask
        if self.block_size > 0:
            sparse_mask = self._create_block_sparse_mask(seq_len, device)
        else:
            sparse_mask = self._create_sparse_mask(seq_len, device)

        # Expand mask for batch and heads
        sparse_mask = sparse_mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, seq_len)

        # Apply sparse attention
        attended_output, attention_weights = self.attention(query, key, value, sparse_mask)

        return attended_output, attention_weights


class HierarchicalAttention(nn.Module if TORCH_AVAILABLE else object):
    """Hierarchical attention for multi-timeframe analysis"""

    def __init__(self, config: AttentionConfig, n_levels: int = 3):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for HierarchicalAttention")

        super().__init__()
        self.config = config
        self.n_levels = n_levels

        # Attention layers for each level
        self.level_attentions = nn.ModuleList([
            MultiHeadAttention(config) for _ in range(n_levels)
        ])

        # Cross-level attention
        self.cross_level_attention = MultiHeadAttention(config)

        # Pooling operations
        self.pooling = nn.AdaptiveAvgPool1d(1)

    def forward(self, multi_level_inputs: List[torch.Tensor]) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Args:
            multi_level_inputs: List of tensors, each (batch_size, seq_len, d_model)
                               Different levels have different timescales

        Returns:
            final_output: (batch_size, d_model)
            level_outputs: List of level-specific outputs
        """

        level_outputs = []

        # Process each level
        for i, level_input in enumerate(multi_level_inputs):
            level_output, _ = self.level_attentions[i](level_input, level_input, level_input)
            level_outputs.append(level_output)

        # Cross-level attention
        # Use finest level as query, others as key/value
        query = level_outputs[0]  # Finest timescale
        key = torch.cat(level_outputs[1:], dim=1)  # Coarser timescales
        value = key

        cross_output, _ = self.cross_level_attention(query, key, value)

        # Global pooling
        final_output = self.pooling(cross_output.transpose(1, 2)).squeeze(-1)

        return final_output, level_outputs


class CrossModalAttention(nn.Module if TORCH_AVAILABLE else object):
    """Cross-modal attention between different data types"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for CrossModalAttention")

        super().__init__()
        self.config = config

        # Modal-specific projections
        self.price_projection = nn.Linear(config.d_model, config.d_model)
        self.volume_projection = nn.Linear(config.d_model, config.d_model)
        self.sentiment_projection = nn.Linear(config.d_model, config.d_model)

        # Cross-modal attention
        self.cross_attention = MultiHeadAttention(config)

        # Fusion network
        self.fusion = nn.Sequential(
            nn.Linear(config.d_model * 3, config.d_model),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_model, config.d_model)
        )

    def forward(self, price_features: torch.Tensor, volume_features: torch.Tensor,
                sentiment_features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            price_features: (batch_size, seq_len, d_model)
            volume_features: (batch_size, seq_len, d_model)
            sentiment_features: (batch_size, seq_len, d_model)

        Returns:
            fused_output: (batch_size, seq_len, d_model)
        """

        # Project to common space
        price_proj = self.price_projection(price_features)
        volume_proj = self.volume_projection(volume_features)
        sentiment_proj = self.sentiment_projection(sentiment_features)

        # Cross-modal attention (price as query, others as key/value)
        attended_price, _ = self.cross_attention(price_proj, volume_proj, volume_proj)
        attended_price, _ = self.cross_attention(attended_price, sentiment_proj, sentiment_proj)

        # Concatenate all modalities
        concatenated = torch.cat([attended_price, volume_proj, sentiment_proj], dim=-1)

        # Fusion
        fused_output = self.fusion(concatenated)

        return fused_output


class AttentionBasedFeatureSelector(nn.Module if TORCH_AVAILABLE else object):
    """Attention-based feature selection for financial data"""

    def __init__(self, config: AttentionConfig, n_features: int):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for AttentionBasedFeatureSelector")

        super().__init__()
        self.config = config
        self.n_features = n_features

        # Feature attention
        self.feature_attention = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Linear(config.d_model // 2, 1),
            nn.Sigmoid()
        )

        # Feature transformation
        self.feature_transform = nn.Linear(n_features, config.d_model)

    def forward(self, features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            features: (batch_size, seq_len, n_features)

        Returns:
            selected_features: (batch_size, seq_len, d_model)
            attention_weights: (batch_size, seq_len, n_features)
        """

        batch_size, seq_len, _ = features.size()

        # Transform features to model dimension
        transformed = self.feature_transform(features)  # (batch_size, seq_len, d_model)

        # Compute attention weights for each feature
        attention_logits = self.feature_attention(transformed)  # (batch_size, seq_len, 1)
        attention_weights = torch.softmax(attention_logits, dim=-1)  # (batch_size, seq_len, 1)

        # Apply attention to original features
        selected_features = features * attention_weights.expand(-1, -1, self.n_features)

        return selected_features, attention_weights.squeeze(-1)


class RiskAwareAttention(nn.Module if TORCH_AVAILABLE else object):
    """Risk-aware attention mechanism"""

    def __init__(self, config: AttentionConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for RiskAwareAttention")

        super().__init__()
        self.config = config

        # Risk assessment network
        self.risk_assessment = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Linear(config.d_model // 2, 1),
            nn.Sigmoid()  # Risk score between 0 and 1
        )

        # Risk-adjusted attention
        self.attention = MultiHeadAttention(config)

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                risk_threshold: float = 0.5) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            query: (batch_size, seq_len, d_model)
            key: (batch_size, seq_len, d_model)
            value: (batch_size, seq_len, d_model)
            risk_threshold: Risk threshold for filtering

        Returns:
            output: (batch_size, seq_len, d_model)
            attention_weights: (batch_size, n_heads, seq_len, seq_len)
            risk_scores: (batch_size, seq_len)
        """

        # Assess risk for each position
        risk_scores = self.risk_assessment(query).squeeze(-1)

        # Create risk-based mask
        risk_mask = (risk_scores < risk_threshold).unsqueeze(-1).unsqueeze(-1)
        risk_mask = risk_mask.expand(-1, -1, query.size(1)).unsqueeze(1)  # Expand for heads

        # Apply attention with risk filtering
        output, attention_weights = self.attention(query, key, value, risk_mask)

        return output, attention_weights, risk_scores


class AttentionAnalyzer:
    """Analyzer for attention mechanisms in trading"""

    def __init__(self, config: AttentionConfig):
        self.config = config

    def analyze_attention_patterns(self, attention_weights: np.ndarray,
                                 feature_names: List[str]) -> Dict[str, Any]:
        """Analyze attention patterns for interpretability"""

        # Average attention across heads and batch
        avg_attention = np.mean(attention_weights, axis=(0, 1))  # (seq_len, seq_len)

        # Find most attended positions
        most_attended_positions = np.argmax(avg_attention, axis=-1)

        # Calculate attention entropy (diversity)
        attention_entropy = -np.sum(avg_attention * np.log(avg_attention + 1e-10), axis=-1)
        avg_entropy = np.mean(attention_entropy)

        # Identify attention clusters
        from sklearn.cluster import KMeans
        attention_flat = avg_attention.reshape(-1, 1)
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(attention_flat)

        return {
            'attention_matrix': avg_attention,
            'most_attended_positions': most_attended_positions,
            'attention_entropy': avg_entropy,
            'attention_clusters': clusters.reshape(avg_attention.shape),
            'feature_importance': self._calculate_feature_importance(avg_attention, feature_names)
        }

    def _calculate_feature_importance(self, attention_matrix: np.ndarray,
                                    feature_names: List[str]) -> Dict[str, float]:
        """Calculate feature importance from attention patterns"""

        # Sum attention weights for each position
        position_importance = np.sum(attention_matrix, axis=-1)

        # Map to feature names (assuming features are ordered)
        importance_dict = {}
        for i, name in enumerate(feature_names):
            if i < len(position_importance):
                importance_dict[name] = float(position_importance[i])

        return importance_dict

    def detect_attention_anomalies(self, attention_weights: np.ndarray,
                                 threshold: float = 2.0) -> List[Tuple[int, int, float]]:
        """Detect anomalous attention patterns"""

        anomalies = []
        avg_attention = np.mean(attention_weights, axis=(0, 1))

        # Calculate z-scores
        mean_attention = np.mean(avg_attention)
        std_attention = np.std(avg_attention)

        z_scores = (avg_attention - mean_attention) / (std_attention + 1e-10)

        # Find positions with high z-scores
        anomaly_positions = np.where(np.abs(z_scores) > threshold)

        for i, j in zip(anomaly_positions[0], anomaly_positions[1]):
            anomalies.append((int(i), int(j), float(z_scores[i, j])))

        return anomalies


# Factory functions
def create_multihead_attention(config: Optional[AttentionConfig] = None) -> MultiHeadAttention:
    """Factory function for multi-head attention"""
    if config is None:
        config = AttentionConfig()
    return MultiHeadAttention(config)


def create_temporal_attention(config: Optional[AttentionConfig] = None) -> TemporalAttention:
    """Factory function for temporal attention"""
    if config is None:
        config = AttentionConfig()
    return TemporalAttention(config)


def create_sparse_attention(config: Optional[AttentionConfig] = None) -> SparseAttention:
    """Factory function for sparse attention"""
    if config is None:
        config = AttentionConfig()
    return SparseAttention(config)


def create_hierarchical_attention(config: Optional[AttentionConfig] = None,
                                n_levels: int = 3) -> HierarchicalAttention:
    """Factory function for hierarchical attention"""
    if config is None:
        config = AttentionConfig()
    return HierarchicalAttention(config, n_levels)


def create_cross_modal_attention(config: Optional[AttentionConfig] = None) -> CrossModalAttention:
    """Factory function for cross-modal attention"""
    if config is None:
        config = AttentionConfig()
    return CrossModalAttention(config)


def create_risk_aware_attention(config: Optional[AttentionConfig] = None) -> RiskAwareAttention:
    """Factory function for risk-aware attention"""
    if config is None:
        config = AttentionConfig()
    return RiskAwareAttention(config)


def create_attention_analyzer(config: Optional[AttentionConfig] = None) -> AttentionAnalyzer:
    """Factory function for attention analyzer"""
    if config is None:
        config = AttentionConfig()
    return AttentionAnalyzer(config)


# Example usage and testing
if __name__ == "__main__":
    # Test attention mechanisms
    print("Testing Attention Mechanisms...")

    if TORCH_AVAILABLE:
        config = AttentionConfig()

        # Test multi-head attention
        print("\n1. Testing Multi-Head Attention...")
        mha = create_multihead_attention(config)

        # Create dummy input
        batch_size, seq_len, d_model = 2, 10, 128
        x = torch.randn(batch_size, seq_len, d_model)

        output, attention_weights = mha(x, x, x)
        print(f"Multi-head attention output shape: {output.shape}")
        print(f"Attention weights shape: {attention_weights.shape}")

        # Test temporal attention
        print("\n2. Testing Temporal Attention...")
        ta = create_temporal_attention(config)
        timestamps = torch.randn(batch_size, seq_len)

        output, attention_weights = ta(x, timestamps)
        print(f"Temporal attention output shape: {output.shape}")

        # Test attention analyzer
        print("\n3. Testing Attention Analyzer...")
        analyzer = create_attention_analyzer(config)
        feature_names = [f'feature_{i}' for i in range(seq_len)]

        analysis = analyzer.analyze_attention_patterns(attention_weights.detach().numpy(), feature_names)
        print(f"Attention entropy: {analysis['attention_entropy']:.4f}")
        print(f"Number of attention clusters: {len(np.unique(analysis['attention_clusters']))}")

        anomalies = analyzer.detect_attention_anomalies(attention_weights.detach().numpy())
        print(f"Detected {len(anomalies)} attention anomalies")

    else:
        print("PyTorch not available - Attention functionality disabled")
        print("Install PyTorch to enable attention mechanisms: pip install torch")
