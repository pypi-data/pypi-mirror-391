"""Advanced Feature Engineering Pipeline for Quantitative Modeling.

This module provides comprehensive feature engineering capabilities including:
- Technical indicators and statistical features
- Time-series transformations and decompositions
- Natural language processing features
- Image and signal processing features
- Automated feature selection and generation
- Cross-sectional and temporal feature engineering
- Feature scaling and normalization
- Outlier detection and robust statistics
- Dimensionality reduction techniques
- Feature interaction and polynomial features
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union, Any, Tuple
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
import warnings
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats, signal
from scipy.stats import entropy, kurtosis, skew
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, PolynomialFeatures
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.manifold import TSNE, Isomap
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# Optional imports
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    talib = None

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    nltk = None
    SentimentIntensityAnalyzer = None

try:
    import spacy
    HAS_SPACY = False  # Will be set to True if model is available
except ImportError:
    HAS_SPACY = False
    spacy = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    pipeline = None
    AutoTokenizer = None
    AutoModel = None

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller, kpss
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    seasonal_decompose = None
    adfuller = None
    kpss = None

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    librosa = None

from qantify.signals import (
    atr,
    bollinger_bands,
    cumulative_return,
    difference,
    donchian_channels,
    ema,
    hma,
    ichimoku,
    keltner_channels,
    lag,
    macd,
    obv,
    percent_rank,
    pvo,
    rolling_beta,
    rolling_correlation,
    rolling_volatility,
    rsi,
    sma,
    stochastic,
    true_range,
    vwma,
    wma,
    zscore,
)


DEFAULT_PRICE_COLUMNS = ["open", "high", "low", "close"]


# =============================================================================
# ADVANCED FEATURE ENGINEERING CLASSES
# =============================================================================

class FeatureEngineer(ABC):
    """Abstract base class for feature engineering."""

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'FeatureEngineer':
        """Fit the feature engineer."""
        pass

    @abstractmethod
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform input data."""
        pass

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """Fit and transform."""
        return self.fit(X, y).transform(X)


class StatisticalFeatureEngineer(FeatureEngineer):
    """Advanced statistical feature engineering."""

    def __init__(self, windows: Sequence[int] = None, include_moments: bool = True,
                 include_entropy: bool = True, include_distribution: bool = True):
        self.windows = windows or [5, 10, 20, 50]
        self.include_moments = include_moments
        self.include_entropy = include_entropy
        self.include_distribution = include_distribution
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'StatisticalFeatureEngineer':
        """Fit the statistical feature engineer."""
        self.feature_names = []
        for col in X.columns:
            for window in self.windows:
                if self.include_moments:
                    self.feature_names.extend([
                        f"{col}_mean_{window}",
                        f"{col}_std_{window}",
                        f"{col}_skew_{window}",
                        f"{col}_kurt_{window}",
                        f"{col}_min_{window}",
                        f"{col}_max_{window}",
                        f"{col}_median_{window}",
                        f"{col}_q25_{window}",
                        f"{col}_q75_{window}",
                        f"{col}_iqr_{window}"
                    ])
                if self.include_entropy:
                    self.feature_names.append(f"{col}_entropy_{window}")
                if self.include_distribution:
                    self.feature_names.extend([
                        f"{col}_cv_{window}",  # coefficient of variation
                        f"{col}_range_{window}",
                        f"{col}_mad_{window}",  # mean absolute deviation
                        f"{col}_variation_{window}"
                    ])
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with statistical features."""
        features = pd.DataFrame(index=X.index)

        for col in X.columns:
            series = X[col]
            for window in self.windows:
                rolled = series.rolling(window=window, min_periods=1)

                if self.include_moments:
                    features[f"{col}_mean_{window}"] = rolled.mean()
                    features[f"{col}_std_{window}"] = rolled.std()
                    features[f"{col}_skew_{window}"] = rolled.apply(lambda x: skew(x.dropna()) if len(x.dropna()) > 2 else 0)
                    features[f"{col}_kurt_{window}"] = rolled.apply(lambda x: kurtosis(x.dropna()) if len(x.dropna()) > 3 else 0)
                    features[f"{col}_min_{window}"] = rolled.min()
                    features[f"{col}_max_{window}"] = rolled.max()
                    features[f"{col}_median_{window}"] = rolled.median()
                    features[f"{col}_q25_{window}"] = rolled.quantile(0.25)
                    features[f"{col}_q75_{window}"] = rolled.quantile(0.75)
                    features[f"{col}_iqr_{window}"] = features[f"{col}_q75_{window}"] - features[f"{col}_q25_{window}"]

                if self.include_entropy:
                    features[f"{col}_entropy_{window}"] = rolled.apply(
                        lambda x: entropy(np.histogram(x.dropna(), bins=10, density=True)[0] + 1e-10)
                        if len(x.dropna()) > 1 else 0
                    )

                if self.include_distribution:
                    mean = rolled.mean()
                    std = rolled.std()
                    features[f"{col}_cv_{window}"] = std / mean.replace(0, 1e-10)
                    features[f"{col}_range_{window}"] = rolled.max() - rolled.min()
                    features[f"{col}_mad_{window}"] = rolled.apply(lambda x: np.mean(np.abs(x - np.mean(x))))
                    features[f"{col}_variation_{window}"] = rolled.var()

        return features.fillna(0)


class TimeSeriesFeatureEngineer(FeatureEngineer):
    """Advanced time-series feature engineering."""

    def __init__(self, include_seasonal: bool = True, include_trend: bool = True,
                 include_cycles: bool = True, include_autocorr: bool = True,
                 freq: str = None):
        self.include_seasonal = include_seasonal
        self.include_trend = include_trend
        self.include_cycles = include_cycles
        self.include_autocorr = include_autocorr
        self.freq = freq
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'TimeSeriesFeatureEngineer':
        """Fit the time-series feature engineer."""
        self.feature_names = []
        for col in X.columns:
            if self.include_seasonal and HAS_STATSMODELS:
                self.feature_names.extend([
                    f"{col}_seasonal_strength",
                    f"{col}_trend_strength",
                    f"{col}_residual_strength"
                ])
            if self.include_trend:
                self.feature_names.extend([
                    f"{col}_linear_trend",
                    f"{col}_trend_slope",
                    f"{col}_trend_acceleration"
                ])
            if self.include_cycles:
                self.feature_names.extend([
                    f"{col}_fft_peak_freq",
                    f"{col}_fft_peak_power",
                    f"{col}_dominant_cycle"
                ])
            if self.include_autocorr:
                self.feature_names.extend([
                    f"{col}_autocorr_1",
                    f"{col}_autocorr_5",
                    f"{col}_autocorr_10",
                    f"{col}_autocorr_lag_max"
                ])
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with time-series features."""
        features = pd.DataFrame(index=X.index)

        for col in X.columns:
            series = X[col].dropna()

            if len(series) < 10:  # Need minimum data for decomposition
                continue

            if self.include_seasonal and HAS_STATSMODELS and self.freq:
                try:
                    decomposition = seasonal_decompose(series, model='additive', period=self.freq)
                    seasonal_std = decomposition.seasonal.std()
                    trend_std = decomposition.trend.std()
                    residual_std = decomposition.resid.std()
                    total_std = series.std()

                    features[f"{col}_seasonal_strength"] = seasonal_std / total_std if total_std > 0 else 0
                    features[f"{col}_trend_strength"] = trend_std / total_std if total_std > 0 else 0
                    features[f"{col}_residual_strength"] = residual_std / total_std if total_std > 0 else 0
                except:
                    features[f"{col}_seasonal_strength"] = 0
                    features[f"{col}_trend_strength"] = 0
                    features[f"{col}_residual_strength"] = 0

            if self.include_trend:
                # Linear trend
                x = np.arange(len(series))
                slope, intercept = np.polyfit(x, series.values, 1)
                features[f"{col}_linear_trend"] = slope * x + intercept
                features[f"{col}_trend_slope"] = slope

                # Trend acceleration (second derivative approximation)
                if len(series) > 2:
                    accel = np.gradient(np.gradient(series.values))
                    features[f"{col}_trend_acceleration"] = pd.Series(accel, index=series.index)

            if self.include_cycles and len(series) > 20:
                try:
                    # FFT analysis
                    fft = np.fft.fft(series.values)
                    freqs = np.fft.fftfreq(len(series))
                    power = np.abs(fft) ** 2

                    # Find dominant frequency
                    positive_freq_mask = freqs > 0
                    positive_freqs = freqs[positive_freq_mask]
                    positive_power = power[positive_freq_mask]

                    if len(positive_freqs) > 0:
                        peak_idx = np.argmax(positive_power)
                        features[f"{col}_fft_peak_freq"] = positive_freqs[peak_idx]
                        features[f"{col}_fft_peak_power"] = positive_power[peak_idx]
                        features[f"{col}_dominant_cycle"] = 1 / positive_freqs[peak_idx] if positive_freqs[peak_idx] > 0 else 0
                except:
                    features[f"{col}_fft_peak_freq"] = 0
                    features[f"{col}_fft_peak_power"] = 0
                    features[f"{col}_dominant_cycle"] = 0

            if self.include_autocorr and len(series) > 15:
                try:
                    autocorr = [series.autocorr(lag=i) for i in range(1, min(11, len(series)//2))]
                    features[f"{col}_autocorr_1"] = autocorr[0] if len(autocorr) > 0 else 0
                    features[f"{col}_autocorr_5"] = autocorr[4] if len(autocorr) > 4 else 0
                    features[f"{col}_autocorr_10"] = autocorr[9] if len(autocorr) > 9 else 0
                    features[f"{col}_autocorr_lag_max"] = np.argmax(np.abs(autocorr)) + 1 if autocorr else 0
                except:
                    features[f"{col}_autocorr_1"] = 0
                    features[f"{col}_autocorr_5"] = 0
                    features[f"{col}_autocorr_10"] = 0
                    features[f"{col}_autocorr_lag_max"] = 0

        return features.fillna(0)


class NLPFeatureEngineer(FeatureEngineer):
    """Natural Language Processing feature engineering."""

    def __init__(self, model_name: str = "en_core_web_sm", use_transformers: bool = False,
                 sentiment_analysis: bool = True, text_complexity: bool = True,
                 readability_metrics: bool = True):
        self.model_name = model_name
        self.use_transformers = use_transformers
        self.sentiment_analysis = sentiment_analysis
        self.text_complexity = text_complexity
        self.readability_metrics = readability_metrics

        # Initialize models
        self.nlp = None
        self.sentiment_analyzer = None
        self.tokenizer = None
        self.model = None

        if HAS_SPACY and not use_transformers:
            try:
                self.nlp = spacy.load(model_name)
                HAS_SPACY = True
            except:
                warnings.warn(f"Could not load spaCy model {model_name}")

        if HAS_TRANSFORMERS and use_transformers:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
                self.model = AutoModel.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
            except:
                warnings.warn("Could not load transformer models")

        if HAS_NLTK and sentiment_analysis:
            try:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except:
                warnings.warn("Could not initialize NLTK sentiment analyzer")

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'NLPFeatureEngineer':
        """Fit the NLP feature engineer."""
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform text data into NLP features."""
        features = pd.DataFrame(index=X.index)

        # Find text columns
        text_columns = X.select_dtypes(include=['object', 'string']).columns

        for col in text_columns:
            text_series = X[col].fillna('')

            if self.sentiment_analysis and self.sentiment_analyzer:
                sentiments = text_series.apply(self._extract_sentiment)
                features[f"{col}_sentiment_compound"] = sentiments.apply(lambda x: x['compound'])
                features[f"{col}_sentiment_pos"] = sentiments.apply(lambda x: x['pos'])
                features[f"{col}_sentiment_neg"] = sentiments.apply(lambda x: x['neg'])
                features[f"{col}_sentiment_neu"] = sentiments.apply(lambda x: x['neu'])

            if self.text_complexity:
                complexity_features = text_series.apply(self._extract_text_complexity)
                features[f"{col}_word_count"] = complexity_features.apply(lambda x: x['word_count'])
                features[f"{col}_sentence_count"] = complexity_features.apply(lambda x: x['sentence_count'])
                features[f"{col}_avg_word_length"] = complexity_features.apply(lambda x: x['avg_word_length'])
                features[f"{col}_unique_words_ratio"] = complexity_features.apply(lambda x: x['unique_words_ratio'])
                features[f"{col}_lexical_diversity"] = complexity_features.apply(lambda x: x['lexical_diversity'])

            if self.readability_metrics:
                readability_features = text_series.apply(self._extract_readability)
                features[f"{col}_flesch_reading_ease"] = readability_features.apply(lambda x: x['flesch_reading_ease'])
                features[f"{col}_flesch_kincaid_grade"] = readability_features.apply(lambda x: x['flesch_kincaid_grade'])
                features[f"{col}_dale_chall_score"] = readability_features.apply(lambda x: x['dale_chall_score'])

        return features.fillna(0)

    def _extract_sentiment(self, text: str) -> Dict[str, float]:
        """Extract sentiment scores."""
        if not self.sentiment_analyzer or not text.strip():
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 0}

        try:
            return self.sentiment_analyzer.polarity_scores(text)
        except:
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 0}

    def _extract_text_complexity(self, text: str) -> Dict[str, float]:
        """Extract text complexity metrics."""
        if not text.strip():
            return {'word_count': 0, 'sentence_count': 0, 'avg_word_length': 0,
                   'unique_words_ratio': 0, 'lexical_diversity': 0}

        words = text.split()
        sentences = text.split('.')

        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = np.mean([len(word) for word in words]) if words else 0
        unique_words = len(set(words.lower() for word in words))
        unique_words_ratio = unique_words / word_count if word_count > 0 else 0
        lexical_diversity = unique_words / len(words) if words else 0

        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'unique_words_ratio': unique_words_ratio,
            'lexical_diversity': lexical_diversity
        }

    def _extract_readability(self, text: str) -> Dict[str, float]:
        """Extract readability metrics."""
        if not text.strip():
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0, 'dale_chall_score': 0}

        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        if not words or not sentences:
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0, 'dale_chall_score': 0}

        # Simplified Flesch Reading Ease
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(self._count_syllables(word) for word in words)

        if total_sentences == 0 or total_words == 0:
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0, 'dale_chall_score': 0}

        # Flesch Reading Ease = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        words_per_sentence = total_words / total_sentences
        syllables_per_word = total_syllables / total_words
        flesch_reading_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word

        # Flesch-Kincaid Grade Level = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        flesch_kincaid_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59

        # Simplified Dale-Chall Score
        dale_chall_score = 0.1579 * (100 * self._difficult_words_ratio(text)) + 0.0496 * words_per_sentence

        return {
            'flesch_reading_ease': flesch_reading_ease,
            'flesch_kincaid_grade': flesch_kincaid_grade,
            'dale_chall_score': dale_chall_score
        }

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def _difficult_words_ratio(self, text: str) -> float:
        """Calculate ratio of difficult words (simplified)."""
        words = text.split()
        if not words:
            return 0

        # Simple heuristic: words longer than 6 characters are considered difficult
        difficult_words = [word for word in words if len(word) > 6]
        return len(difficult_words) / len(words)


class ImageFeatureEngineer(FeatureEngineer):
    """Image feature engineering using computer vision."""

    def __init__(self, include_color: bool = True, include_texture: bool = True,
                 include_shape: bool = True, include_edges: bool = True,
                 resize_dim: Tuple[int, int] = (64, 64)):
        if not HAS_CV2:
            raise ImportError("OpenCV is required for image feature engineering")

        self.include_color = include_color
        self.include_texture = include_texture
        self.include_shape = include_shape
        self.include_edges = include_edges
        self.resize_dim = resize_dim
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'ImageFeatureEngineer':
        """Fit the image feature engineer."""
        self.feature_names = []

        # Assume image columns contain paths or base64 encoded images
        image_columns = [col for col in X.columns if 'image' in col.lower() or 'img' in col.lower()]

        for col in image_columns:
            if self.include_color:
                self.feature_names.extend([
                    f"{col}_color_mean_r", f"{col}_color_mean_g", f"{col}_color_mean_b",
                    f"{col}_color_std_r", f"{col}_color_std_g", f"{col}_color_std_b",
                    f"{col}_color_skew_r", f"{col}_color_skew_g", f"{col}_color_skew_b"
                ])
            if self.include_texture:
                self.feature_names.extend([
                    f"{col}_texture_contrast", f"{col}_texture_energy",
                    f"{col}_texture_homogeneity", f"{col}_texture_correlation"
                ])
            if self.include_shape:
                self.feature_names.extend([
                    f"{col}_shape_area", f"{col}_shape_perimeter",
                    f"{col}_shape_circularity", f"{col}_shape_compactness"
                ])
            if self.include_edges:
                self.feature_names.extend([
                    f"{col}_edges_canny_count", f"{col}_edges_sobel_mean",
                    f"{col}_edges_laplacian_var", f"{col}_edges_hough_lines"
                ])

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform image data into features."""
        features = pd.DataFrame(index=X.index)

        image_columns = [col for col in X.columns if 'image' in col.lower() or 'img' in col.lower()]

        for col in image_columns:
            image_features = X[col].apply(self._extract_image_features)
            image_df = pd.DataFrame(list(image_features), index=X.index)

            # Rename columns with prefix
            rename_dict = {old: f"{col}_{old}" for old in image_df.columns}
            image_df = image_df.rename(columns=rename_dict)

            features = pd.concat([features, image_df], axis=1)

        return features.fillna(0)

    def _extract_image_features(self, image_data) -> Dict[str, float]:
        """Extract features from a single image."""
        features = {}

        try:
            # Handle different image input formats
            if isinstance(image_data, str):
                # Assume it's a file path
                img = cv2.imread(image_data)
                if img is None:
                    return self._empty_features()
            elif isinstance(image_data, np.ndarray):
                img = image_data.copy()
            else:
                return self._empty_features()

            # Resize image
            img = cv2.resize(img, self.resize_dim)

            if self.include_color:
                color_features = self._extract_color_features(img)
                features.update(color_features)

            if self.include_texture:
                texture_features = self._extract_texture_features(img)
                features.update(texture_features)

            if self.include_shape:
                shape_features = self._extract_shape_features(img)
                features.update(shape_features)

            if self.include_edges:
                edge_features = self._extract_edge_features(img)
                features.update(edge_features)

        except Exception as e:
            warnings.warn(f"Error extracting image features: {e}")
            return self._empty_features()

        return features

    def _extract_color_features(self, img: np.ndarray) -> Dict[str, float]:
        """Extract color-based features."""
        features = {}

        # Convert to different color spaces
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        for i, channel in enumerate(['r', 'g', 'b']):
            channel_data = img[:, :, i].flatten()
            features[f"color_mean_{channel}"] = np.mean(channel_data)
            features[f"color_std_{channel}"] = np.std(channel_data)
            features[f"color_skew_{channel}"] = stats.skew(channel_data)

        # HSV features
        h_channel = hsv[:, :, 0].flatten()
        s_channel = hsv[:, :, 1].flatten()
        v_channel = hsv[:, :, 2].flatten()

        features['color_hue_mean'] = np.mean(h_channel)
        features['color_saturation_mean'] = np.mean(s_channel)
        features['color_value_mean'] = np.mean(v_channel)

        return features

    def _extract_texture_features(self, img: np.ndarray) -> Dict[str, float]:
        """Extract texture-based features using GLCM."""
        features = {}

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Calculate GLCM features (simplified)
            # In practice, you'd use skimage.feature.graycomatrix and graycoprops
            features['texture_contrast'] = np.std(gray)  # Simplified
            features['texture_energy'] = np.mean(gray ** 2) / (np.mean(gray) ** 2) if np.mean(gray) != 0 else 0
            features['texture_homogeneity'] = 1 / (1 + np.var(gray))  # Simplified
            features['texture_correlation'] = np.corrcoef(gray.flatten(), np.roll(gray.flatten(), 1))[0, 1]

        except:
            features['texture_contrast'] = 0
            features['texture_energy'] = 0
            features['texture_homogeneity'] = 0
            features['texture_correlation'] = 0

        return features

    def _extract_shape_features(self, img: np.ndarray) -> Dict[str, float]:
        """Extract shape-based features."""
        features = {}

        try:
            # Convert to grayscale and threshold
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Largest contour
                largest_contour = max(contours, key=cv2.contourArea)

                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)

                features['shape_area'] = area
                features['shape_perimeter'] = perimeter
                features['shape_circularity'] = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
                features['shape_compactness'] = area / (perimeter ** 2) if perimeter > 0 else 0
            else:
                features['shape_area'] = 0
                features['shape_perimeter'] = 0
                features['shape_circularity'] = 0
                features['shape_compactness'] = 0

        except:
            features['shape_area'] = 0
            features['shape_perimeter'] = 0
            features['shape_circularity'] = 0
            features['shape_compactness'] = 0

        return features

    def _extract_edge_features(self, img: np.ndarray) -> Dict[str, float]:
        """Extract edge-based features."""
        features = {}

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Canny edge detection
            canny = cv2.Canny(gray, 100, 200)
            features['edges_canny_count'] = np.sum(canny > 0)

            # Sobel edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            sobel = np.sqrt(sobelx**2 + sobely**2)
            features['edges_sobel_mean'] = np.mean(sobel)

            # Laplacian
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            features['edges_laplacian_var'] = np.var(laplacian)

            # Hough line detection
            lines = cv2.HoughLines(canny, 1, np.pi/180, 50)
            features['edges_hough_lines'] = len(lines) if lines is not None else 0

        except:
            features['edges_canny_count'] = 0
            features['edges_sobel_mean'] = 0
            features['edges_laplacian_var'] = 0
            features['edges_hough_lines'] = 0

        return features

    def _empty_features(self) -> Dict[str, float]:
        """Return empty features dictionary."""
        return {name: 0.0 for name in self.feature_names}


class AudioFeatureEngineer(FeatureEngineer):
    """Audio feature engineering using librosa."""

    def __init__(self, sample_rate: int = 22050, n_mfcc: int = 13,
                 include_spectral: bool = True, include_temporal: bool = True,
                 include_rhythm: bool = True):
        if not HAS_LIBROSA:
            raise ImportError("librosa is required for audio feature engineering")

        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.include_spectral = include_spectral
        self.include_temporal = include_temporal
        self.include_rhythm = include_rhythm
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'AudioFeatureEngineer':
        """Fit the audio feature engineer."""
        self.feature_names = []

        audio_columns = [col for col in X.columns if 'audio' in col.lower() or 'sound' in col.lower()]

        for col in audio_columns:
            if self.include_spectral:
                self.feature_names.extend([f"{col}_mfcc_{i}" for i in range(self.n_mfcc)])
                self.feature_names.extend([
                    f"{col}_spectral_centroid", f"{col}_spectral_bandwidth",
                    f"{col}_spectral_rolloff", f"{col}_spectral_flux"
                ])
            if self.include_temporal:
                self.feature_names.extend([
                    f"{col}_zero_crossing_rate", f"{col}_rms_energy",
                    f"{col}_tempo", f"{col}_beat_strength"
                ])
            if self.include_rhythm:
                self.feature_names.extend([
                    f"{col}_chroma_cqt_{i}" for i in range(12)
                ])

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform audio data into features."""
        features = pd.DataFrame(index=X.index)

        audio_columns = [col for col in X.columns if 'audio' in col.lower() or 'sound' in col.lower()]

        for col in audio_columns:
            audio_features = X[col].apply(self._extract_audio_features)
            audio_df = pd.DataFrame(list(audio_features), index=X.index)

            # Rename columns with prefix
            rename_dict = {old: f"{col}_{old}" for old in audio_df.columns}
            audio_df = audio_df.rename(columns=rename_dict)

            features = pd.concat([features, audio_df], axis=1)

        return features.fillna(0)

    def _extract_audio_features(self, audio_data) -> Dict[str, float]:
        """Extract features from audio data."""
        features = {}

        try:
            if isinstance(audio_data, str):
                # Assume it's a file path
                y, sr = librosa.load(audio_data, sr=self.sample_rate)
            elif isinstance(audio_data, np.ndarray):
                y = audio_data
                sr = self.sample_rate
            else:
                return self._empty_features()

            if len(y) == 0:
                return self._empty_features()

            if self.include_spectral:
                spectral_features = self._extract_spectral_features(y, sr)
                features.update(spectral_features)

            if self.include_temporal:
                temporal_features = self._extract_temporal_features(y, sr)
                features.update(temporal_features)

            if self.include_rhythm:
                rhythm_features = self._extract_rhythm_features(y, sr)
                features.update(rhythm_features)

        except Exception as e:
            warnings.warn(f"Error extracting audio features: {e}")
            return self._empty_features()

        return features

    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features."""
        features = {}

        try:
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            for i in range(self.n_mfcc):
                features[f"mfcc_{i}"] = np.mean(mfccs[i])

            # Spectral features
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            features['spectral_flux'] = np.mean(librosa.onset.onset_strength(y=y, sr=sr))

        except:
            for i in range(self.n_mfcc):
                features[f"mfcc_{i}"] = 0
            features['spectral_centroid'] = 0
            features['spectral_bandwidth'] = 0
            features['spectral_rolloff'] = 0
            features['spectral_flux'] = 0

        return features

    def _extract_temporal_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract temporal features."""
        features = {}

        try:
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
            features['rms_energy'] = np.mean(librosa.feature.rms(y=y))

            # Tempo and beat
            tempo, beat_strength = librosa.beat.tempo(y=y, sr=sr)
            features['tempo'] = tempo
            features['beat_strength'] = np.mean(beat_strength)

        except:
            features['zero_crossing_rate'] = 0
            features['rms_energy'] = 0
            features['tempo'] = 0
            features['beat_strength'] = 0

        return features

    def _extract_rhythm_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract rhythm features."""
        features = {}

        try:
            # Chroma features
            chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr)
            for i in range(12):  # 12 chroma bins
                features[f"chroma_cqt_{i}"] = np.mean(chroma_cqt[i])

        except:
            for i in range(12):
                features[f"chroma_cqt_{i}"] = 0

        return features

    def _empty_features(self) -> Dict[str, float]:
        """Return empty features dictionary."""
        return {name: 0.0 for name in self.feature_names}


class DimensionalityReductionEngineer(FeatureEngineer):
    """Dimensionality reduction and manifold learning feature engineering."""

    def __init__(self, method: str = "pca", n_components: Optional[int] = None,
                 explained_variance_ratio: float = 0.95, random_state: int = 42):
        self.method = method
        self.n_components = n_components
        self.explained_variance_ratio = explained_variance_ratio
        self.random_state = random_state
        self.reducer = None
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'DimensionalityReductionEngineer':
        """Fit the dimensionality reduction model."""
        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values

        if X_numeric.shape[1] == 0:
            self.reducer = None
            return self

        if self.method == "pca":
            if self.n_components is None:
                # Use explained variance ratio to determine components
                pca_temp = PCA(random_state=self.random_state)
                pca_temp.fit(X_numeric)
                explained_variance = np.cumsum(pca_temp.explained_variance_ratio_)
                self.n_components = np.argmax(explained_variance >= self.explained_variance_ratio) + 1
                if self.n_components < 2:
                    self.n_components = min(5, X_numeric.shape[1])

            self.reducer = PCA(n_components=self.n_components, random_state=self.random_state)

        elif self.method == "ica":
            self.n_components = self.n_components or min(10, X_numeric.shape[1])
            self.reducer = FastICA(n_components=self.n_components, random_state=self.random_state)

        elif self.method == "tsne":
            self.n_components = self.n_components or 2
            # t-SNE is typically used for visualization, but can be used for feature engineering
            self.reducer = TSNE(n_components=self.n_components, random_state=self.random_state)

        elif self.method == "isomap":
            self.n_components = self.n_components or 2
            self.reducer = Isomap(n_components=self.n_components)

        elif self.method == "svd":
            self.n_components = self.n_components or min(50, X_numeric.shape[1])
            self.reducer = TruncatedSVD(n_components=self.n_components, random_state=self.random_state)

        else:
            raise ValueError(f"Unknown dimensionality reduction method: {self.method}")

        if self.reducer:
            self.reducer.fit(X_numeric)

        # Generate feature names
        self.n_components = self.n_components or X_numeric.shape[1]
        self.feature_names = [f"{self.method.upper()}_{i}" for i in range(self.n_components)]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data using fitted dimensionality reduction."""
        if self.reducer is None:
            return pd.DataFrame(index=X.index)

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values
        X_reduced = self.reducer.transform(X_numeric)

        features = pd.DataFrame(
            X_reduced,
            index=X.index,
            columns=self.feature_names
        )

        return features


class FeatureInteractionEngineer(FeatureEngineer):
    """Feature interaction and polynomial feature engineering."""

    def __init__(self, degree: int = 2, interaction_only: bool = False,
                 include_bias: bool = False, max_features: Optional[int] = None):
        self.degree = degree
        self.interaction_only = interaction_only
        self.include_bias = include_bias
        self.max_features = max_features
        self.poly = None
        self.selected_features = []
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'FeatureInteractionEngineer':
        """Fit the polynomial feature generator."""
        X_numeric = X.select_dtypes(include=[np.number]).fillna(0)

        if X_numeric.shape[1] < 2:
            self.poly = None
            return self

        self.poly = PolynomialFeatures(
            degree=self.degree,
            interaction_only=self.interaction_only,
            include_bias=self.include_bias
        )

        X_poly = self.poly.fit_transform(X_numeric)

        # Get feature names
        feature_names = self.poly.get_feature_names_out(X_numeric.columns)

        # Limit features if specified
        if self.max_features and len(feature_names) > self.max_features:
            # Select most important features using correlation with target (if available)
            if y is not None and len(y) == len(X):
                correlations = []
                for i, name in enumerate(feature_names):
                    if X_poly.shape[1] > i:
                        corr = abs(np.corrcoef(X_poly[:, i], y.fillna(y.mean()))[0, 1])
                        correlations.append((name, corr if not np.isnan(corr) else 0))

                correlations.sort(key=lambda x: x[1], reverse=True)
                self.selected_features = [name for name, _ in correlations[:self.max_features]]
            else:
                # Random selection if no target
                indices = np.random.choice(len(feature_names), self.max_features, replace=False)
                self.selected_features = [feature_names[i] for i in indices]
        else:
            self.selected_features = list(feature_names)

        self.feature_names = self.selected_features
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with polynomial features."""
        if self.poly is None:
            return pd.DataFrame(index=X.index)

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0)
        X_poly = self.poly.transform(X_numeric)

        # Create DataFrame with selected features
        features = pd.DataFrame(
            X_poly,
            index=X.index,
            columns=self.poly.get_feature_names_out(X_numeric.columns)
        )

        # Select only the chosen features
        if self.selected_features:
            available_features = [col for col in self.selected_features if col in features.columns]
            features = features[available_features]

        return features


class OutlierDetectionEngineer(FeatureEngineer):
    """Outlier detection and robust statistics feature engineering."""

    def __init__(self, methods: List[str] = None, contamination: float = 0.1,
                 include_scores: bool = True, include_flags: bool = True):
        self.methods = methods or ['isolation_forest', 'local_outlier_factor', 'elliptic_envelope']
        self.contamination = contamination
        self.include_scores = include_scores
        self.include_flags = include_flags
        self.detectors = {}
        self.scalers = {}
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'OutlierDetectionEngineer':
        """Fit outlier detection models."""
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        from sklearn.covariance import EllipticEnvelope
        from sklearn.preprocessing import StandardScaler

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values

        if X_numeric.shape[1] == 0:
            return self

        self.feature_names = []

        for method in self.methods:
            if method == 'isolation_forest':
                detector = IsolationForest(contamination=self.contamination, random_state=42)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_numeric)
                detector.fit(X_scaled)

                self.detectors[method] = detector
                self.scalers[method] = scaler

                if self.include_scores:
                    self.feature_names.append(f"{method}_score")
                if self.include_flags:
                    self.feature_names.append(f"{method}_outlier")

            elif method == 'local_outlier_factor':
                detector = LocalOutlierFactor(contamination=self.contamination, novelty=True)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_numeric)
                detector.fit(X_scaled)

                self.detectors[method] = detector
                self.scalers[method] = scaler

                if self.include_scores:
                    self.feature_names.append(f"{method}_score")
                if self.include_flags:
                    self.feature_names.append(f"{method}_outlier")

            elif method == 'elliptic_envelope':
                detector = EllipticEnvelope(contamination=self.contamination, random_state=42)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_numeric)
                detector.fit(X_scaled)

                self.detectors[method] = detector
                self.scalers[method] = scaler

                if self.include_scores:
                    self.feature_names.append(f"{method}_score")
                if self.include_flags:
                    self.feature_names.append(f"{method}_outlier")

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with outlier detection features."""
        features = pd.DataFrame(index=X.index)

        if not self.detectors:
            return features

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values

        for method, detector in self.detectors.items():
            scaler = self.scalers[method]
            X_scaled = scaler.transform(X_numeric)

            if method == 'local_outlier_factor':
                # LOF decision_function gives negative scores for outliers
                scores = detector.decision_function(X_scaled)
                predictions = detector.predict(X_scaled)
            else:
                scores = detector.decision_function(X_scaled)
                predictions = detector.predict(X_scaled)

            if self.include_scores:
                features[f"{method}_score"] = scores

            if self.include_flags:
                # Convert predictions to binary flags (1 for inlier, 0 for outlier)
                features[f"{method}_outlier"] = (predictions == -1).astype(int)

        return features.fillna(0)


class AutomatedFeatureSelector(FeatureEngineer):
    """Automated feature selection using multiple methods."""

    def __init__(self, methods: List[str] = None, target_type: str = "regression",
                 max_features: Optional[int] = None, cv_folds: int = 5):
        self.methods = methods or ['mutual_info', 'correlation', 'importance', 'recursive']
        self.target_type = target_type
        self.max_features = max_features
        self.cv_folds = cv_folds
        self.selected_features = []
        self.feature_importance = {}
        self.selector = None

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'AutomatedFeatureSelector':
        """Fit automated feature selector."""
        if y is None:
            raise ValueError("Target variable y is required for feature selection")

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0)

        if X_numeric.shape[1] == 0:
            return self

        all_scores = {}

        # Mutual Information
        if 'mutual_info' in self.methods:
            if self.target_type == 'regression':
                scores = mutual_info_regression(X_numeric.values, y.values)
            else:
                scores = mutual_info_classif(X_numeric.values, y.values)

            for col, score in zip(X_numeric.columns, scores):
                all_scores[col] = all_scores.get(col, 0) + score

        # Correlation-based selection
        if 'correlation' in self.methods:
            for col in X_numeric.columns:
                corr = abs(X_numeric[col].corr(y))
                if not np.isnan(corr):
                    all_scores[col] = all_scores.get(col, 0) + corr

        # Feature importance using Random Forest
        if 'importance' in self.methods:
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

            if self.target_type == 'regression':
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                rf = RandomForestClassifier(n_estimators=100, random_state=42)

            rf.fit(X_numeric.values, y.values)
            for col, importance in zip(X_numeric.columns, rf.feature_importances_):
                all_scores[col] = all_scores.get(col, 0) + importance

        # Recursive feature elimination
        if 'recursive' in self.methods and len(X_numeric.columns) > 10:
            from sklearn.feature_selection import RFE

            if self.target_type == 'regression':
                from sklearn.linear_model import LinearRegression
                estimator = LinearRegression()
            else:
                from sklearn.linear_model import LogisticRegression
                estimator = LogisticRegression(random_state=42)

            rfe = RFE(estimator=estimator, n_features_to_select=max(5, len(X_numeric.columns) // 2))
            rfe.fit(X_numeric.values, y.values)

            for col, selected in zip(X_numeric.columns, rfe.support_):
                if selected:
                    all_scores[col] = all_scores.get(col, 0) + 1

        # Sort features by combined score
        sorted_features = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)

        # Select top features
        if self.max_features:
            self.selected_features = [feat for feat, _ in sorted_features[:self.max_features]]
        else:
            # Use elbow method or keep top 50% by default
            n_features = max(5, len(sorted_features) // 2)
            self.selected_features = [feat for feat, _ in sorted_features[:n_features]]

        # Store importance scores
        self.feature_importance = dict(sorted_features)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform by selecting features."""
        available_features = [col for col in self.selected_features if col in X.columns]
        if not available_features:
            return pd.DataFrame(index=X.index)

        return X[available_features].copy()


class FeatureScalerEngineer(FeatureEngineer):
    """Advanced feature scaling and normalization."""

    def __init__(self, methods: List[str] = None, quantile_range: Tuple[float, float] = (25.0, 75.0)):
        self.methods = methods or ['standard', 'robust', 'minmax', 'quantile']
        self.quantile_range = quantile_range
        self.scalers = {}
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'FeatureScalerEngineer':
        """Fit scalers for each method."""
        X_numeric = X.select_dtypes(include=[np.number]).fillna(0)

        if X_numeric.shape[1] == 0:
            return self

        self.feature_names = []

        for method in self.methods:
            if method == 'standard':
                scaler = StandardScaler()
                scaler.fit(X_numeric.values)
                self.scalers[method] = scaler
                self.feature_names.extend([f"{col}_standard" for col in X_numeric.columns])

            elif method == 'robust':
                scaler = RobustScaler(quantile_range=self.quantile_range)
                scaler.fit(X_numeric.values)
                self.scalers[method] = scaler
                self.feature_names.extend([f"{col}_robust" for col in X_numeric.columns])

            elif method == 'minmax':
                scaler = MinMaxScaler()
                scaler.fit(X_numeric.values)
                self.scalers[method] = scaler
                self.feature_names.extend([f"{col}_minmax" for col in X_numeric.columns])

            elif method == 'quantile':
                # Quantile normalization (simplified)
                self.scalers[method] = X_numeric.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
                self.feature_names.extend([f"{col}_quantile" for col in X_numeric.columns])

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with multiple scaling methods."""
        features = pd.DataFrame(index=X.index)
        X_numeric = X.select_dtypes(include=[np.number]).fillna(0)

        if X_numeric.shape[1] == 0:
            return features

        for method, scaler in self.scalers.items():
            if method == 'quantile':
                # Apply quantile transformation
                for col in X_numeric.columns:
                    quantiles = scaler[col]
                    scaled = pd.Series(index=X_numeric.index, dtype=float)

                    for val in X_numeric[col]:
                        # Find appropriate quantile
                        if val <= quantiles.iloc[0]:
                            scaled_val = 0.0
                        elif val >= quantiles.iloc[-1]:
                            scaled_val = 1.0
                        else:
                            # Linear interpolation between quantiles
                            scaled_val = 0.5  # Simplified

                        scaled.loc[scaled.index] = scaled_val

                    features[f"{col}_quantile"] = scaled
            else:
                # Standard sklearn scaling
                X_scaled = scaler.transform(X_numeric.values)
                for i, col in enumerate(X_numeric.columns):
                    features[f"{col}_{method}"] = X_scaled[:, i]

        return features.fillna(0)


class ClusteringFeatureEngineer(FeatureEngineer):
    """Feature engineering using clustering techniques."""

    def __init__(self, methods: List[str] = None, n_clusters_range: Tuple[int, int] = (2, 10),
                 include_distances: bool = True, include_labels: bool = True):
        self.methods = methods or ['kmeans', 'dbscan']
        self.n_clusters_range = n_clusters_range
        self.include_distances = include_distances
        self.include_labels = include_labels
        self.clusterers = {}
        self.best_n_clusters = {}
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'ClusteringFeatureEngineer':
        """Fit clustering models."""
        from sklearn.metrics import silhouette_score

        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values

        if X_numeric.shape[1] == 0:
            return self

        self.feature_names = []

        for method in self.methods:
            if method == 'kmeans':
                best_score = -1
                best_k = self.n_clusters_range[0]
                best_model = None

                # Find optimal number of clusters
                for n_clusters in range(self.n_clusters_range[0], self.n_clusters_range[1] + 1):
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    labels = kmeans.fit_predict(X_numeric)

                    if len(np.unique(labels)) > 1:
                        score = silhouette_score(X_numeric, labels)
                        if score > best_score:
                            best_score = score
                            best_k = n_clusters
                            best_model = kmeans

                if best_model:
                    self.clusterers[method] = best_model
                    self.best_n_clusters[method] = best_k

                    if self.include_labels:
                        self.feature_names.append(f"{method}_label")
                    if self.include_distances:
                        for i in range(best_k):
                            self.feature_names.append(f"{method}_dist_to_centroid_{i}")

            elif method == 'dbscan':
                # DBSCAN with automatic parameter selection
                best_score = -1
                best_model = None

                eps_values = np.linspace(0.1, 2.0, 10)
                min_samples_values = range(3, 10)

                for eps in eps_values:
                    for min_samples in min_samples_values:
                        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
                        labels = dbscan.fit_predict(X_numeric)

                        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                        if n_clusters >= 2:
                            score = silhouette_score(X_numeric, labels)
                            if score > best_score:
                                best_score = score
                                best_model = dbscan

                if best_model:
                    self.clusterers[method] = best_model

                    if self.include_labels:
                        self.feature_names.append(f"{method}_label")
                    # DBSCAN doesn't have centroids, so no distance features

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data with clustering features."""
        features = pd.DataFrame(index=X.index)
        X_numeric = X.select_dtypes(include=[np.number]).fillna(0).values

        if X_numeric.shape[1] == 0:
            return features

        for method, clusterer in self.clusterers.items():
            if method == 'kmeans':
                labels = clusterer.predict(X_numeric)
                centroids = clusterer.cluster_centers_

                if self.include_labels:
                    features[f"{method}_label"] = labels

                if self.include_distances:
                    for i, centroid in enumerate(centroids):
                        distances = np.linalg.norm(X_numeric - centroid, axis=1)
                        features[f"{method}_dist_to_centroid_{i}"] = distances

            elif method == 'dbscan':
                labels = clusterer.fit_predict(X_numeric)  # DBSCAN needs fit_predict for new data

                if self.include_labels:
                    features[f"{method}_label"] = labels

        return features.fillna(0)


class ComprehensiveFeatureEngineer:
    """Comprehensive feature engineering pipeline combining multiple techniques."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.engineers = {}
        self.feature_names = []

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for comprehensive feature engineering."""
        return {
            'statistical': {'windows': [5, 10, 20], 'include_moments': True, 'include_entropy': True},
            'time_series': {'include_seasonal': True, 'include_trend': True, 'freq': 24},
            'nlp': {'sentiment_analysis': True, 'text_complexity': True},
            'image': {'include_color': True, 'include_texture': True},
            'audio': {'include_spectral': True, 'include_temporal': True},
            'dimensionality': {'method': 'pca', 'explained_variance_ratio': 0.95},
            'interactions': {'degree': 2, 'interaction_only': True},
            'outliers': {'methods': ['isolation_forest'], 'contamination': 0.1},
            'selection': {'max_features': 50},
            'scaling': {'methods': ['standard', 'robust']},
            'clustering': {'n_clusters_range': (2, 8)}
        }

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'ComprehensiveFeatureEngineer':
        """Fit all feature engineers."""
        self.engineers = {}
        self.feature_names = []

        # Statistical features
        if self.config.get('statistical', {}).get('enabled', True):
            engineer = StatisticalFeatureEngineer(**self.config['statistical'])
            engineer.fit(X, y)
            self.engineers['statistical'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Time series features
        if self.config.get('time_series', {}).get('enabled', True):
            engineer = TimeSeriesFeatureEngineer(**self.config['time_series'])
            engineer.fit(X, y)
            self.engineers['time_series'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # NLP features
        if self.config.get('nlp', {}).get('enabled', True):
            engineer = NLPFeatureEngineer(**self.config['nlp'])
            engineer.fit(X, y)
            self.engineers['nlp'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Image features
        if self.config.get('image', {}).get('enabled', True):
            engineer = ImageFeatureEngineer(**self.config['image'])
            engineer.fit(X, y)
            self.engineers['image'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Audio features
        if self.config.get('audio', {}).get('enabled', True):
            engineer = AudioFeatureEngineer(**self.config['audio'])
            engineer.fit(X, y)
            self.engineers['audio'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Dimensionality reduction
        if self.config.get('dimensionality', {}).get('enabled', True):
            engineer = DimensionalityReductionEngineer(**self.config['dimensionality'])
            engineer.fit(X, y)
            self.engineers['dimensionality'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Feature interactions
        if self.config.get('interactions', {}).get('enabled', True):
            engineer = FeatureInteractionEngineer(**self.config['interactions'])
            engineer.fit(X, y)
            self.engineers['interactions'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Outlier detection
        if self.config.get('outliers', {}).get('enabled', True):
            engineer = OutlierDetectionEngineer(**self.config['outliers'])
            engineer.fit(X, y)
            self.engineers['outliers'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Automated feature selection (applied last)
        if self.config.get('selection', {}).get('enabled', True) and y is not None:
            engineer = AutomatedFeatureSelector(**self.config['selection'])
            engineer.fit(X, y)
            self.engineers['selection'] = engineer
            self.feature_names = engineer.selected_features

        # Scaling (applied after selection)
        if self.config.get('scaling', {}).get('enabled', True):
            engineer = FeatureScalerEngineer(**self.config['scaling'])
            engineer.fit(X, y)
            self.engineers['scaling'] = engineer
            self.feature_names.extend(engineer.feature_names)

        # Clustering
        if self.config.get('clustering', {}).get('enabled', True):
            engineer = ClusteringFeatureEngineer(**self.config['clustering'])
            engineer.fit(X, y)
            self.engineers['clustering'] = engineer
            self.feature_names.extend(engineer.feature_names)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data using all fitted engineers."""
        all_features = [X]  # Start with original features

        for name, engineer in self.engineers.items():
            if name == 'selection':
                # Selection is applied to all previous features
                combined = pd.concat(all_features, axis=1)
                selected = engineer.transform(combined)
                all_features = [selected]
            elif name == 'scaling':
                # Scaling is applied to selected features
                combined = pd.concat(all_features, axis=1)
                scaled = engineer.transform(combined)
                all_features = [scaled]
            else:
                # Other engineers work on original data
                features = engineer.transform(X)
                if not features.empty:
                    all_features.append(features)

        # Combine all features
        if len(all_features) == 1:
            return all_features[0]
        else:
            return pd.concat(all_features, axis=1).fillna(0)


@dataclass(slots=True)
class FeatureConfig:
    name: str
    function: Callable[..., pd.DataFrame | pd.Series]
    kwargs: Mapping[str, object] = field(default_factory=dict)
    required_columns: Sequence[str] = field(default_factory=list)
    windows: Sequence[int] = field(default_factory=tuple)
    prefix: Optional[str] = None
    include_original: bool = False


def create_features(
    frame: pd.DataFrame,
    *,
    price_columns: Sequence[str] = DEFAULT_PRICE_COLUMNS,
    volume_column: Optional[str] = "volume",
    feature_sets: Sequence[str] | None = None,
    windows: Sequence[int] = (5, 10, 20, 55, 100, 200),
    custom_features: Sequence[FeatureConfig] | None = None,
    dropna: bool = True,
    add_returns: bool = True,
    benchmark_column: Optional[str] = None,
    prune_original: bool = False,
) -> pd.DataFrame:
    """Generate a rich set of technical features from a price DataFrame."""

    if frame.empty:
        raise ValueError("Input DataFrame is empty.")

    df = frame.copy()
    catalog = _build_catalog(frame, price_columns, volume_column, benchmark_column)

    if feature_sets:
        selected = {key: value for key, value in catalog.items() if value[0] in feature_sets}
    else:
        selected = catalog

    if custom_features:
        for cfg in custom_features:
            selected[cfg.name] = ("custom", cfg)

    feature_frames: List[pd.DataFrame] = [df]
    base_columns = set(df.columns)

    for name, entry in selected.items():
        category, config = entry
        feature_configs = _expand_config(config, category, windows)
        for cfg in feature_configs:
            if not _requirements_met(df, cfg.required_columns):
                continue
            try:
                result = cfg.function(df, **cfg.kwargs)
            except Exception:
                continue
            result_df = _normalize_output(df.index, result, base_columns=base_columns, prefix=cfg.prefix or name)
            if not result_df.empty:
                feature_frames.append(result_df)

    features = pd.concat(feature_frames, axis=1)

    if add_returns and "close" in features.columns:
        features["ret_1"] = features["close"].pct_change()
        features["ret_log_1"] = np.log(features["close"]).diff()

    if prune_original:
        for column in price_columns:
            if column in features.columns:
                features.pop(column)
        if volume_column and volume_column in features.columns:
            features.pop(volume_column)

    if dropna:
        features = features.dropna()

    return features


def _build_catalog(
    frame: pd.DataFrame,
    price_columns: Sequence[str],
    volume_column: Optional[str],
    benchmark_column: Optional[str],
) -> Dict[str, tuple[str, FeatureConfig]]:
    catalog: Dict[str, tuple[str, FeatureConfig]] = {}

    close_kwargs = {"column": "close"}

    catalog["sma"] = (
        "trend",
        FeatureConfig(
            name="sma",
            function=lambda df, window: sma(df, column="close", window=window, inplace=False),
            required_columns=["close"],
        ),
    )
    catalog["ema"] = (
        "trend",
        FeatureConfig(
            name="ema",
            function=lambda df, period: ema(df, column="close", period=period, inplace=False),
            required_columns=["close"],
        ),
    )
    catalog["wma"] = (
        "trend",
        FeatureConfig(
            name="wma",
            function=lambda df, window: wma(df, column="close", window=window, inplace=False),
            required_columns=["close"],
        ),
    )
    catalog["hma"] = (
        "trend",
        FeatureConfig(
            name="hma",
            function=lambda df, period: hma(df, column="close", period=period, inplace=False),
            required_columns=["close"],
        ),
    )

    catalog["rsi"] = (
        "momentum",
        FeatureConfig(
            name="rsi",
            function=lambda df, period: rsi(
                df,
                column="close",
                period=period,
                inplace=False,
                name=f"rsi_{period}",
            ),
            required_columns=["close"],
            prefix="rsi",
        ),
    )

    catalog["macd"] = (
        "momentum",
        FeatureConfig(
            name="macd",
            function=lambda df, fast, slow, signal: macd(
                df,
                column="close",
                fast_period=fast,
                slow_period=slow,
                signal_period=signal,
                inplace=False,
            ),
            kwargs={"fast": 12, "slow": 26, "signal": 9},
            required_columns=["close"],
        ),
    )

    catalog["bollinger"] = (
        "volatility",
        FeatureConfig(
            name="boll",
            function=lambda df, period: bollinger_bands(df, column="close", period=period, inplace=False, prefix=f"BOLL_{period}"),
            required_columns=["close"],
        ),
    )

    catalog["keltner"] = (
        "volatility",
        FeatureConfig(
            name="keltner",
            function=lambda df, ema_period, atr_period: keltner_channels(
                df,
                ema_period=ema_period,
                atr_period=atr_period,
                price_column="close",
                inplace=False,
                prefix=f"KC_{ema_period}_{atr_period}"
            ),
            kwargs={"ema_period": 20, "atr_period": 10},
            required_columns=["close", "high", "low"],
        ),
    )

    catalog["atr"] = (
        "volatility",
        FeatureConfig(
            name="atr",
            function=lambda df, period: atr(df, period=period, inplace=False, name=f"ATR_{period}"),
            required_columns=["high", "low", "close"],
        ),
    )

    catalog["true_range"] = (
        "volatility",
        FeatureConfig(
            name="tr",
            function=lambda df: true_range(df).to_frame("true_range"),
            required_columns=["high", "low", "close"],
        ),
    )

    catalog["stochastic"] = (
        "momentum",
        FeatureConfig(
            name="stoch",
            function=lambda df, k, d: stochastic(
                df, high="high", low="low", close="close", k_period=k, d_period=d, inplace=False, prefix=f"STO_{k}_{d}"
            ),
            kwargs={"k": 14, "d": 3},
            required_columns=["high", "low", "close"],
        ),
    )

    catalog["ichimoku"] = (
        "trend",
        FeatureConfig(
            name="ichimoku",
            function=lambda df: ichimoku(df, inplace=False, prefix="ICH"),
            required_columns=["high", "low", "close"],
        ),
    )

    catalog["zscore"] = (
        "stat",
        FeatureConfig(
            name="zscore",
            function=lambda df, period: zscore(df, column="close", window=period, inplace=False),
            required_columns=["close"],
        ),
    )

    catalog["percent_rank"] = (
        "stat",
        FeatureConfig(
            name="prank",
            function=lambda df, period: percent_rank(df, column="close", window=period, inplace=False),
            required_columns=["close"],
        ),
    )

    catalog["lag"] = (
        "stat",
        FeatureConfig(
            name="lag",
            function=lambda df, periods: lag(df, column="close", periods=periods, inplace=False, name=f"LAG_{periods}"),
            required_columns=["close"],
            windows=(1, 2, 5, 10, 20),
        ),
    )

    catalog["diff"] = (
        "stat",
        FeatureConfig(
            name="diff",
            function=lambda df, periods: difference(df, column="close", periods=periods, inplace=False, name=f"DIFF_{periods}"),
            required_columns=["close"],
            windows=(1, 2, 5, 10),
        ),
    )

    catalog["cumret"] = (
        "stat",
        FeatureConfig(
            name="cumret",
            function=lambda df: cumulative_return(df, column="close", inplace=False),
            required_columns=["close"],
        ),
    )

    if volume_column and volume_column in frame.columns:
        catalog["vwma"] = (
            "volume",
            FeatureConfig(
                name="vwma",
                function=lambda df, window: vwma(
                    df,
                    price_column="close",
                    volume_column=volume_column,
                    window=window,
                    inplace=False,
                    name=f"VWMA_{window}"
                ),
                required_columns=["close", volume_column],
            ),
        )

        catalog["obv"] = (
            "volume",
            FeatureConfig(
                name="obv",
                function=lambda df: obv(
                    df,
                    price_column="close",
                    volume_column=volume_column,
                    inplace=False,
                    name="OBV",
                ),
                required_columns=["close", volume_column],
            ),
        )

        catalog["pvo"] = (
            "volume",
            FeatureConfig(
                name="pvo",
                function=lambda df, fast, slow, signal: pvo(
                    df,
                    column=volume_column,
                    fast_period=fast,
                    slow_period=slow,
                    signal_period=signal,
                    inplace=False,
                    prefix=f"PVO_{fast}_{slow}_{signal}"
                ),
                required_columns=[volume_column],
                kwargs={"fast": 12, "slow": 26, "signal": 9},
            ),
        )

    if benchmark_column and benchmark_column in frame.columns:
        catalog["beta"] = (
            "cross",
            FeatureConfig(
                name="beta",
                function=lambda df, window: rolling_beta(
                    df,
                    column="close",
                    benchmark=benchmark_column,
                    window=window,
                    inplace=False,
                    name=f"BETA_{window}"
                ),
                required_columns=["close", benchmark_column],
            ),
        )
        catalog["corr"] = (
            "cross",
            FeatureConfig(
                name="corr",
                function=lambda df, window: rolling_correlation(
                    df,
                    column_x="close",
                    column_y=benchmark_column,
                    window=window,
                    inplace=False,
                    name=f"CORR_{window}"
                ),
                required_columns=["close", benchmark_column],
            ),
        )

    catalog["vol"] = (
        "volatility",
        FeatureConfig(
            name="vol",
            function=lambda df, window: rolling_volatility(df, column="close", window=window, inplace=False, name=f"VOL_{window}"),
            required_columns=["close"],
        ),
    )

    catalog["donchian"] = (
        "trend",
        FeatureConfig(
            name="donchian",
            function=lambda df, window: donchian_channels(
                df,
                column_high="high",
                column_low="low",
                period=window,
                inplace=False,
                prefix=f"DC_{window}"
            ),
            required_columns=["high", "low"],
        ),
    )

    return catalog


def _expand_config(config: FeatureConfig, category: str, default_windows: Sequence[int]) -> List[FeatureConfig]:
    configs: List[FeatureConfig] = []
    windows = config.windows or default_windows

    argnames = config.function.__code__.co_varnames
    window_args = [name for name in ("window", "period", "periods") if name in argnames]

    if window_args:
        for window in windows:
            kwargs = dict(config.kwargs)
            for arg in window_args:
                kwargs[arg] = window
            configs.append(
                FeatureConfig(
                    name=f"{config.name}_{window}",
                    function=lambda df, _cfg=config, _kwargs=kwargs: _cfg.function(df, **_kwargs),
                    kwargs={},
                    required_columns=config.required_columns,
                    prefix=config.prefix or f"{config.name}_{window}",
                )
            )
    else:
        configs.append(config)

    return configs


def _normalize_output(
    index: pd.Index,
    result: pd.DataFrame | pd.Series,
    *,
    base_columns: set[str],
    prefix: str | None = None,
) -> pd.DataFrame:
    if isinstance(result, pd.Series):
        series = result.reindex(index)
        if prefix and series.name:
            name = f"{prefix}_{series.name}"
        elif prefix:
            name = prefix
        else:
            name = series.name or "feature"
        return series.to_frame(name)
    elif isinstance(result, pd.DataFrame):
        frame = result.reindex(index)
        new_columns = [col for col in frame.columns if col not in base_columns]
        if new_columns:
            frame = frame[new_columns]
        if prefix:
            frame = frame.add_prefix(f"{prefix}_")
        return frame
    else:
        raise TypeError("Indicator output must be a pandas Series or DataFrame.")


def _requirements_met(df: pd.DataFrame, required: Iterable[str]) -> bool:
    return all(column in df.columns for column in required)


# =============================================================================
# ADVANCED FEATURE ENGINEERING UTILITIES
# =============================================================================

def create_comprehensive_features(
    data: pd.DataFrame,
    target: Optional[pd.Series] = None,
    config: Optional[Dict[str, Any]] = None,
    enable_progress_bar: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Create comprehensive features using all available feature engineering techniques.

    Args:
        data: Input DataFrame
        target: Target variable for supervised feature selection
        config: Configuration for feature engineering
        enable_progress_bar: Whether to show progress

    Returns:
        Tuple of (features, metadata)
    """
    if config is None:
        config = {}

    # Initialize comprehensive feature engineer
    engineer = ComprehensiveFeatureEngineer(config)

    # Fit and transform
    engineer.fit(data, target)
    features = engineer.transform(data)

    # Create metadata
    metadata = {
        'n_original_features': data.shape[1],
        'n_engineered_features': features.shape[1],
        'engineers_used': list(engineer.engineers.keys()),
        'feature_names': features.columns.tolist(),
        'config_used': config
    }

    return features, metadata


def create_temporal_features(
    data: pd.DataFrame,
    time_column: str = 'timestamp',
    features_config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Create advanced temporal features from time series data.

    Args:
        data: Input DataFrame with temporal data
        time_column: Name of timestamp column
        features_config: Configuration for temporal features

    Returns:
        DataFrame with temporal features
    """
    if features_config is None:
        features_config = {}

    # Ensure timestamp column exists
    if time_column not in data.columns:
        raise ValueError(f"Time column '{time_column}' not found in data")

    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(data[time_column]):
        data = data.copy()
        data[time_column] = pd.to_datetime(data[time_column])

    features = pd.DataFrame(index=data.index)

    # Time-based features
    dt = data[time_column]

    # Basic temporal features
    features['hour'] = dt.dt.hour
    features['day_of_week'] = dt.dt.dayofweek
    features['day_of_month'] = dt.dt.day
    features['month'] = dt.dt.month
    features['quarter'] = dt.dt.quarter
    features['year'] = dt.dt.year
    features['is_weekend'] = dt.dt.dayofweek.isin([5, 6]).astype(int)
    features['is_month_start'] = dt.dt.is_month_start.astype(int)
    features['is_month_end'] = dt.dt.is_month_end.astype(int)
    features['is_quarter_start'] = dt.dt.is_quarter_start.astype(int)
    features['is_quarter_end'] = dt.dt.is_quarter_end.astype(int)

    # Cyclic encoding for periodic features
    features['hour_sin'] = np.sin(2 * np.pi * dt.dt.hour / 24)
    features['hour_cos'] = np.cos(2 * np.pi * dt.dt.hour / 24)
    features['month_sin'] = np.sin(2 * np.pi * dt.dt.month / 12)
    features['month_cos'] = np.cos(2 * np.pi * dt.dt.month / 12)
    features['day_of_week_sin'] = np.sin(2 * np.pi * dt.dt.dayofweek / 7)
    features['day_of_week_cos'] = np.cos(2 * np.pi * dt.dt.dayofweek / 7)

    # Time differences
    time_diff = dt.diff()
    features['time_diff_seconds'] = time_diff.dt.total_seconds()
    features['time_diff_hours'] = time_diff.dt.total_seconds() / 3600
    features['time_diff_days'] = time_diff.dt.total_seconds() / (3600 * 24)

    # Rolling time statistics
    features['time_diff_rolling_mean'] = features['time_diff_seconds'].rolling(10).mean()
    features['time_diff_rolling_std'] = features['time_diff_seconds'].rolling(10).std()

    # Business day features
    try:
        features['is_business_day'] = dt.dt.dayofweek.isin([0, 1, 2, 3, 4]).astype(int)
        features['business_days_since_start'] = dt.dt.dayofweek.cumsum()  # Simplified
    except:
        features['is_business_day'] = 0

    # Holiday features (simplified)
    # In practice, you'd use a proper holiday calendar
    features['is_christmas_period'] = ((dt.dt.month == 12) & (dt.dt.day >= 20)).astype(int)
    features['is_new_year_period'] = ((dt.dt.month == 1) & (dt.dt.day <= 5)).astype(int)

    return features.fillna(0)


def create_cross_sectional_features(
    data: pd.DataFrame,
    group_column: Optional[str] = None,
    rank_features: bool = True,
    zscore_features: bool = True,
    percentile_features: bool = True
) -> pd.DataFrame:
    """
    Create cross-sectional features across groups or entire dataset.

    Args:
        data: Input DataFrame
        group_column: Column to group by for cross-sectional analysis
        rank_features: Whether to create ranking features
        zscore_features: Whether to create z-score features
        percentile_features: Whether to create percentile features

    Returns:
        DataFrame with cross-sectional features
    """
    features = pd.DataFrame(index=data.index)
    numeric_columns = data.select_dtypes(include=[np.number]).columns

    for col in numeric_columns:
        series = data[col]

        if group_column and group_column in data.columns:
            # Group-wise transformations
            if rank_features:
                features[f"{col}_group_rank"] = series.groupby(data[group_column]).rank(pct=True)
            if zscore_features:
                features[f"{col}_group_zscore"] = series.groupby(data[group_column]).transform(
                    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
                )
            if percentile_features:
                features[f"{col}_group_percentile"] = series.groupby(data[group_column]).rank(pct=True)
        else:
            # Global transformations
            if rank_features:
                features[f"{col}_global_rank"] = series.rank(pct=True)
            if zscore_features:
                features[f"{col}_global_zscore"] = (series - series.mean()) / series.std() if series.std() > 0 else 0
            if percentile_features:
                features[f"{col}_global_percentile"] = series.rank(pct=True)

        # Additional cross-sectional features
        features[f"{col}_vs_median"] = series - series.median()
        features[f"{col}_vs_mean"] = series - series.mean()
        features[f"{col}_decile"] = pd.qcut(series, 10, labels=False, duplicates='drop')

    return features.fillna(0)


def create_interaction_features(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None,
    degree: int = 2,
    max_features: Optional[int] = None
) -> pd.DataFrame:
    """
    Create feature interactions using polynomial features.

    Args:
        data: Input DataFrame
        columns: Columns to use for interactions (default: all numeric)
        degree: Degree of polynomial features
        max_features: Maximum number of interaction features

    Returns:
        DataFrame with interaction features
    """
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()

    if len(columns) < 2:
        return pd.DataFrame(index=data.index)

    # Select data
    X = data[columns].fillna(0)

    # Create polynomial features
    poly = PolynomialFeatures(degree=degree, interaction_only=True, include_bias=False)
    X_poly = poly.fit_transform(X)

    # Get feature names
    feature_names = poly.get_feature_names_out(X.columns)

    # Create DataFrame
    features = pd.DataFrame(X_poly, index=data.index, columns=feature_names)

    # Remove original columns (they're included in interactions)
    features = features.drop(columns=[col for col in columns if col in features.columns])

    # Limit features if specified
    if max_features and len(features.columns) > max_features:
        # Select most variable features
        variances = features.var()
        top_features = variances.nlargest(max_features).index
        features = features[top_features]

    return features.fillna(0)


def create_automated_features(
    data: pd.DataFrame,
    target: Optional[pd.Series] = None,
    methods: Optional[List[str]] = None,
    max_features: int = 100
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Automatically create features using multiple techniques.

    Args:
        data: Input DataFrame
        target: Target variable for supervised feature creation
        methods: List of feature engineering methods to use
        max_features: Maximum number of features to create

    Returns:
        Tuple of (features, feature_importance_dict)
    """
    if methods is None:
        methods = ['statistical', 'interactions', 'scaling']

    all_features = []
    feature_importance = {}

    # Statistical features
    if 'statistical' in methods:
        stat_engineer = StatisticalFeatureEngineer()
        stat_engineer.fit(data, target)
        stat_features = stat_engineer.transform(data)
        if not stat_features.empty:
            all_features.append(stat_features)
            feature_importance['statistical'] = len(stat_features.columns)

    # Interaction features
    if 'interactions' in methods:
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            interact_features = create_interaction_features(data, numeric_cols[:10], degree=2, max_features=20)
            if not interact_features.empty:
                all_features.append(interact_features)
                feature_importance['interactions'] = len(interact_features.columns)

    # Scaling features
    if 'scaling' in methods:
        scale_engineer = FeatureScalerEngineer(methods=['standard', 'robust'])
        scale_engineer.fit(data, target)
        scale_features = scale_engineer.transform(data)
        if not scale_features.empty:
            all_features.append(scale_features)
            feature_importance['scaling'] = len(scale_features.columns)

    # Combine all features
    if all_features:
        combined_features = pd.concat(all_features, axis=1)
    else:
        combined_features = data.copy()

    # Limit total features
    if len(combined_features.columns) > max_features:
        # Simple feature selection: keep most variable features
        variances = combined_features.select_dtypes(include=[np.number]).var()
        top_features = variances.nlargest(max_features).index
        combined_features = combined_features[top_features]

    metadata = {
        'methods_used': methods,
        'total_features_created': len(combined_features.columns),
        'feature_importance': feature_importance,
        'original_features': data.shape[1]
    }

    return combined_features, metadata


def validate_features(
    features: pd.DataFrame,
    target: Optional[pd.Series] = None,
    checks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate created features for quality and usefulness.

    Args:
        features: Feature DataFrame to validate
        target: Target variable for correlation analysis
        checks: List of validation checks to perform

    Returns:
        Dictionary with validation results
    """
    if checks is None:
        checks = ['missing_values', 'infinite_values', 'constant_features', 'high_correlation']

    results = {}

    # Missing values check
    if 'missing_values' in checks:
        missing_pct = features.isnull().mean()
        results['missing_values'] = {
            'total_missing': features.isnull().sum().sum(),
            'missing_by_column': missing_pct[missing_pct > 0].to_dict(),
            'columns_with_missing': (missing_pct > 0).sum()
        }

    # Infinite values check
    if 'infinite_values' in checks:
        infinite_mask = np.isinf(features.select_dtypes(include=[np.number]))
        results['infinite_values'] = {
            'total_infinite': infinite_mask.sum().sum(),
            'infinite_by_column': infinite_mask.sum()[infinite_mask.sum() > 0].to_dict()
        }

    # Constant features check
    if 'constant_features' in checks:
        numeric_features = features.select_dtypes(include=[np.number])
        constant_features = []
        for col in numeric_features.columns:
            if numeric_features[col].nunique() <= 1:
                constant_features.append(col)
        results['constant_features'] = constant_features

    # High correlation check
    if 'high_correlation' in checks and len(features.columns) > 1:
        numeric_features = features.select_dtypes(include=[np.number])
        if not numeric_features.empty:
            corr_matrix = numeric_features.corr().abs()
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            high_corr_pairs = []
            for col in upper.columns:
                for idx in upper.index:
                    if not pd.isna(upper.loc[idx, col]) and upper.loc[idx, col] > 0.95:
                        high_corr_pairs.append((idx, col, upper.loc[idx, col]))
            results['high_correlation'] = high_corr_pairs[:10]  # Top 10

    # Target correlation (if target provided)
    if target is not None and 'target_correlation' in checks:
        numeric_features = features.select_dtypes(include=[np.number])
        correlations = {}
        for col in numeric_features.columns:
            corr = numeric_features[col].corr(target)
            if not pd.isna(corr):
                correlations[col] = abs(corr)

        # Sort by absolute correlation
        sorted_corrs = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
        results['target_correlation'] = {
            'top_10_features': sorted_corrs[:10],
            'weak_features': [feat for feat, corr in sorted_corrs if corr < 0.01]
        }

    return results


def optimize_feature_pipeline(
    data: pd.DataFrame,
    target: pd.Series,
    pipeline_configs: List[Dict[str, Any]],
    cv_folds: int = 5,
    scoring: str = 'neg_mean_squared_error'
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Optimize feature engineering pipeline using cross-validation.

    Args:
        data: Input DataFrame
        target: Target variable
        pipeline_configs: List of pipeline configurations to test
        cv_folds: Number of CV folds
        scoring: Scoring metric

    Returns:
        Tuple of (best_config, cv_results)
    """
    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error

    results = []

    for config in pipeline_configs:
        try:
            # Create features
            if 'method' in config and config['method'] == 'comprehensive':
                engineer = ComprehensiveFeatureEngineer(config.get('config', {}))
                engineer.fit(data, target)
                features = engineer.transform(data)
            else:
                features = create_features(data, **config)

            # Handle missing values
            features = features.fillna(0)

            # Ensure we have numeric features
            numeric_features = features.select_dtypes(include=[np.number])
            if numeric_features.empty:
                continue

            # Evaluate with cross-validation
            model = RandomForestRegressor(n_estimators=100, random_state=42)

            if len(numeric_features) > 0 and len(target) == len(numeric_features):
                scores = cross_val_score(
                    model, numeric_features.values, target.values,
                    cv=cv_folds, scoring=scoring
                )

                results.append({
                    'config': config,
                    'mean_score': scores.mean(),
                    'std_score': scores.std(),
                    'n_features': len(numeric_features.columns),
                    'scores': scores.tolist()
                })

        except Exception as e:
            results.append({
                'config': config,
                'error': str(e),
                'mean_score': float('-inf')
            })

    # Find best configuration
    if results:
        best_result = max(results, key=lambda x: x.get('mean_score', float('-inf')))
        best_config = best_result['config']
    else:
        best_config = {}

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    return best_config, results_df


__all__ = [
    "create_features",
    "FeatureConfig",
    "FeatureEngineer",
    "StatisticalFeatureEngineer",
    "TimeSeriesFeatureEngineer",
    "NLPFeatureEngineer",
    "ImageFeatureEngineer",
    "AudioFeatureEngineer",
    "DimensionalityReductionEngineer",
    "FeatureInteractionEngineer",
    "OutlierDetectionEngineer",
    "AutomatedFeatureSelector",
    "FeatureScalerEngineer",
    "ClusteringFeatureEngineer",
    "ComprehensiveFeatureEngineer",
    "create_comprehensive_features",
    "create_temporal_features",
    "create_cross_sectional_features",
    "create_interaction_features",
    "create_automated_features",
    "validate_features",
    "optimize_feature_pipeline"
]
