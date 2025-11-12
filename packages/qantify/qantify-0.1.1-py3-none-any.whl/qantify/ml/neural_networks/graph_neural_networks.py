"""
Graph Neural Networks for Financial Asset Relationships
======================================================

This module implements Graph Neural Networks (GNNs) specifically designed for modeling
relationships between financial assets, market sectors, and economic indicators.

Key Features:
- Graph Convolutional Networks (GCN) for asset relationships
- Graph Attention Networks (GAT) for adaptive relationship learning
- Temporal Graph Networks for dynamic market structures
- Portfolio optimization using graph-based risk assessment
- Sector and industry relationship modeling
- Cross-asset correlation networks
- Market contagion modeling
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans

# Neural network dependencies
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch_geometric.nn import GCNConv, GATConv, SAGEConv
    from torch_geometric.data import Data, Batch
    from torch_geometric.utils import dense_to_sparse, add_self_loops
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None


@dataclass
class GraphConfig:
    """Configuration for Graph Neural Networks"""

    # Architecture
    gnn_type: str = "gcn"  # "gcn", "gat", "sage", "temporal_gnn"
    hidden_channels: List[int] = field(default_factory=lambda: [64, 128, 64])
    num_layers: int = 3
    dropout: float = 0.1

    # Attention parameters (for GAT)
    num_heads: int = 8
    concat_heads: bool = True

    # Temporal parameters (for temporal GNNs)
    time_steps: int = 10
    temporal_hidden: int = 32

    # Graph construction
    edge_threshold: float = 0.3  # Correlation threshold for edges
    max_edges_per_node: int = 10  # Maximum edges per node
    include_self_loops: bool = True

    # Node features
    node_feature_dim: int = 20  # Technical indicators, fundamentals, etc.
    edge_feature_dim: int = 5   # Correlation, distance, relationship strength

    # Training parameters
    batch_size: int = 32
    num_epochs: int = 100
    learning_rate: float = 0.001
    weight_decay: float = 1e-4

    # Hardware acceleration
    use_gpu: bool = True
    device: Optional[str] = None


@dataclass
class AssetNode:
    """Represents a financial asset node in the graph"""

    asset_id: str
    asset_type: str  # "stock", "bond", "commodity", "currency", "crypto"
    sector: str
    industry: str
    market_cap: float
    features: np.ndarray  # Technical and fundamental features

    def to_tensor(self) -> torch.Tensor:
        """Convert node features to tensor"""
        if TORCH_AVAILABLE:
            return torch.FloatTensor(self.features)
        return self.features


@dataclass
class AssetRelationship:
    """Represents relationship between assets"""

    source_asset: str
    target_asset: str
    relationship_type: str  # "correlation", "sector", "industry", "geographic"
    strength: float
    direction: str  # "positive", "negative", "neutral"

    # Additional features
    distance: float = 0.0  # Geographic or economic distance
    beta: float = 1.0      # Beta coefficient
    volatility: float = 0.0  # Relationship volatility

    def to_edge_features(self) -> np.ndarray:
        """Convert relationship to edge features"""
        return np.array([
            self.strength,
            1 if self.direction == "positive" else -1 if self.direction == "negative" else 0,
            self.distance,
            self.beta,
            self.volatility
        ])


class FinancialGraphConstructor:
    """Constructs financial asset relationship graphs"""

    def __init__(self, config: GraphConfig):
        self.config = config

    def construct_correlation_graph(self, asset_data: pd.DataFrame,
                                  asset_metadata: Dict[str, AssetNode]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Construct graph based on asset correlations

        Args:
            asset_data: DataFrame with asset returns (assets as columns)
            asset_metadata: Dictionary mapping asset IDs to AssetNode objects

        Returns:
            node_features: (num_nodes, feature_dim)
            edge_index: (2, num_edges)
            edge_attr: (num_edges, edge_feature_dim)
        """

        # Calculate correlation matrix
        returns = asset_data.pct_change().dropna()
        correlation_matrix = returns.corr()

        # Convert to adjacency matrix with threshold
        adjacency_matrix = correlation_matrix.abs()
        adjacency_matrix[adjacency_matrix < self.config.edge_threshold] = 0

        # Limit edges per node
        if self.config.max_edges_per_node > 0:
            for i in range(len(adjacency_matrix)):
                row = adjacency_matrix.iloc[i].copy()
                top_indices = row.nlargest(self.config.max_edges_per_node).index
                adjacency_matrix.iloc[i] = 0
                adjacency_matrix.loc[i, top_indices] = correlation_matrix.loc[i, top_indices]

        # Create node features
        node_features = []
        asset_order = list(asset_metadata.keys())

        for asset_id in asset_order:
            node = asset_metadata[asset_id]
            node_features.append(node.features)

        node_features = np.array(node_features)

        # Create edge information
        edge_indices = []
        edge_attributes = []

        for i, source_asset in enumerate(asset_order):
            for j, target_asset in enumerate(asset_order):
                if adjacency_matrix.loc[source_asset, target_asset] > 0:
                    edge_indices.append([i, j])

                    # Create edge features
                    correlation = correlation_matrix.loc[source_asset, target_asset]
                    edge_attr = np.array([
                        correlation,  # strength
                        1 if correlation > 0 else -1,  # direction
                        0.0,  # distance (placeholder)
                        1.0,  # beta (placeholder)
                        returns[source_asset].std() * returns[target_asset].std()  # volatility
                    ])
                    edge_attributes.append(edge_attr)

        if not edge_indices:
            # Create self-loops if no edges
            for i in range(len(asset_order)):
                edge_indices.append([i, i])
                edge_attributes.append(np.zeros(self.config.edge_feature_dim))

        edge_index = torch.LongTensor(edge_indices).t().contiguous()
        edge_attr = torch.FloatTensor(edge_attributes)

        return torch.FloatTensor(node_features), edge_index, edge_attr

    def construct_sector_graph(self, asset_metadata: Dict[str, AssetNode]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Construct graph based on sector relationships"""

        asset_order = list(asset_metadata.keys())
        n_assets = len(asset_order)

        # Create sector adjacency matrix
        sector_matrix = np.zeros((n_assets, n_assets))

        for i, asset_i in enumerate(asset_order):
            sector_i = asset_metadata[asset_i].sector
            for j, asset_j in enumerate(asset_order):
                sector_j = asset_metadata[asset_j].sector
                if sector_i == sector_j and i != j:
                    sector_matrix[i, j] = 1.0  # Same sector connection
                elif sector_i != sector_j:
                    sector_matrix[i, j] = 0.5  # Different sector connection

        # Create node features (same as correlation graph)
        node_features = []
        for asset_id in asset_order:
            node = asset_metadata[asset_id]
            node_features.append(node.features)
        node_features = np.array(node_features)

        # Create edges
        edge_indices = []
        edge_attributes = []

        for i in range(n_assets):
            for j in range(n_assets):
                if sector_matrix[i, j] > 0:
                    edge_indices.append([i, j])
                    edge_attr = np.array([
                        sector_matrix[i, j],  # strength
                        1,  # direction (neutral)
                        0.0,  # distance
                        1.0,  # beta
                        0.0   # volatility
                    ])
                    edge_attributes.append(edge_attr)

        edge_index = torch.LongTensor(edge_indices).t().contiguous()
        edge_attr = torch.FloatTensor(edge_attributes)

        return torch.FloatTensor(node_features), edge_index, edge_attr

    def construct_dynamic_graph(self, historical_data: List[pd.DataFrame],
                               asset_metadata: Dict[str, AssetNode]) -> List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Construct time-varying graphs"""

        graphs = []
        for data in historical_data:
            node_features, edge_index, edge_attr = self.construct_correlation_graph(data, asset_metadata)
            graphs.append((node_features, edge_index, edge_attr))

        return graphs


class GCNLayer(nn.Module if TORCH_AVAILABLE else object):
    """Graph Convolutional Network Layer"""

    def __init__(self, in_channels: int, out_channels: int, dropout: float = 0.1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for GCNLayer")

        super().__init__()
        self.conv = GCNConv(in_channels, out_channels)
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(out_channels)

    def forward(self, x, edge_index):
        x = self.conv(x, edge_index)
        x = self.norm(x)
        x = F.relu(x)
        x = self.dropout(x)
        return x


class GATLayer(nn.Module if TORCH_AVAILABLE else object):
    """Graph Attention Network Layer"""

    def __init__(self, in_channels: int, out_channels: int, num_heads: int = 8,
                 dropout: float = 0.1, concat: bool = True):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for GATLayer")

        super().__init__()
        self.conv = GATConv(in_channels, out_channels, heads=num_heads,
                           dropout=dropout, concat=concat)
        self.norm = nn.LayerNorm(out_channels * num_heads if concat else out_channels)

    def forward(self, x, edge_index):
        x = self.conv(x, edge_index)
        x = self.norm(x)
        x = F.relu(x)
        return x


class GraphSAGELayer(nn.Module if TORCH_AVAILABLE else object):
    """GraphSAGE Layer"""

    def __init__(self, in_channels: int, out_channels: int, dropout: float = 0.1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for GraphSAGELayer")

        super().__init__()
        self.conv = SAGEConv(in_channels, out_channels)
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(out_channels)

    def forward(self, x, edge_index):
        x = self.conv(x, edge_index)
        x = self.norm(x)
        x = F.relu(x)
        x = self.dropout(x)
        return x


class FinancialGCN(nn.Module if TORCH_AVAILABLE else object):
    """Graph Convolutional Network for Financial Assets"""

    def __init__(self, config: GraphConfig, output_dim: int = 1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for FinancialGCN")

        super().__init__()
        self.config = config

        # Input projection
        self.input_proj = nn.Linear(config.node_feature_dim, config.hidden_channels[0])

        # GCN layers
        self.gcn_layers = nn.ModuleList()
        for i in range(len(config.hidden_channels) - 1):
            self.gcn_layers.append(GCNLayer(config.hidden_channels[i], config.hidden_channels[i+1]))

        # Output layers
        self.output_layer = nn.Sequential(
            nn.Linear(config.hidden_channels[-1], config.hidden_channels[-1] // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_channels[-1] // 2, output_dim)
        )

    def forward(self, x, edge_index, batch=None):
        # Input projection
        x = self.input_proj(x)

        # GCN layers
        for layer in self.gcn_layers:
            x = layer(x, edge_index)

        # Global pooling (if batched)
        if batch is not None:
            x = torch_geometric.nn.global_mean_pool(x, batch)

        # Output prediction
        output = self.output_layer(x)
        return output


class FinancialGAT(nn.Module if TORCH_AVAILABLE else object):
    """Graph Attention Network for Financial Assets"""

    def __init__(self, config: GraphConfig, output_dim: int = 1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for FinancialGAT")

        super().__init__()
        self.config = config

        # Input projection
        self.input_proj = nn.Linear(config.node_feature_dim, config.hidden_channels[0])

        # GAT layers
        self.gat_layers = nn.ModuleList()
        for i in range(len(config.hidden_channels) - 1):
            concat = i < len(config.hidden_channels) - 2  # Don't concat on last layer
            out_channels = config.hidden_channels[i+1] // config.num_heads if concat else config.hidden_channels[i+1]
            self.gat_layers.append(GATLayer(config.hidden_channels[i], out_channels,
                                          config.num_heads, config.dropout, concat))

        # Output layers
        self.output_layer = nn.Sequential(
            nn.Linear(config.hidden_channels[-1], config.hidden_channels[-1] // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_channels[-1] // 2, output_dim)
        )

    def forward(self, x, edge_index, batch=None):
        # Input projection
        x = self.input_proj(x)

        # GAT layers
        for layer in self.gat_layers:
            x = layer(x, edge_index)

        # Global pooling (if batched)
        if batch is not None:
            x = torch_geometric.nn.global_mean_pool(x, batch)

        # Output prediction
        output = self.output_layer(x)
        return output


class TemporalGNN(nn.Module if TORCH_AVAILABLE else object):
    """Temporal Graph Neural Network for dynamic financial relationships"""

    def __init__(self, config: GraphConfig, output_dim: int = 1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for TemporalGNN")

        super().__init__()
        self.config = config

        # Spatial GNN (GCN, GAT, etc.)
        self.spatial_gnn = FinancialGAT(config, config.hidden_channels[-1])

        # Temporal modeling
        self.temporal_encoder = nn.GRU(
            config.hidden_channels[-1],
            config.temporal_hidden,
            num_layers=2,
            batch_first=True,
            dropout=config.dropout
        )

        # Output layers
        self.output_layer = nn.Sequential(
            nn.Linear(config.temporal_hidden, config.temporal_hidden // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.temporal_hidden // 2, output_dim)
        )

    def forward(self, temporal_graphs: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]):
        """
        Args:
            temporal_graphs: List of (node_features, edge_index, edge_attr) for each time step

        Returns:
            predictions: (batch_size, output_dim)
        """

        temporal_embeddings = []

        for node_features, edge_index, edge_attr in temporal_graphs:
            # Spatial aggregation
            spatial_emb = self.spatial_gnn(node_features, edge_index)
            temporal_embeddings.append(spatial_emb.unsqueeze(0))

        # Stack temporal embeddings
        temporal_input = torch.cat(temporal_embeddings, dim=0)  # (time_steps, batch_size, hidden_dim)

        # Temporal modeling
        temporal_output, _ = self.temporal_encoder(temporal_input)

        # Use last time step
        final_embedding = temporal_output[-1]

        # Output prediction
        output = self.output_layer(final_embedding)
        return output


class GraphBasedPortfolioOptimizer:
    """Portfolio optimization using graph-based risk assessment"""

    def __init__(self, config: GraphConfig):
        self.config = config
        self.risk_model = None

    def estimate_graph_risk(self, node_features: torch.Tensor, edge_index: torch.Tensor,
                           edge_attr: torch.Tensor) -> np.ndarray:
        """Estimate risk using graph structure"""

        if not TORCH_AVAILABLE:
            return np.ones(node_features.shape[0]) * 0.02  # Default volatility

        # Simple risk estimation based on connectivity
        n_assets = node_features.shape[0]

        # Calculate degree centrality (connectedness)
        degrees = torch.zeros(n_assets)
        for i in range(edge_index.shape[1]):
            degrees[edge_index[1, i]] += 1

        # Higher degree = higher systemic risk
        base_risk = 0.01  # Base volatility
        risk_premium = degrees.float() / degrees.max() * 0.02  # Additional risk based on connectivity

        return (base_risk + risk_premium.numpy()).astype(np.float32)

    def optimize_portfolio(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray,
                          risk_free_rate: float = 0.02, target_return: Optional[float] = None) -> np.ndarray:
        """Optimize portfolio using Markowitz framework with graph-based constraints"""

        n_assets = len(expected_returns)

        # Objective: maximize Sharpe ratio
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
            return -sharpe_ratio  # Minimize negative Sharpe

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
        ]

        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.dot(w, expected_returns) - target_return
            })

        # Bounds: no short selling, max 20% per asset
        bounds = [(0, 0.2) for _ in range(n_assets)]

        # Initial guess
        x0 = np.ones(n_assets) / n_assets

        # Optimize
        result = optimize.minimize(objective, x0, method='SLSQP',
                                 bounds=bounds, constraints=constraints)

        return result.x if result.success else x0

    def graph_constrained_optimization(self, expected_returns: np.ndarray,
                                     covariance_matrix: np.ndarray,
                                     edge_index: torch.Tensor,
                                     max_cluster_weight: float = 0.3) -> np.ndarray:
        """Portfolio optimization with graph-based constraints"""

        n_assets = len(expected_returns)

        # Identify asset clusters using graph structure
        clusters = self._identify_clusters(edge_index, n_assets)

        # Objective: maximize Sharpe ratio with cluster constraints
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            sharpe_ratio = (portfolio_return - 0.02) / portfolio_volatility

            # Cluster concentration penalty
            cluster_penalty = 0
            for cluster in clusters.values():
                cluster_weight = sum(weights[i] for i in cluster)
                if cluster_weight > max_cluster_weight:
                    cluster_penalty += (cluster_weight - max_cluster_weight) ** 2

            return -sharpe_ratio + cluster_penalty

        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 0.15) for _ in range(n_assets)]  # Stricter bounds

        x0 = np.ones(n_assets) / n_assets
        result = optimize.minimize(objective, x0, method='SLSQP',
                                 bounds=bounds, constraints=constraints)

        return result.x if result.success else x0

    def _identify_clusters(self, edge_index: torch.Tensor, n_assets: int) -> Dict[int, List[int]]:
        """Identify asset clusters using graph structure"""

        # Simple clustering based on connectivity
        clusters = defaultdict(list)

        # Use connected components or simple degree-based clustering
        degrees = torch.zeros(n_assets)
        for i in range(edge_index.shape[1]):
            degrees[edge_index[1, i]] += 1

        # Cluster based on degree quantiles
        degree_percentiles = torch.quantile(degrees, torch.tensor([0.33, 0.67]))

        for i in range(n_assets):
            if degrees[i] <= degree_percentiles[0]:
                clusters[0].append(i)  # Low connectivity
            elif degrees[i] <= degree_percentiles[1]:
                clusters[1].append(i)  # Medium connectivity
            else:
                clusters[2].append(i)  # High connectivity

        return dict(clusters)


class FinancialGNNTrainer:
    """Trainer for Financial Graph Neural Networks"""

    def __init__(self, config: GraphConfig, model: nn.Module):
        self.config = config
        self.model = model

        # Initialize device
        if TORCH_AVAILABLE and config.use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif TORCH_AVAILABLE:
            self.device = torch.device("cpu")
        else:
            self.device = None

        if TORCH_AVAILABLE:
            self.model.to(self.device)
            self.optimizer = optim.Adam(self.model.parameters(),
                                      lr=config.learning_rate,
                                      weight_decay=config.weight_decay)

        self.training_history = []

    def train_epoch(self, data_loader):
        """Train for one epoch"""

        if not TORCH_AVAILABLE:
            return 0.0

        self.model.train()
        total_loss = 0.0

        for batch in data_loader:
            batch = batch.to(self.device)

            self.optimizer.zero_grad()

            # Forward pass
            output = self.model(batch.x, batch.edge_index, batch.batch)

            # Loss calculation (assuming regression task)
            loss = F.mse_loss(output.squeeze(), batch.y)

            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(data_loader)

    def validate(self, data_loader):
        """Validate model"""

        if not TORCH_AVAILABLE:
            return 0.0

        self.model.eval()
        total_loss = 0.0

        with torch.no_grad():
            for batch in data_loader:
                batch = batch.to(self.device)
                output = self.model(batch.x, batch.edge_index, batch.batch)
                loss = F.mse_loss(output.squeeze(), batch.y)
                total_loss += loss.item()

        return total_loss / len(data_loader)

    def train(self, train_loader, val_loader, num_epochs: Optional[int] = None) -> Dict[str, List]:
        """Train the model"""

        num_epochs = num_epochs or self.config.num_epochs

        print(f"Starting GNN training for {num_epochs} epochs...")

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(num_epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)

            self.training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss
            })

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{num_epochs}: "
                      f"Train Loss = {train_loss:.6f}, Val Loss = {val_loss:.6f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= 20:
                print(f"Early stopping at epoch {epoch + 1}")
                break

        return self.training_history


# Factory functions
def create_financial_gcn(config: Optional[GraphConfig] = None, output_dim: int = 1):
    """Factory function for Financial GCN"""
    if config is None:
        config = GraphConfig(gnn_type="gcn")
    return FinancialGCN(config, output_dim)


def create_financial_gat(config: Optional[GraphConfig] = None, output_dim: int = 1):
    """Factory function for Financial GAT"""
    if config is None:
        config = GraphConfig(gnn_type="gat")
    return FinancialGAT(config, output_dim)


def create_temporal_gnn(config: Optional[GraphConfig] = None, output_dim: int = 1):
    """Factory function for Temporal GNN"""
    if config is None:
        config = GraphConfig(gnn_type="temporal_gnn")
    return TemporalGNN(config, output_dim)


def create_graph_constructor(config: Optional[GraphConfig] = None):
    """Factory function for graph constructor"""
    if config is None:
        config = GraphConfig()
    return FinancialGraphConstructor(config)


def create_portfolio_optimizer(config: Optional[GraphConfig] = None):
    """Factory function for portfolio optimizer"""
    if config is None:
        config = GraphConfig()
    return GraphBasedPortfolioOptimizer(config)


# Example usage and testing
if __name__ == "__main__":
    # Test Graph Neural Networks
    print("Testing Graph Neural Networks...")

    if TORCH_AVAILABLE and TORCH_GEOMETRIC_AVAILABLE:
        config = GraphConfig()

        # Test graph constructor
        print("\n1. Testing Graph Constructor...")
        constructor = create_graph_constructor(config)

        # Create dummy asset data
        np.random.seed(42)
        assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        dates = pd.date_range("2023-01-01", periods=100, freq="D")

        # Generate synthetic price data
        asset_data = pd.DataFrame({
            asset: 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 100)))
            for asset in assets
        }, index=dates)

        # Create asset metadata
        asset_metadata = {}
        for asset in assets:
            features = np.random.normal(0, 1, 20)  # 20 features
            asset_metadata[asset] = AssetNode(
                asset_id=asset,
                asset_type="stock",
                sector="Technology",
                industry="Software",
                market_cap=1000000000,
                features=features
            )

        # Construct correlation graph
        node_features, edge_index, edge_attr = constructor.construct_correlation_graph(
            asset_data, asset_metadata
        )

        print(f"Constructed graph with {node_features.shape[0]} nodes and {edge_index.shape[1]} edges")
        print(f"Node features shape: {node_features.shape}")
        print(f"Edge attributes shape: {edge_attr.shape}")

        # Test GCN
        print("\n2. Testing GCN...")
        gcn = create_financial_gcn(config)
        gcn.to(torch.device("cpu"))

        # Forward pass
        output = gcn(node_features, edge_index)
        print(f"GCN output shape: {output.shape}")

    else:
        print("PyTorch and/or PyTorch Geometric not available - GNN functionality disabled")
        print("Install PyTorch: pip install torch")
        print("Install PyTorch Geometric: pip install torch-geometric")
