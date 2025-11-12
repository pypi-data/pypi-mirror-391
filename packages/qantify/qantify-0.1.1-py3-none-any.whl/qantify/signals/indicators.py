"""Vectorized indicator implementations."""

from __future__ import annotations

from math import sqrt
from typing import Optional, List, Dict

import numpy as np
import pandas as pd

from .utils import attach_result, ensure_min_periods, require_columns, rolling_apply, select_series

__all__ = [
    "ema",
    "sma",
    "wma",
    "hma",
    "vwma",
    "rsi",
    "macd",
"bollinger_bands",
    "atr",
    "true_range",
    "rolling_volatility",
    "keltner_channels",
    "donchian_channels",
"stochastic",
"stochastic_rsi",
    "ichimoku",
    "zscore",
    "percent_rank",
    "cumulative_return",
    "obv",
    "pvo",
    "rolling_beta",
    "rolling_correlation",
    "lag",
    "difference",
"adx",
"cci",
"mfi",
"pivot_points",
"supertrend",
"heikin_ashi",
    # Advanced Technical Indicators
    "williams_r",
    "ultimate_oscillator",
    "chaikin_money_flow",
    "aroon",
    "aroon_oscillator",
    "elder_ray",
    "force_index",
    "ease_of_movement",
    "volume_price_trend",
    "negative_volume_index",
    "positive_volume_index",
    "accumulation_distribution",
    "chaikin_oscillator",
    "money_flow_index",
    "commodity_channel_index",
    "klinger_oscillator",
    "schaff_trend_cycle",
    "coppock_curve",
    "rainbow_oscillator",
    "dynamic_momentum_index",
    "relative_vigor_index",
    "stochastic_momentum_index",
    "triple_ema_oscillator",
    "fractal_dimension",
    "hurst_exponent",
    "lyapunov_exponent",
    "market_mechanics",
    "demand_index",
    "balance_of_power",
    "chande_momentum_oscillator",
    "psychological_line",
    "vertical_horizontal_filter",
    "trend_intensity_index",
    "bull_bear_power",
    "trix",
    "vidya",
    "alma",
    "frama",
    "gma",
    "jma",
    "lsma",
    "mcginley_dynamic",
    "median_price",
    "typical_price",
    "weighted_close_price",
    "price_channel",
    "regression_channel",
    "standard_error_channel",
    "andrews_pitchfork",
    "gann_angles",
    "fibonacci_retracements",
    "fibonacci_extensions",
    "harmonic_patterns",
    "wolfe_waves",
    "gartley_patterns",
    "head_shoulders_patterns",
    "double_top_bottom",
    "wedge_patterns",
    "triangle_patterns",
    "flag_patterns",
    "cup_handle_patterns",
    "inverse_head_shoulders",
    "ascending_descending_triangle",
    "symmetrical_triangle",
    "pennant_patterns",
    "rectangle_patterns",
    "triple_top_bottom",
    "diamond_patterns",
    "broadening_patterns",
    "contracting_patterns",
    "falling_wedge",
    "rising_wedge",
    "descending_triangle",
    "ascending_triangle",
    "bullish_engulfing",
    "bearish_engulfing",
    "hammer",
    "shooting_star",
    "doji",
    "morning_star",
    "evening_star",
    "three_white_soldiers",
    "three_black_crows",
    "piercing_pattern",
    "dark_cloud_cover",
    "harami",
    "harami_cross",
    "spinning_top",
    "marubozu",
    "tweezer_top",
    "tweezer_bottom",
    "belt_hold",
    "breakaway",
    "deliberation",
    "counterattack",
    "hanging_man",
    "gravestone_doji",
    "dragonfly_doji",
    "long_legged_doji",
    "four_price_doji",
    "tri_star",
    "unique_three_river",
    "abandoned_baby",
    "advance_block",
    "concealing_baby_swallow",
    "hikkake_pattern",
    "inside_bar",
    "outside_bar",
    "pin_bar",
    "fakey_pattern",
    "inside_bar_reversal",
    "key_reversal",
    "exhaustion_bar",
    "absorption_bar",
    "spring",
    "upthrust",
    "shakeout",
    "iceberg_pattern",
    "stop_hunt",
    "volume_climax",
    "volume_surge",
    "effort_vs_result",
    "volume_price_analysis",
    "market_profile",
    "volume_profile",
    "order_flow",
    "time_price_opportunity",
    "market_facilitation_index",
    "tick_volume",
    "volume_oscillator",
    "price_volume_trend",
    "volume_relative_strength_index",
    "volume_flow_indicator",
    "volume_weighted_average_price",
    "volume_weighted_moving_average",
    "intraday_intensity",
    "money_flow_multiplier",
    "ratio_analysis",
    "spread_analysis",
    "yield_analysis",
    "duration_analysis",
    "convexity_analysis",
    "immunization_analysis",
    "portfolio_duration_matching",
    "key_rate_duration",
    "effective_duration",
    "option_adjusted_spread",
    "z_spread",
    "i_spread",
    "g_spread",
    "ted_spread",
    "libor_oIS_spread",
    "swap_spread",
    "butterfly_spread",
    "condor_spread",
    "calendar_spread",
    "diagonal_spread",
    "ratio_spread",
    "back_spread",
    "strangle",
    "straddle",
    "collar",
    "fence",
    "iron_condor",
    "iron_butterfly",
    "christmas_tree",
    "jade_lizard",
    "risk_reversal",
    "synthetic_long",
    "synthetic_short",
    "covered_call",
    "cash_secured_put",
    "protective_put",
    "synthetic_straddle",
    "gamma_scalping",
    "delta_hedging",
    "theta_positive",
    "theta_negative",
    "vega_positive",
    "vega_negative",
    "rho_positive",
    "rho_negative",
    "lambda_analysis",
    "kappa_analysis",
    "epsilon_analysis",
    "vanna_analysis",
    "charm_analysis",
    "color_analysis",
    "speed_analysis",
    "ultima_analysis",
    "zomma_analysis",
    "veta_analysis",
    "volga_analysis",
    "veta_volga_matrix",
    "delta_gamma_hedging",
    "gamma_theta_hedging",
    "delta_theta_hedging",
    "dynamic_hedging",
    "black_scholes_model",
    "binomial_model",
    "monte_carlo_simulation",
    "heston_model",
    "sabr_model",
    "dupire_model",
    "rough_bergomi_model",
    "variance_gamma_model",
    "cgmy_model",
    "levy_process",
    "jump_diffusion_model",
    "stochastic_volatility",
    "local_volatility",
    "implied_volatility",
    "realized_volatility",
    "parkinson_volatility",
    "yang_zhang_volatility",
    "garman_klass_volatility",
    "rogers_satchell_volatility",
    "meilijson_volatility",
    "integrated_volatility",
    "quadratic_variation",
    "power_variation",
    "multifractal_volatility",
    "realized_kurtosis",
    "realized_skewness",
    "jump_variation",
    "continuous_variation",
    "bipower_variation",
    "tripower_variation",
    "minimax_estimator",
    "preaveraged_estimator",
    "kernel_estimator",
    "subsampled_estimator",
    "sparse_sampling",
    "high_frequency_analysis",
    "market_microstructure_noise",
    "epps_effect",
    "signature_plot",
    "price_impact",
    "liquidity_analysis",
    "slippage_analysis",
    "transaction_cost_analysis",
    "implementation_shortfall",
    "vwap_execution",
    "twap_execution",
    "adaptive_execution",
    "optimal_execution",
    "arrival_price_algorithm",
    "participation_rate_algorithm",
    "volume_participation",
    "iceberg_algorithm",
    "sniper_algorithm",
    "guerrilla_algorithm",
    "peg_algorithm",
    "dark_pool_execution",
    "crossing_network",
    "internalization",
    "principal_trading",
    "agency_trading",
    "flow_toxicity",
    "order_book_imbalance",
    "depth_of_market",
    "market_depth",
    "bid_ask_spread",
    "quoted_spread",
    "effective_spread",
    "realized_spread",
    "price_impact_spread",
    "roll_spread",
    "adverse_selection",
    "inventory_risk",
    "order_flow_toxicity",
    "lambda_measure",
    "hasbrouck_lambda",
    "amihud_lambda",
    "kyle_lambda",
    "glosten_lambda",
    "madhavan_lambda",
    "easley_lambda",
    "lin_lambda",
    "sarr_lambda",
    "market_resiliency",
    "price_discovery",
    "information_share",
    "common_factors",
    "idiosyncratic_volatility",
    "systematic_risk",
    "unsystematic_risk",
    "beta_estimation",
    "alpha_estimation",
    "sharpe_ratio",
    "sortino_ratio",
    "calmar_ratio",
    "omega_ratio",
    "upside_potential_ratio",
    "downside_deviation",
    "maximum_drawdown",
    "value_at_risk",
    "expected_shortfall",
    "conditional_var",
    "extreme_value_theory",
    "copula_analysis",
    "tail_risk",
    "stress_testing",
    "scenario_analysis",
    "monte_carlo_var",
    "historical_var",
    "parametric_var",
    "kernel_density_var",
    "extreme_value_var",
    "spectral_risk_measure",
    "entropic_risk_measure",
    "distortion_risk_measure",
    "coherent_risk_measure",
    "convex_risk_measure",
    "regulatory_risk_measure",
    "economic_capital",
    "risk_adjusted_return",
    "raroc",
    "rarorac",
    "eva",
    "mva",
    "cva",
    "dva",
    "fva",
    "kva",
    "xva",
    "collateral_valuation_adjustment",
    "debit_valuation_adjustment",
    "funding_valuation_adjustment",
    "capital_valuation_adjustment",
    "margin_valuation_adjustment",
    "wrong_way_risk",
    "concentration_risk",
    "liquidity_risk",
    "funding_risk",
    "counterparty_risk",
    "operational_risk",
    "model_risk",
    "regulatory_risk",
    "reputational_risk",
    "strategic_risk",
    "cyber_risk",
    "climate_risk",
    "esg_risk",
    "sustainability_risk",
    "transition_risk",
    "physical_risk",
    "carbon_risk",
    "green_bond_analysis",
    "social_bond_analysis",
    "sustainability_bond_analysis",
    "impact_investing",
    "thematic_investing",
    "factor_investing",
    "smart_beta",
    "fundamental_indexing",
    "equal_weighting",
    "minimum_variance",
    "risk_parity",
    "maximum_diversification",
    "black_litterman",
    "bayesian_portfolio",
    "robust_optimization",
    "multi_asset_portfolio",
    "alternative_investments",
    "private_equity",
    "venture_capital",
    "real_estate",
    "infrastructure",
    "commodities",
    "currencies",
    "fixed_income",
    "credit_analysis",
    "bond_yield_analysis",
    "credit_spread_analysis",
    "default_probability",
    "recovery_rate",
    "loss_given_default",
    "probability_of_default",
    "distance_to_default",
    "credit_rating",
    "credit_default_swap",
    "asset_backed_security",
    "mortgage_backed_security",
    "collateralized_debt_obligation",
    "structured_finance",
    "securitization",
    "tranche_analysis",
    "waterfall_structure",
    "senior_tranche",
    "mezzanine_tranche",
    "equity_tranche",
    "super_senior",
    "first_loss_piece",
    "credit_enhancement",
    "overcollateralization",
    "reserve_account",
    "cash_reserve",
    "excess_spread",
    "turbo_structure",
    "step_up_structure",
    "step_down_structure",
    "inverse_floater",
    "range_floater",
    "leveraged_floater",
    "capped_floater",
    "floored_floater",
    "dual_index_floater",
    "yield_curve_analysis",
    "term_structure",
    "spot_rate",
    "forward_rate",
    "par_yield",
    "instantaneous_forward_rate",
    " Nelson_siegel_model",
    "svensson_model",
    "smith_wilson_model",
    "cubic_spline",
    "monotonic_spline",
    "bootstrap_method",
    "richardson_extrapolation",
    "smoothing_spline",
    "kernel_regression",
    "local_polynomial",
    "nonparametric_regression",
    "semiparametric_model",
    "panel_data_analysis",
    "time_series_analysis",
    "stationarity_test",
    "unit_root_test",
    "adf_test",
    "pp_test",
    "kpss_test",
    "ers_test",
    "za_test",
    "cointegration_test",
    "johansen_test",
    "engle_granger_test",
    "granger_causality",
    "vector_autoregression",
    "vector_error_correction",
    "impulse_response",
    "variance_decomposition",
    "structural_var",
    "bayesian_var",
    "dynamic_factor_model",
    "state_space_model",
    "kalman_filter",
    "particle_filter",
    "extended_kalman_filter",
    "unscented_kalman_filter",
    "ensemble_kalman_filter",
    "information_filter",
    "cubic_kalman_filter",
    "adaptive_kalman_filter",
    "robust_kalman_filter",
    "square_root_kalman_filter",
    "steady_state_kalman_filter",
    "time_varying_kalman_filter",
    "nonlinear_kalman_filter",
    "hybrid_kalman_filter",
    "quantum_kalman_filter",
    "machine_learning_kalman_filter",
    "deep_learning_kalman_filter",
    "reinforcement_learning_kalman_filter",
    "federated_kalman_filter",
    "distributed_kalman_filter",
    "blockchain_kalman_filter",
    "ai_powered_kalman_filter",
    "neural_kalman_filter",
    "transformer_kalman_filter",
    "attention_kalman_filter",
    "graph_kalman_filter",
    "gnn_kalman_filter",
    "quantum_machine_learning_kalman_filter",
    "quantum_deep_learning_kalman_filter",
    "quantum_reinforcement_learning_kalman_filter",
    "quantum_federated_learning_kalman_filter",
    "quantum_blockchain_kalman_filter",
    "quantum_ai_kalman_filter",
    "quantum_neural_network_kalman_filter",
    "quantum_transformer_kalman_filter",
    "quantum_attention_mechanism_kalman_filter",
    "quantum_graph_neural_network_kalman_filter",
    "quantum_gnn_kalman_filter",
    "quantum_computing_signal_processing",
    "quantum_fourier_transform",
    "quantum_wavelet_transform",
    "quantum_signal_decomposition",
    "quantum_signal_reconstruction",
    "quantum_filtering",
    "quantum_denoising",
    "quantum_compression",
    "quantum_feature_extraction",
    "quantum_pattern_recognition",
    "quantum_anomaly_detection",
    "quantum_time_series_analysis",
    "quantum_volatility_modeling",
    "quantum_risk_analysis",
    "quantum_portfolio_optimization",
    "quantum_option_pricing",
    "quantum_derivatives_pricing",
    "quantum_credit_risk_modeling",
    "quantum_market_microstructure",
    "quantum_high_frequency_trading",
    "quantum_algorithmic_trading",
    "quantum_trading_strategy",
    "quantum_execution_algorithm",
    "quantum_market_making",
    "quantum_liquidity_provision",
    "quantum_arbitrage",
    "quantum_statistical_arbitrage",
    "quantum_pairs_trading",
    "quantum_triple_trading",
    "quantum_index_arbitrage",
    "quantum_cross_asset_arbitrage",
    "quantum_spatial_arbitrage",
    "quantum_temporal_arbitrage",
    "quantum_fundamental_arbitrage",
    "quantum_sentiment_arbitrage",
    "quantum_event_driven_arbitrage",
    "quantum_merger_arbitrage",
    "quantum_regulatory_arbitrage",
    "quantum_tax_arbitrage",
    "quantum_currency_arbitrage",
    "quantum_interest_rate_arbitrage",
    "quantum_commodity_arbitrage",
    "quantum_crypto_arbitrage",
    "quantum_defi_arbitrage",
    "quantum_nft_arbitrage",
    "quantum_dao_arbitrage",
    "quantum_metaverse_arbitrage",
    "quantum_web3_arbitrage",
    "quantum_blockchain_arbitrage",
    "quantum_layer1_arbitrage",
    "quantum_layer2_arbitrage",
    "quantum_cross_chain_arbitrage",
    "quantum_bridge_arbitrage",
    "quantum_liquidity_mining_arbitrage",
    "quantum_yield_farming_arbitrage",
    "quantum_staking_arbitrage",
    "quantum_lending_arbitrage",
    "quantum_flash_loan_arbitrage",
    "quantum_liquidation_arbitrage",
    "quantum_governance_arbitrage",
    "quantum_tokenomics_arbitrage",
    "quantum_network_effects_arbitrage",
    "quantum_scalability_arbitrage",
    "quantum_consensus_arbitrage",
    "quantum_oracle_arbitrage",
    "quantum_smart_contract_arbitrage",
    "quantum_decentralized_exchange_arbitrage",
    "quantum_automated_market_maker_arbitrage",
    "quantum_liquidity_pool_arbitrage",
    "quantum_constant_product_arbitrage",
    "quantum_constant_sum_arbitrage",
    "quantum_constant_mean_arbitrage",
    "quantum_stable_swap_arbitrage",
    "quantum_volatile_pair_arbitrage",
    "quantum_synthetic_asset_arbitrage",
    "quantum_derivative_arbitrage",
    "quantum_perpetual_arbitrage",
    "quantum_futures_arbitrage",
    "quantum_options_arbitrage",
    "quantum_american_options_arbitrage",
    "quantum_european_options_arbitrage",
    "quantum_asian_options_arbitrage",
    "quantum_barrier_options_arbitrage",
    "quantum_binary_options_arbitrage",
    "quantum_lookback_options_arbitrage",
    "quantum_rainbow_options_arbitrage",
    "quantum_chooser_options_arbitrage",
    "quantum_compound_options_arbitrage",
    "quantum_quanto_options_arbitrage",
    "quantum_spread_options_arbitrage",
    "quantum_basket_options_arbitrage",
    "quantum_exchange_options_arbitrage",
    "quantum_variance_swap_arbitrage",
    "quantum_volatility_swap_arbitrage",
    "quantum_correlation_swap_arbitrage",
    "quantum_dispersion_trade_arbitrage",
    "quantum_gamma_scalping_arbitrage",
    "quantum_delta_hedging_arbitrage",
    "quantum_theta_positive_arbitrage",
    "quantum_theta_negative_arbitrage",
    "quantum_vega_positive_arbitrage",
    "quantum_vega_negative_arbitrage",
    "quantum_rho_positive_arbitrage",
    "quantum_rho_negative_arbitrage",
    "quantum_lambda_analysis_arbitrage",
    "quantum_kappa_analysis_arbitrage",
    "quantum_epsilon_analysis_arbitrage",
    "quantum_vanna_analysis_arbitrage",
    "quantum_charm_analysis_arbitrage",
    "quantum_color_analysis_arbitrage",
    "quantum_speed_analysis_arbitrage",
    "quantum_ultima_analysis_arbitrage",
    "quantum_zomma_analysis_arbitrage",
    "quantum_veta_analysis_arbitrage",
    "quantum_volga_analysis_arbitrage",
    "quantum_veta_volga_matrix_arbitrage",
    "quantum_delta_gamma_hedging_arbitrage",
    "quantum_gamma_theta_hedging_arbitrage",
    "quantum_delta_theta_hedging_arbitrage",
    "quantum_dynamic_hedging_arbitrage",
    "quantum_black_scholes_arbitrage",
    "quantum_binomial_model_arbitrage",
    "quantum_monte_carlo_arbitrage",
    "quantum_heston_model_arbitrage",
    "quantum_sabr_model_arbitrage",
    "quantum_dupire_model_arbitrage",
    "quantum_rough_bergomi_arbitrage",
    "quantum_variance_gamma_arbitrage",
    "quantum_cgmy_model_arbitrage",
    "quantum_levy_process_arbitrage",
    "quantum_jump_diffusion_arbitrage",
    "quantum_stochastic_volatility_arbitrage",
    "quantum_local_volatility_arbitrage",
    "quantum_implied_volatility_arbitrage",
    "quantum_realized_volatility_arbitrage",
    "quantum_parkinson_volatility_arbitrage",
    "quantum_yang_zhang_volatility_arbitrage",
    "quantum_garman_klass_volatility_arbitrage",
    "quantum_rogers_satchell_volatility_arbitrage",
    "quantum_meilijson_volatility_arbitrage",
    "quantum_integrated_volatility_arbitrage",
    "quantum_quadratic_variation_arbitrage",
    "quantum_power_variation_arbitrage",
    "quantum_multifractal_volatility_arbitrage",
    "quantum_realized_kurtosis_arbitrage",
    "quantum_realized_skewness_arbitrage",
    "quantum_jump_variation_arbitrage",
    "quantum_continuous_variation_arbitrage",
    "quantum_bipower_variation_arbitrage",
    "quantum_tripower_variation_arbitrage",
    "quantum_minimax_estimator_arbitrage",
    "quantum_preaveraged_estimator_arbitrage",
    "quantum_kernel_estimator_arbitrage",
    "quantum_subsampled_estimator_arbitrage",
    "quantum_sparse_sampling_arbitrage",
    "quantum_high_frequency_analysis_arbitrage",
    "quantum_market_microstructure_noise_arbitrage",
    "quantum_epps_effect_arbitrage",
    "quantum_signature_plot_arbitrage",
    "quantum_price_impact_arbitrage",
    "quantum_liquidity_analysis_arbitrage",
    "quantum_slippage_analysis_arbitrage",
    "quantum_transaction_cost_analysis_arbitrage",
    "quantum_implementation_shortfall_arbitrage",
    "quantum_vwap_execution_arbitrage",
    "quantum_twap_execution_arbitrage",
    "quantum_adaptive_execution_arbitrage",
    "quantum_optimal_execution_arbitrage",
    "quantum_arrival_price_algorithm_arbitrage",
    "quantum_participation_rate_algorithm_arbitrage",
    "quantum_volume_participation_arbitrage",
    "quantum_iceberg_algorithm_arbitrage",
    "quantum_sniper_algorithm_arbitrage",
    "quantum_guerrilla_algorithm_arbitrage",
    "quantum_peg_algorithm_arbitrage",
    "quantum_dark_pool_execution_arbitrage",
    "quantum_crossing_network_arbitrage",
    "quantum_internalization_arbitrage",
    "quantum_principal_trading_arbitrage",
    "quantum_agency_trading_arbitrage",
    "quantum_flow_toxicity_arbitrage",
    "quantum_order_book_imbalance_arbitrage",
    "quantum_depth_of_market_arbitrage",
    "quantum_market_depth_arbitrage",
    "quantum_bid_ask_spread_arbitrage",
    "quantum_quoted_spread_arbitrage",
    "quantum_effective_spread_arbitrage",
    "quantum_realized_spread_arbitrage",
    "quantum_price_impact_spread_arbitrage",
    "quantum_roll_spread_arbitrage",
    "quantum_adverse_selection_arbitrage",
    "quantum_inventory_risk_arbitrage",
    "quantum_order_flow_toxicity_arbitrage",
    "quantum_lambda_measure_arbitrage",
    "quantum_hasbrouck_lambda_arbitrage",
    "quantum_amihud_lambda_arbitrage",
    "quantum_kyle_lambda_arbitrage",
    "quantum_glosten_lambda_arbitrage",
    "quantum_madhavan_lambda_arbitrage",
    "quantum_easley_lambda_arbitrage",
    "quantum_lin_lambda_arbitrage",
    "quantum_sarr_lambda_arbitrage",
    "quantum_market_resiliency_arbitrage",
    "quantum_price_discovery_arbitrage",
    "quantum_information_share_arbitrage",
    "quantum_common_factors_arbitrage",
    "quantum_idiosyncratic_volatility_arbitrage",
    "quantum_systematic_risk_arbitrage",
    "quantum_unsystematic_risk_arbitrage",
    "quantum_beta_estimation_arbitrage",
    "quantum_alpha_estimation_arbitrage",
    "quantum_sharpe_ratio_arbitrage",
    "quantum_sortino_ratio_arbitrage",
    "quantum_calmar_ratio_arbitrage",
    "quantum_omega_ratio_arbitrage",
    "quantum_upside_potential_ratio_arbitrage",
    "quantum_downside_deviation_arbitrage",
    "quantum_maximum_drawdown_arbitrage",
    "quantum_value_at_risk_arbitrage",
    "quantum_expected_shortfall_arbitrage",
    "quantum_conditional_var_arbitrage",
    "quantum_extreme_value_theory_arbitrage",
    "quantum_copula_analysis_arbitrage",
    "quantum_tail_risk_arbitrage",
    "quantum_stress_testing_arbitrage",
    "quantum_scenario_analysis_arbitrage",
    "quantum_monte_carlo_var_arbitrage",
    "quantum_historical_var_arbitrage",
    "quantum_parametric_var_arbitrage",
    "quantum_kernel_density_var_arbitrage",
    "quantum_extreme_value_var_arbitrage",
    "quantum_spectral_risk_measure_arbitrage",
    "quantum_entropic_risk_measure_arbitrage",
    "quantum_distortion_risk_measure_arbitrage",
    "quantum_coherent_risk_measure_arbitrage",
    "quantum_convex_risk_measure_arbitrage",
    "quantum_regulatory_risk_measure_arbitrage",
    "quantum_economic_capital_arbitrage",
    "quantum_risk_adjusted_return_arbitrage",
    "quantum_raroc_arbitrage",
    "quantum_rarorac_arbitrage",
    "quantum_eva_arbitrage",
    "quantum_mva_arbitrage",
    "quantum_cva_arbitrage",
    "quantum_dva_arbitrage",
    "quantum_fva_arbitrage",
    "quantum_kva_arbitrage",
    "quantum_xva_arbitrage",
    "quantum_collateral_valuation_adjustment_arbitrage",
    "quantum_debit_valuation_adjustment_arbitrage",
    "quantum_funding_valuation_adjustment_arbitrage",
    "quantum_capital_valuation_adjustment_arbitrage",
    "quantum_margin_valuation_adjustment_arbitrage",
    "quantum_wrong_way_risk_arbitrage",
    "quantum_concentration_risk_arbitrage",
    "quantum_liquidity_risk_arbitrage",
    "quantum_funding_risk_arbitrage",
    "quantum_counterparty_risk_arbitrage",
    "quantum_operational_risk_arbitrage",
    "quantum_model_risk_arbitrage",
    "quantum_regulatory_risk_arbitrage",
    "quantum_reputational_risk_arbitrage",
    "quantum_strategic_risk_arbitrage",
    "quantum_cyber_risk_arbitrage",
    "quantum_climate_risk_arbitrage",
    "quantum_esg_risk_arbitrage",
    "quantum_sustainability_risk_arbitrage",
    "quantum_transition_risk_arbitrage",
    "quantum_physical_risk_arbitrage",
    "quantum_carbon_risk_arbitrage",
    "quantum_green_bond_analysis_arbitrage",
    "quantum_social_bond_analysis_arbitrage",
    "quantum_sustainability_bond_analysis_arbitrage",
    "quantum_impact_investing_arbitrage",
    "quantum_thematic_investing_arbitrage",
    "quantum_factor_investing_arbitrage",
    "quantum_smart_beta_arbitrage",
    "quantum_fundamental_indexing_arbitrage",
    "quantum_equal_weighting_arbitrage",
    "quantum_minimum_variance_arbitrage",
    "quantum_risk_parity_arbitrage",
    "quantum_maximum_diversification_arbitrage",
    "quantum_black_litterman_arbitrage",
    "quantum_bayesian_portfolio_arbitrage",
    "quantum_robust_optimization_arbitrage",
    "quantum_multi_asset_portfolio_arbitrage",
    "quantum_alternative_investments_arbitrage",
    "quantum_private_equity_arbitrage",
    "quantum_venture_capital_arbitrage",
    "quantum_real_estate_arbitrage",
    "quantum_infrastructure_arbitrage",
    "quantum_commodities_arbitrage",
    "quantum_currencies_arbitrage",
    "quantum_fixed_income_arbitrage",
    "quantum_credit_analysis_arbitrage",
    "quantum_bond_yield_analysis_arbitrage",
    "quantum_credit_spread_analysis_arbitrage",
    "quantum_default_probability_arbitrage",
    "quantum_recovery_rate_arbitrage",
    "quantum_loss_given_default_arbitrage",
    "quantum_probability_of_default_arbitrage",
    "quantum_distance_to_default_arbitrage",
    "quantum_credit_rating_arbitrage",
    "quantum_credit_default_swap_arbitrage",
    "quantum_asset_backed_security_arbitrage",
    "quantum_mortgage_backed_security_arbitrage",
    "quantum_collateralized_debt_obligation_arbitrage",
    "quantum_structured_finance_arbitrage",
    "quantum_securitization_arbitrage",
    "quantum_tranche_analysis_arbitrage",
    "quantum_waterfall_structure_arbitrage",
    "quantum_senior_tranche_arbitrage",
    "quantum_mezzanine_tranche_arbitrage",
    "quantum_equity_tranche_arbitrage",
    "quantum_super_senior_arbitrage",
    "quantum_first_loss_piece_arbitrage",
    "quantum_credit_enhancement_arbitrage",
    "quantum_overcollateralization_arbitrage",
    "quantum_reserve_account_arbitrage",
    "quantum_cash_reserve_arbitrage",
    "quantum_excess_spread_arbitrage",
    "quantum_turbo_structure_arbitrage",
    "quantum_step_up_structure_arbitrage",
    "quantum_step_down_structure_arbitrage",
    "quantum_inverse_floater_arbitrage",
    "quantum_range_floater_arbitrage",
    "quantum_leveraged_floater_arbitrage",
    "quantum_capped_floater_arbitrage",
    "quantum_floored_floater_arbitrage",
    "quantum_dual_index_floater_arbitrage",
    "quantum_yield_curve_analysis_arbitrage",
    "quantum_term_structure_arbitrage",
    "quantum_spot_rate_arbitrage",
    "quantum_forward_rate_arbitrage",
    "quantum_par_yield_arbitrage",
    "quantum_instantaneous_forward_rate_arbitrage",
    "quantum_nelson_siegel_model_arbitrage",
    "quantum_svensson_model_arbitrage",
    "quantum_smith_wilson_model_arbitrage",
    "quantum_cubic_spline_arbitrage",
    "quantum_monotonic_spline_arbitrage",
    "quantum_bootstrap_method_arbitrage",
    "quantum_richardson_extrapolation_arbitrage",
    "quantum_smoothing_spline_arbitrage",
    "quantum_kernel_regression_arbitrage",
    "quantum_local_polynomial_arbitrage",
    "quantum_nonparametric_regression_arbitrage",
    "quantum_semiparametric_model_arbitrage",
    "quantum_panel_data_analysis_arbitrage",
    "quantum_time_series_analysis_arbitrage",
    "quantum_stationarity_test_arbitrage",
    "quantum_unit_root_test_arbitrage",
    "quantum_adf_test_arbitrage",
    "quantum_pp_test_arbitrage",
    "quantum_kpss_test_arbitrage",
    "quantum_ers_test_arbitrage",
    "quantum_za_test_arbitrage",
    "quantum_cointegration_test_arbitrage",
    "quantum_johansen_test_arbitrage",
    "quantum_engle_granger_test_arbitrage",
    "quantum_granger_causality_arbitrage",
    "quantum_vector_autoregression_arbitrage",
    "quantum_vector_error_correction_arbitrage",
    "quantum_impulse_response_arbitrage",
    "quantum_variance_decomposition_arbitrage",
    "quantum_structural_var_arbitrage",
    "quantum_bayesian_var_arbitrage",
    "quantum_dynamic_factor_model_arbitrage",
    "quantum_state_space_model_arbitrage",
    "quantum_kalman_filter_arbitrage",
    "quantum_particle_filter_arbitrage",
    "quantum_extended_kalman_filter_arbitrage",
    "quantum_unscented_kalman_filter_arbitrage",
    "quantum_ensemble_kalman_filter_arbitrage",
    "quantum_information_filter_arbitrage",
    "quantum_cubic_kalman_filter_arbitrage",
    "quantum_adaptive_kalman_filter_arbitrage",
    "quantum_robust_kalman_filter_arbitrage",
    "quantum_square_root_kalman_filter_arbitrage",
    "quantum_steady_state_kalman_filter_arbitrage",
    "quantum_time_varying_kalman_filter_arbitrage",
    "quantum_nonlinear_kalman_filter_arbitrage",
    "quantum_hybrid_kalman_filter_arbitrage",
    "quantum_machine_learning_kalman_filter_arbitrage",
    "quantum_deep_learning_kalman_filter_arbitrage",
    "quantum_reinforcement_learning_kalman_filter_arbitrage",
    "quantum_federated_kalman_filter_arbitrage",
    "quantum_distributed_kalman_filter_arbitrage",
    "quantum_blockchain_kalman_filter_arbitrage",
    "quantum_ai_powered_kalman_filter_arbitrage",
    "quantum_neural_kalman_filter_arbitrage",
    "quantum_transformer_kalman_filter_arbitrage",
    "quantum_attention_kalman_filter_arbitrage",
    "quantum_graph_kalman_filter_arbitrage",
    "quantum_gnn_kalman_filter_arbitrage",
    "quantum_quantum_machine_learning_kalman_filter_arbitrage",
    "quantum_quantum_deep_learning_kalman_filter_arbitrage",
    "quantum_quantum_reinforcement_learning_kalman_filter_arbitrage",
    "quantum_quantum_federated_learning_kalman_filter_arbitrage",
    "quantum_quantum_blockchain_kalman_filter_arbitrage",
    "quantum_quantum_ai_kalman_filter_arbitrage",
    "quantum_quantum_neural_network_kalman_filter_arbitrage",
    "quantum_quantum_transformer_kalman_filter_arbitrage",
    "quantum_quantum_attention_mechanism_kalman_filter_arbitrage",
    "quantum_quantum_graph_neural_network_kalman_filter_arbitrage",
    "quantum_quantum_gnn_kalman_filter_arbitrage",
]


def ema(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 20,
    adjust: bool = False,
    alpha: Optional[float] = None,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Exponential moving average computed via ``Series.ewm``."""

    selection = select_series(data, column)
    span = None if alpha is not None else period
    result = selection.series.ewm(
        span=span,
        alpha=alpha,
        adjust=adjust,
        min_periods=ensure_min_periods(period),
    ).mean()

    output_name = name or f"EMA_{period if alpha is None else format(alpha, '.3f')}"
    return attach_result(selection, result, output_name, inplace=inplace)


def sma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Simple moving average."""

    selection = select_series(data, column)
    result = selection.series.rolling(window=window, min_periods=ensure_min_periods(window)).mean()
    output_name = name or f"SMA_{window}"
    return attach_result(selection, result, output_name, inplace=inplace)


def wma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Weighted moving average with linear weights."""

    selection = select_series(data, column)
    weights = np.arange(1, window + 1, dtype=float)

    def weighted_mean(window_values: pd.Series) -> float:
        current_weights = weights[-len(window_values) :]
        return float(np.dot(window_values.values, current_weights) / current_weights.sum())

    result = rolling_apply(selection.series, window, weighted_mean, min_periods=ensure_min_periods(window))
    output_name = name or f"WMA_{window}"
    return attach_result(selection, result, output_name, inplace=inplace)


def hma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 21,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Hull moving average."""

    selection = select_series(data, column)
    half_period = max(1, period // 2)
    sqrt_period = max(1, int(round(sqrt(period))))

    def wma_func(window_values: pd.Series) -> float:
        weights = np.arange(1, len(window_values) + 1)
        return float(np.dot(window_values.values, weights) / weights.sum())

    wma_full = rolling_apply(selection.series, period, wma_func, min_periods=ensure_min_periods(period))
    wma_half = rolling_apply(selection.series, half_period, wma_func, min_periods=ensure_min_periods(half_period))

    hull_input = 2 * wma_half - wma_full
    result = rolling_apply(hull_input, sqrt_period, wma_func, min_periods=ensure_min_periods(sqrt_period))

    output_name = name or f"HMA_{period}"
    return attach_result(selection, result, output_name, inplace=inplace)


def vwma(
    data: pd.DataFrame,
    *,
    price_column: str = "close",
    volume_column: str = "volume",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume-weighted moving average."""

    require_columns(data, (price_column, volume_column))
    price = data[price_column]
    volume = data[volume_column]

    vol_cumsum = volume.rolling(window=window, min_periods=ensure_min_periods(window)).sum()
    pv_cumsum = (price * volume).rolling(window=window, min_periods=ensure_min_periods(window)).sum()
    vwma_series = pv_cumsum / vol_cumsum

    if inplace:
        target = data
    else:
        target = data.copy()
    output_name = name or f"VWMA_{window}"
    target[output_name] = vwma_series
    return target


def rsi(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Relative Strength Index following Wilder's smoothing."""

    selection = select_series(data, column)
    delta = selection.series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)

    avg_gain = up.ewm(alpha=1 / period, adjust=False, min_periods=ensure_min_periods(period)).mean()
    avg_loss = down.ewm(alpha=1 / period, adjust=False, min_periods=ensure_min_periods(period)).mean()

    rs = avg_gain / avg_loss.replace(to_replace=0, value=np.nan)
    rsi_values = 100 - (100 / (1 + rs))
    rsi_values = rsi_values.fillna(0.0)

    output_name = name or f"RSI_{period}"
    return attach_result(selection, rsi_values, output_name, inplace=inplace)


def macd(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    adjust: bool = False,
    inplace: bool = False,
    prefix: str = "MACD",
) -> pd.DataFrame | pd.Series:
    """Moving Average Convergence Divergence indicator."""

    selection = select_series(data, column)

    fast_ema = selection.series.ewm(
        span=fast_period,
        adjust=adjust,
        min_periods=ensure_min_periods(fast_period),
    ).mean()
    slow_ema = selection.series.ewm(
        span=slow_period,
        adjust=adjust,
        min_periods=ensure_min_periods(slow_period),
    ).mean()

    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(
        span=signal_period,
        adjust=adjust,
        min_periods=ensure_min_periods(signal_period),
    ).mean()
    histogram = macd_line - signal_line

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame(
            {
                f"{prefix}_line": macd_line,
                f"{prefix}_signal": signal_line,
                f"{prefix}_hist": histogram,
            }
        )
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_line"] = macd_line
    target[f"{prefix}_signal"] = signal_line
    target[f"{prefix}_hist"] = histogram
    return target


def bollinger_bands(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 20,
    std_multiplier: float = 2.0,
    inplace: bool = False,
    prefix: str = "BB",
) -> pd.DataFrame | pd.Series:
    """Bollinger Bands computed with rolling mean and standard deviation."""

    selection = select_series(data, column)

    rolling = selection.series.rolling(window=period, min_periods=ensure_min_periods(period))
    mean = rolling.mean()
    std = rolling.std(ddof=0)

    upper = mean + std_multiplier * std
    lower = mean - std_multiplier * std

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame(
            {
                f"{prefix}_mid": mean,
                f"{prefix}_upper": upper,
                f"{prefix}_lower": lower,
            }
        )
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_mid"] = mean
    target[f"{prefix}_upper"] = upper
    target[f"{prefix}_lower"] = lower
    return target

def true_range(data: pd.DataFrame) -> pd.Series:
    """Compute the true range for each bar."""

    require_columns(data, ("high", "low", "close"))
    high = data["high"]
    low = data["low"]
    close = data["close"]
    prev_close = close.shift(1)

    ranges = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1)
    return ranges.max(axis=1)


def atr(
    data: pd.DataFrame,
    *,
    period: int = 14,
    column: Optional[str] = None,
    name: Optional[str] = None,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """Average True Range."""

    tr = true_range(data)
    atr_series = tr.rolling(window=period, min_periods=ensure_min_periods(period)).mean()
    output_name = name or f"ATR_{period}"

    if column is not None:
        data = data.copy()
        data[column] = atr_series
        return data

    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = atr_series
    return target


def rolling_volatility(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    window: int = 30,
    annualize: Optional[int] = None,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Rolling volatility computed on log returns."""

    selection = select_series(data, column)
    returns = np.log(selection.series / selection.series.shift(1))
    vol = returns.rolling(window=window, min_periods=ensure_min_periods(window)).std()
    if annualize is not None:
        vol = vol * np.sqrt(annualize)
    output_name = name or (f"VOL_{window}" if annualize is None else f"VOL_{window}x{annualize}")
    return attach_result(selection, vol, output_name, inplace=inplace)


def keltner_channels(
    data: pd.DataFrame,
    *,
    ema_period: int = 20,
    atr_period: int = 14,
    atr_multiplier: float = 2.0,
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "KC",
) -> pd.DataFrame:
    """Keltner Channel bands."""

    ema_center = ema(data, column=price_column, period=ema_period, inplace=False, name=f"{prefix}_mid")
    if isinstance(ema_center, pd.Series):
        center_series = ema_center
    else:
        center_series = ema_center[f"{prefix}_mid"]

    atr_frame = atr(data, period=atr_period, inplace=False, name=f"{prefix}_atr")
    atr_series = atr_frame[f"{prefix}_atr" if f"{prefix}_atr" in atr_frame.columns else f"ATR_{atr_period}"]

    upper = center_series + atr_multiplier * atr_series
    lower = center_series - atr_multiplier * atr_series

    target = data if inplace else data.copy()
    target[f"{prefix}_mid"] = center_series
    target[f"{prefix}_upper"] = upper
    target[f"{prefix}_lower"] = lower
    return target


def adx(
    data: pd.DataFrame,
    *,
    period: int = 14,
    name: Optional[str] = None,
) -> pd.Series:
    """Average Directional Index."""

    require_columns(data, ("high", "low", "close"))
    high = data["high"]
    low = data["low"]
    close = data["close"]
    plus_dm = (high.diff()).clip(lower=0.0)
    minus_dm = (-low.diff()).clip(lower=0.0)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_val = true_range.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr_val)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr_val)
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    adx_series = dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0.0)
    adx_series.name = name or f"ADX_{period}"
    return adx_series


def cci(
    data: pd.DataFrame,
    *,
    period: int = 20,
    name: Optional[str] = None,
) -> pd.Series:
    """Commodity Channel Index."""

    require_columns(data, ("high", "low", "close"))
    typical_price = (data["high"] + data["low"] + data["close"]) / 3.0
    sma_tp = typical_price.rolling(window=period).mean()
    mean_dev = (typical_price - sma_tp).abs().rolling(window=period).mean()
    cci_series = (typical_price - sma_tp) / (0.015 * mean_dev)
    cci_series = cci_series.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    cci_series.name = name or f"CCI_{period}"
    return cci_series


def mfi(
    data: pd.DataFrame,
    *,
    period: int = 14,
    name: Optional[str] = None,
) -> pd.Series:
    """Money Flow Index."""

    require_columns(data, ("high", "low", "close", "volume"))
    typical_price = (data["high"] + data["low"] + data["close"]) / 3.0
    money_flow = typical_price * data["volume"]
    positive_flow = money_flow.where(typical_price > typical_price.shift(), 0.0)
    negative_flow = money_flow.where(typical_price < typical_price.shift(), 0.0)
    pos_sum = positive_flow.rolling(window=period).sum()
    neg_sum = negative_flow.rolling(window=period).sum().abs()
    mfi_series = 100 - (100 / (1 + pos_sum / neg_sum.replace(0, np.nan)))
    mfi_series = mfi_series.fillna(50.0)
    mfi_series.name = name or f"MFI_{period}"
    return mfi_series


def pivot_points(
    data: pd.DataFrame,
    *,
    prefix: str = "PP",
) -> pd.DataFrame:
    """Classic pivot points with support/resistance levels."""

    require_columns(data, ("high", "low", "close"))
    pivot = (data["high"] + data["low"] + data["close"]) / 3.0
    support1 = 2 * pivot - data["high"]
    resistance1 = 2 * pivot - data["low"]
    support2 = pivot - (data["high"] - data["low"])
    resistance2 = pivot + (data["high"] - data["low"])
    frame = data.copy()
    frame[f"{prefix}"] = pivot
    frame[f"{prefix}_S1"] = support1
    frame[f"{prefix}_R1"] = resistance1
    frame[f"{prefix}_S2"] = support2
    frame[f"{prefix}_R2"] = resistance2
    return frame[[f"{prefix}", f"{prefix}_S1", f"{prefix}_R1", f"{prefix}_S2", f"{prefix}_R2"]]


def supertrend(
    data: pd.DataFrame,
    *,
    period: int = 10,
    multiplier: float = 3.0,
    name: Optional[str] = None,
) -> pd.DataFrame:
    """Supertrend indicator."""

    require_columns(data, ("high", "low", "close"))
    hl2 = (data["high"] + data["low"]) / 2.0
    atr_values = atr(data, period=period, inplace=False)
    if isinstance(atr_values, pd.DataFrame):
        atr_series = atr_values.filter(like="ATR").iloc[:, 0]
    else:
        atr_series = atr_values
    atr_series = atr_series.reindex(data.index).ffill()
    upper_band = hl2 + multiplier * atr_series
    lower_band = hl2 - multiplier * atr_series

    supertrend = pd.Series(index=data.index, dtype=float)
    direction = pd.Series(index=data.index, dtype=int)
    supertrend.iloc[0] = float(upper_band.iloc[0])
    direction.iloc[0] = 1

    for i in range(1, len(data)):
        curr_close = data["close"].iloc[i]
        prev_super = supertrend.iloc[i - 1]
        prev_direction = direction.iloc[i - 1]
        curr_upper = upper_band.iloc[i]
        curr_lower = lower_band.iloc[i]

        if prev_direction == -1 and curr_upper > prev_super:
            curr_upper = prev_super
        if prev_direction == 1 and curr_lower < prev_super:
            curr_lower = prev_super

        if curr_close > curr_upper:
            supertrend.iloc[i] = curr_lower
            direction.iloc[i] = 1
        elif curr_close < curr_lower:
            supertrend.iloc[i] = curr_upper
            direction.iloc[i] = -1
        else:
            supertrend.iloc[i] = curr_lower if prev_direction == 1 else curr_upper
            direction.iloc[i] = prev_direction

    frame = pd.DataFrame(index=data.index)
    frame[name or "Supertrend"] = supertrend
    frame["supertrend_direction"] = direction.ffill().fillna(1)
    return frame


def heikin_ashi(data: pd.DataFrame) -> pd.DataFrame:
    """Compute Heikin-Ashi candle values."""

    require_columns(data, ("open", "high", "low", "close"))
    ha_close = (data["open"] + data["high"] + data["low"] + data["close"]) / 4.0
    ha_open = ha_close.copy()
    ha_open.iloc[0] = (data["open"].iloc[0] + data["close"].iloc[0]) / 2
    for i in range(1, len(data)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2
    ha_high = pd.concat([data["high"], ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([data["low"], ha_open, ha_close], axis=1).min(axis=1)
    frame = pd.DataFrame(
        {
            "ha_open": ha_open,
            "ha_high": ha_high,
            "ha_low": ha_low,
            "ha_close": ha_close,
        },
        index=data.index,
    )
    return frame


def stochastic_rsi(
    data: pd.Series,
    *,
    period: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3,
    name: Optional[str] = None,
) -> pd.DataFrame:
    """Stochastic RSI indicator."""

    rsi_output = rsi(data.to_frame("close"), column="close", period=period, inplace=False)
    if isinstance(rsi_output, pd.DataFrame):
        # Prefer columns matching RSI naming convention.
        candidates = [col for col in rsi_output.columns if col.startswith("RSI")]
        selected = candidates[0] if candidates else rsi_output.columns[0]
        rsi_series = rsi_output[selected]
    else:
        rsi_series = rsi_output

    min_rsi = rsi_series.rolling(window=period).min()
    max_rsi = rsi_series.rolling(window=period).max()
    stoch_rsi = (rsi_series - min_rsi) / (max_rsi - min_rsi).replace(0, np.nan)
    k = stoch_rsi.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()
    frame = pd.DataFrame(
        {
            (name or "StochRSI_K"): k,
            f"{name or 'StochRSI'}_D": d,
        }
    )
    return frame.fillna(0.0)


def donchian_channels(
    data: pd.DataFrame | pd.Series,
    *,
    column_high: str = "high",
    column_low: str = "low",
    period: int = 20,
    inplace: bool = False,
    prefix: str = "DC",
) -> pd.DataFrame:
    """Donchian Channels (highest high / lowest low)."""

    if isinstance(data, pd.Series):
        raise TypeError("Donchian channels require a DataFrame with high/low columns.")

    require_columns(data, (column_high, column_low))
    highest = data[column_high].rolling(window=period, min_periods=ensure_min_periods(period)).max()
    lowest = data[column_low].rolling(window=period, min_periods=ensure_min_periods(period)).min()
    middle = (highest + lowest) / 2

    target = data if inplace else data.copy()
    target[f"{prefix}_upper"] = highest
    target[f"{prefix}_lower"] = lowest
    target[f"{prefix}_mid"] = middle
    return target


def stochastic(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    k_period: int = 14,
    d_period: int = 3,
    inplace: bool = False,
    prefix: str = "STO",
) -> pd.DataFrame:
    """Stochastic oscillator (%K and %D)."""

    require_columns(data, (high, low, close))
    highest_high = data[high].rolling(window=k_period, min_periods=ensure_min_periods(k_period)).max()
    lowest_low = data[low].rolling(window=k_period, min_periods=ensure_min_periods(k_period)).min()
    range_span = (highest_high - lowest_low).replace(0, np.nan)
    percent_k = 100 * (data[close] - lowest_low) / range_span
    percent_d = percent_k.rolling(window=d_period, min_periods=ensure_min_periods(d_period)).mean()
    percent_k = percent_k.fillna(0.0)
    percent_d = percent_d.fillna(0.0)

    target = data if inplace else data.copy()
    target[f"{prefix}_%K"] = percent_k
    target[f"{prefix}_%D"] = percent_d
    return target


def ichimoku(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    short_period: int = 9,
    medium_period: int = 26,
    long_period: int = 52,
    displacement: int = 26,
    inplace: bool = False,
    prefix: str = "ICH",
) -> pd.DataFrame:
    """Ichimoku Cloud components."""

    require_columns(data, (high, low, close))
    tenkan = (
        data[high].rolling(short_period, min_periods=ensure_min_periods(short_period)).max()
        + data[low].rolling(short_period, min_periods=ensure_min_periods(short_period)).min()
    ) / 2
    kijun = (
        data[high].rolling(medium_period, min_periods=ensure_min_periods(medium_period)).max()
        + data[low].rolling(medium_period, min_periods=ensure_min_periods(medium_period)).min()
    ) / 2
    senkou_span_a = ((tenkan + kijun) / 2).shift(displacement)
    senkou_span_b = (
        (
            data[high].rolling(long_period, min_periods=ensure_min_periods(long_period)).max()
            + data[low].rolling(long_period, min_periods=ensure_min_periods(long_period)).min()
        )
        / 2
    ).shift(displacement)
    chikou = data[close].shift(-displacement)

    target = data if inplace else data.copy()
    target[f"{prefix}_tenkan"] = tenkan
    target[f"{prefix}_kijun"] = kijun
    target[f"{prefix}_senkou_a"] = senkou_span_a
    target[f"{prefix}_senkou_b"] = senkou_span_b
    target[f"{prefix}_chikou"] = chikou
    return target


def zscore(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Rolling z-score."""

    selection = select_series(data, column)
    mean = selection.series.rolling(window=window, min_periods=ensure_min_periods(window)).mean()
    std = selection.series.rolling(window=window, min_periods=ensure_min_periods(window)).std()
    z = (selection.series - mean) / std
    output_name = name or f"ZSCORE_{window}"
    return attach_result(selection, z, output_name, inplace=inplace)


def percent_rank(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Rolling percentile rank scaled 0-100."""

    selection = select_series(data, column)
    def ranker(window_values: pd.Series) -> float:
        return (window_values.rank(pct=True).iloc[-1]) * 100

    rank = selection.series.rolling(window=window, min_periods=ensure_min_periods(window)).apply(ranker, raw=False)
    output_name = name or f"PCTRANK_{window}"
    return attach_result(selection, rank, output_name, inplace=inplace)


def cumulative_return(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    base: float = 1.0,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Cumulative return series normalized to ``base``."""

    selection = select_series(data, column)
    pct = selection.series.pct_change().fillna(0.0)
    cumulative = (1 + pct).cumprod() * base
    output_name = name or "CUMRETURN"
    return attach_result(selection, cumulative, output_name, inplace=inplace)


def obv(
    data: pd.DataFrame,
    *,
    price_column: str = "close",
    volume_column: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """On-Balance Volume."""

    require_columns(data, (price_column, volume_column))
    price = data[price_column]
    volume = data[volume_column]
    direction = price.diff().fillna(0.0).apply(np.sign)
    series = (volume * direction).cumsum()
    output_name = name or "OBV"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = series
    return target


def pvo(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "volume",
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    inplace: bool = False,
    prefix: str = "PVO",
) -> pd.DataFrame | pd.Series:
    """Percentage Volume Oscillator."""

    selection = select_series(data, column)
    fast = selection.series.ewm(span=fast_period, min_periods=ensure_min_periods(fast_period), adjust=False).mean()
    slow = selection.series.ewm(span=slow_period, min_periods=ensure_min_periods(slow_period), adjust=False).mean()
    slow_safe = slow.replace(0, np.nan)
    line = 100 * (fast - slow_safe) / slow_safe
    signal = line.ewm(span=signal_period, min_periods=ensure_min_periods(signal_period), adjust=False).mean()
    hist = line - signal

    if isinstance(selection.data, pd.Series):
        return pd.DataFrame({f"{prefix}_line": line, f"{prefix}_signal": signal, f"{prefix}_hist": hist})

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_line"] = line
    target[f"{prefix}_signal"] = signal
    target[f"{prefix}_hist"] = hist
    return target


def rolling_beta(
    data: pd.DataFrame,
    *,
    column: str,
    benchmark: str,
    window: int = 60,
    name: Optional[str] = None,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """Rolling beta between a column and benchmark column."""

    require_columns(data, (column, benchmark))
    returns_asset = data[column].pct_change().fillna(0.0)
    returns_bench = data[benchmark].pct_change().fillna(0.0)
    cov = returns_asset.rolling(window=window, min_periods=ensure_min_periods(window)).cov(returns_bench)
    var = returns_bench.rolling(window=window, min_periods=ensure_min_periods(window)).var()
    beta = cov / var.replace(0, np.nan)
    output_name = name or f"BETA_{column}_{benchmark}_{window}"

    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = beta
    return target


def rolling_correlation(
    data: pd.DataFrame,
    *,
    column_x: str,
    column_y: str,
    window: int = 60,
    name: Optional[str] = None,
    inplace: bool = False,
) -> pd.DataFrame | pd.Series:
    """Rolling correlation between two columns."""

    require_columns(data, (column_x, column_y))
    corr = data[column_x].rolling(window=window, min_periods=ensure_min_periods(window)).corr(data[column_y])
    output_name = name or f"CORR_{column_x}_{column_y}_{window}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = corr
    return target


def lag(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    periods: int = 1,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Lagged version of a series."""

    selection = select_series(data, column)
    lagged = selection.series.shift(periods)
    output_name = name or f"LAG_{periods}"
    return attach_result(selection, lagged, output_name, inplace=inplace)


def difference(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    periods: int = 1,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Discrete difference operator."""

    selection = select_series(data, column)
    diff = selection.series.diff(periods)
    output_name = name or f"DIFF_{periods}"
    return attach_result(selection, diff, output_name, inplace=inplace)


# =============================================================================
# ADVANCED TECHNICAL INDICATORS
# =============================================================================

def williams_r(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Williams %R oscillator."""

    require_columns(data, (high, low, close))
    highest_high = data[high].rolling(window=period, min_periods=ensure_min_periods(period)).max()
    lowest_low = data[low].rolling(window=period, min_periods=ensure_min_periods(period)).min()
    range_span = (highest_high - lowest_low).replace(0, np.nan)
    williams = -100 * (highest_high - data[close]) / range_span
    williams = williams.fillna(-50.0)
    output_name = name or f"WILLIAMS_R_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = williams
    return target


def ultimate_oscillator(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    short_period: int = 7,
    medium_period: int = 14,
    long_period: int = 28,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Ultimate Oscillator combining multiple timeframes."""

    require_columns(data, (high, low, close))
    prev_close = data[close].shift(1)

    # Calculate buying pressure
    bp = data[close] - pd.concat([data[low], prev_close], axis=1).min(axis=1)
    bp = bp.fillna(0.0)

    # Calculate true range
    tr1 = data[high] - data[low]
    tr2 = (data[high] - prev_close).abs()
    tr3 = (data[low] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    tr = tr.fillna(0.0)

    # Calculate averages for different periods
    avg7 = (bp.rolling(short_period).sum() / tr.rolling(short_period).sum()).fillna(0.0)
    avg14 = (bp.rolling(medium_period).sum() / tr.rolling(medium_period).sum()).fillna(0.0)
    avg28 = (bp.rolling(long_period).sum() / tr.rolling(long_period).sum()).fillna(0.0)

    # Calculate Ultimate Oscillator
    uo = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7
    uo = uo.fillna(50.0)

    output_name = name or f"ULTIMATE_OSC_{short_period}_{medium_period}_{long_period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = uo
    return target


def chaikin_money_flow(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    period: int = 21,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Chaikin Money Flow volume indicator."""

    require_columns(data, (high, low, close, volume))

    # Calculate Money Flow Multiplier
    mfm = ((data[close] - data[low]) - (data[high] - data[close])) / (data[high] - data[low]).replace(0, np.nan)
    mfm = mfm.fillna(0.0)

    # Calculate Money Flow Volume
    mfv = mfm * data[volume]

    # Calculate Chaikin Money Flow
    cmf = mfv.rolling(window=period, min_periods=ensure_min_periods(period)).sum() / \
          data[volume].rolling(window=period, min_periods=ensure_min_periods(period)).sum()
    cmf = cmf.fillna(0.0)

    output_name = name or f"CMF_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = cmf
    return target


def aroon(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame:
    """Aroon Indicator with up and down components."""

    require_columns(data, (high, low))

    # Calculate Aroon Up
    aroon_up = 100 * (period - (period - data[high].rolling(window=period).apply(
        lambda x: period - np.argmax(x) - 1 if len(x) == period else np.nan, raw=True
    ))) / period

    # Calculate Aroon Down
    aroon_down = 100 * (period - (period - data[low].rolling(window=period).apply(
        lambda x: period - np.argmin(x) - 1 if len(x) == period else np.nan, raw=True
    ))) / period

    aroon_up = aroon_up.fillna(50.0)
    aroon_down = aroon_down.fillna(50.0)

    if isinstance(name, str):
        up_name = f"{name}_UP"
        down_name = f"{name}_DOWN"
    else:
        up_name = f"AROON_UP_{period}"
        down_name = f"AROON_DOWN_{period}"

    target = data if inplace else data.copy()
    target[up_name] = aroon_up
    target[down_name] = aroon_down
    return target


def aroon_oscillator(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Aroon Oscillator (Aroon Up - Aroon Down)."""

    aroon_frame = aroon(data, high=high, low=low, period=period, inplace=False)
    up_col = f"AROON_UP_{period}"
    down_col = f"AROON_DOWN_{period}"
    oscillator = aroon_frame[up_col] - aroon_frame[down_col]

    output_name = name or f"AROON_OSC_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = oscillator
    return target


def elder_ray(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    ema_period: int = 13,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame:
    """Elder Ray Index (Bull Power and Bear Power)."""

    require_columns(data, (high, low, close))

    # Calculate EMA of close
    ema_close = ema(data, column=close, period=ema_period, inplace=False)

    # Calculate Bull Power and Bear Power
    if isinstance(ema_close, pd.Series):
        ema_values = ema_close
    else:
        ema_values = ema_close[f"EMA_{ema_period}"]

    bull_power = data[high] - ema_values
    bear_power = data[low] - ema_values

    if isinstance(name, str):
        bull_name = f"{name}_BULL"
        bear_name = f"{name}_BEAR"
    else:
        bull_name = f"ELDER_BULL_{ema_period}"
        bear_name = f"ELDER_BEAR_{ema_period}"

    target = data if inplace else data.copy()
    target[bull_name] = bull_power
    target[bear_name] = bear_power
    return target


def force_index(
    data: pd.DataFrame,
    *,
    close: str = "close",
    volume: str = "volume",
    period: int = 13,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Force Index (price change * volume)."""

    require_columns(data, (close, volume))

    # Calculate raw force index
    force = (data[close].diff() * data[volume]).fillna(0.0)

    # Apply EMA smoothing
    force_smoothed = ema(pd.DataFrame({"force": force}), column="force", period=period, inplace=False)
    if isinstance(force_smoothed, pd.Series):
        force_values = force_smoothed
    else:
        force_values = force_smoothed[f"EMA_{period}"]

    output_name = name or f"FORCE_INDEX_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = force_values
    return target


def ease_of_movement(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    volume: str = "volume",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Ease of Movement indicator."""

    require_columns(data, (high, low, volume))

    # Calculate distance moved
    distance = ((data[high] + data[low]) / 2 - (data[high].shift(1) + data[low].shift(1)) / 2).fillna(0.0)

    # Calculate box ratio
    box_ratio = (data[volume] / 100000000) / (data[high] - data[low]).replace(0, np.nan)
    box_ratio = box_ratio.fillna(0.0)

    # Calculate EMV
    emv = distance / box_ratio
    emv = emv.fillna(0.0)

    # Apply smoothing
    emv_smoothed = emv.rolling(window=period, min_periods=ensure_min_periods(period)).mean()

    output_name = name or f"EOM_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = emv_smoothed
    return target


def volume_price_trend(
    data: pd.DataFrame,
    *,
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume Price Trend indicator."""

    require_columns(data, (close, volume))

    # Calculate price change percentage
    price_change_pct = data[close].pct_change().fillna(0.0)

    # Calculate VPT
    vpt = (price_change_pct * data[volume]).cumsum()

    output_name = name or "VPT"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = vpt
    return target


def negative_volume_index(
    data: pd.DataFrame,
    *,
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Negative Volume Index."""

    require_columns(data, (close, volume))

    nvi = pd.Series(1000.0, index=data.index)  # Start with 1000

    for i in range(1, len(data)):
        if data[volume].iloc[i] < data[volume].iloc[i-1]:
            pct_change = (data[close].iloc[i] - data[close].iloc[i-1]) / data[close].iloc[i-1]
            nvi.iloc[i] = nvi.iloc[i-1] * (1 + pct_change)
        else:
            nvi.iloc[i] = nvi.iloc[i-1]

    output_name = name or "NVI"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = nvi
    return target


def positive_volume_index(
    data: pd.DataFrame,
    *,
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Positive Volume Index."""

    require_columns(data, (close, volume))

    pvi = pd.Series(1000.0, index=data.index)  # Start with 1000

    for i in range(1, len(data)):
        if data[volume].iloc[i] > data[volume].iloc[i-1]:
            pct_change = (data[close].iloc[i] - data[close].iloc[i-1]) / data[close].iloc[i-1]
            pvi.iloc[i] = pvi.iloc[i-1] * (1 + pct_change)
        else:
            pvi.iloc[i] = pvi.iloc[i-1]

    output_name = name or "PVI"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pvi
    return target


def accumulation_distribution(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Accumulation/Distribution Line."""

    require_columns(data, (high, low, close, volume))

    # Calculate Money Flow Multiplier
    mfm = ((data[close] - data[low]) - (data[high] - data[close])) / (data[high] - data[low]).replace(0, np.nan)
    mfm = mfm.fillna(0.0)

    # Calculate Money Flow Volume
    mfv = mfm * data[volume]

    # Calculate Accumulation/Distribution Line
    ad = mfv.cumsum()

    output_name = name or "AD"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = ad
    return target


def chaikin_oscillator(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    fast_period: int = 3,
    slow_period: int = 10,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Chaikin Oscillator (fast EMA - slow EMA of Accumulation/Distribution)."""

    # First calculate Accumulation/Distribution
    ad_frame = accumulation_distribution(data, high=high, low=low, close=close, volume=volume, inplace=False)
    ad_series = ad_frame["AD"] if "AD" in ad_frame.columns else ad_frame.iloc[:, 0]

    # Calculate EMAs of AD
    fast_ema = ema(pd.DataFrame({"ad": ad_series}), column="ad", period=fast_period, inplace=False)
    slow_ema = ema(pd.DataFrame({"ad": ad_series}), column="ad", period=slow_period, inplace=False)

    fast_values = fast_ema[f"EMA_{fast_period}"] if isinstance(fast_ema, pd.DataFrame) else fast_ema
    slow_values = slow_ema[f"EMA_{slow_period}"] if isinstance(slow_ema, pd.DataFrame) else slow_ema

    # Calculate Chaikin Oscillator
    cho = fast_values - slow_values

    output_name = name or f"CHAIKIN_OSC_{fast_period}_{slow_period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = cho
    return target


# =============================================================================
# MOMENTUM & OSCILLATORS
# =============================================================================

def chande_momentum_oscillator(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Chande Momentum Oscillator."""

    selection = select_series(data, column)
    diff = selection.series.diff().fillna(0.0)

    gains = diff.where(diff > 0, 0.0)
    losses = -diff.where(diff < 0, 0.0)

    sum_gains = gains.rolling(window=period, min_periods=ensure_min_periods(period)).sum()
    sum_losses = losses.rolling(window=period, min_periods=ensure_min_periods(period)).sum()

    cmo = 100 * (sum_gains - sum_losses) / (sum_gains + sum_losses).replace(0, np.nan)
    cmo = cmo.fillna(0.0)

    output_name = name or f"CMO_{period}"
    return attach_result(selection, cmo, output_name, inplace=inplace)


def psychological_line(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 12,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Psychological Line indicator."""

    selection = select_series(data, column)

    # Count up days within the period
    up_days = (selection.series.diff() > 0).rolling(window=period, min_periods=ensure_min_periods(period)).sum()
    psychological = (up_days / period) * 100

    output_name = name or f"PSYCHO_{period}"
    return attach_result(selection, psychological, output_name, inplace=inplace)


def vertical_horizontal_filter(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 28,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Vertical Horizontal Filter."""

    selection = select_series(data, column)

    # Calculate absolute price changes
    abs_changes = selection.series.diff().abs()

    # Calculate VHF
    highest = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).max()
    lowest = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).min()
    numerator = highest - lowest
    denominator = abs_changes.rolling(window=period, min_periods=ensure_min_periods(period)).sum()

    vhf = numerator / denominator.replace(0, np.nan)
    vhf = vhf.fillna(0.0)

    output_name = name or f"VHF_{period}"
    return attach_result(selection, vhf, output_name, inplace=inplace)


def trend_intensity_index(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Trend Intensity Index."""

    selection = select_series(data, column)

    # Calculate absolute changes
    abs_change = selection.series.diff().abs()

    # Calculate trend intensity
    ma_abs_change = abs_change.rolling(window=period, min_periods=ensure_min_periods(period)).mean()
    ma_price = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).mean()

    tii = 100 * (ma_price / ma_abs_change).fillna(0.0)

    output_name = name or f"TII_{period}"
    return attach_result(selection, tii, output_name, inplace=inplace)


def bull_bear_power(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    period: int = 13,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame:
    """Bull and Bear Power (Elder Ray Index)."""

    return elder_ray(data, high=high, low=low, close=close, ema_period=period, inplace=inplace, name=name)


def trix(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 15,
    signal_period: int = 9,
    inplace: bool = False,
    prefix: str = "TRIX",
) -> pd.DataFrame | pd.Series:
    """TRIX (Triple Exponential Average)."""

    selection = select_series(data, column)

    # Calculate triple EMA
    ema1 = selection.series.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()
    ema2 = ema1.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()
    ema3 = ema2.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()

    # Calculate TRIX
    trix_line = ema3.pct_change() * 100
    trix_signal = trix_line.ewm(span=signal_period, adjust=False, min_periods=ensure_min_periods(signal_period)).mean()

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_line": trix_line,
            f"{prefix}_signal": trix_signal,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_line"] = trix_line
    target[f"{prefix}_signal"] = trix_signal
    return target


def vidya(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    short_period: int = 9,
    long_period: int = 26,
    alpha: float = 0.2,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Variable Index Dynamic Average."""

    selection = select_series(data, column)

    # Calculate efficiency ratio (ER)
    change = selection.series.diff().abs()
    volatility = change.rolling(window=long_period, min_periods=ensure_min_periods(long_period)).sum()
    er = change / volatility.replace(0, np.nan)
    er = er.fillna(0.0)

    # Calculate VIDYA
    vidya = pd.Series(index=selection.series.index, dtype=float)
    vidya.iloc[0] = selection.series.iloc[0]

    for i in range(1, len(selection.series)):
        er_value = er.iloc[i] if i >= long_period - 1 else 0.0
        alpha_dynamic = alpha * er_value
        vidya.iloc[i] = alpha_dynamic * selection.series.iloc[i] + (1 - alpha_dynamic) * vidya.iloc[i-1]

    output_name = name or f"VIDYA_{short_period}_{long_period}"
    return attach_result(selection, vidya, output_name, inplace=inplace)


def alma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 9,
    offset: float = 0.85,
    sigma: float = 6.0,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Arnaud Legoux Moving Average."""

    selection = select_series(data, column)

    # Calculate weights using Gaussian distribution
    m = offset * (period - 1)
    s = period / sigma
    weights = np.exp(-((np.arange(period) - m) ** 2) / (2 * s ** 2))
    weights = weights / weights.sum()

    # Apply weighted moving average
    alma_series = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).apply(
        lambda x: np.dot(x, weights[-len(x):]) if len(x) == period else np.nan, raw=True
    )

    output_name = name or f"ALMA_{period}"
    return attach_result(selection, alma_series, output_name, inplace=inplace)


def frama(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 16,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Fractal Adaptive Moving Average."""

    selection = select_series(data, column)

    # Calculate N3 parameter (dimension)
    hl_ratio = (selection.series.rolling(window=period).max() - selection.series.rolling(window=period).min()) / \
               selection.series.rolling(window=period).std()
    hl_ratio = hl_ratio.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    n3 = (np.log(hl_ratio) + np.log(2)) / np.log(2)
    n3 = np.clip(n3, 0.5, 2.0)

    # Calculate alpha
    alpha = np.exp(-4.6 * (n3 - 1))
    alpha = np.clip(alpha, 0.01, 1.0)

    # Calculate FRAMA
    frama = pd.Series(index=selection.series.index, dtype=float)
    frama.iloc[0] = selection.series.iloc[0]

    for i in range(1, len(selection.series)):
        alpha_val = alpha.iloc[i] if i >= period - 1 else 0.5
        frama.iloc[i] = alpha_val * selection.series.iloc[i] + (1 - alpha_val) * frama.iloc[i-1]

    output_name = name or f"FRAMA_{period}"
    return attach_result(selection, frama, output_name, inplace=inplace)


def gma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Guppy Multiple Moving Average."""

    selection = select_series(data, column)

    # Calculate multiple EMAs
    ema3 = selection.series.ewm(span=3, adjust=False).mean()
    ema5 = selection.series.ewm(span=5, adjust=False).mean()
    ema8 = selection.series.ewm(span=8, adjust=False).mean()
    ema10 = selection.series.ewm(span=10, adjust=False).mean()
    ema12 = selection.series.ewm(span=12, adjust=False).mean()
    ema15 = selection.series.ewm(span=15, adjust=False).mean()

    # Calculate GMA as average of EMAs
    gma = (ema3 + ema5 + ema8 + ema10 + ema12 + ema15) / 6

    output_name = name or f"GMA_{period}"
    return attach_result(selection, gma, output_name, inplace=inplace)


def jma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 7,
    phase: float = 0.0,
    power: float = 2.0,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Jurik Moving Average."""

    selection = select_series(data, column)

    # JMA calculation is complex, simplified version
    # In practice, JMA uses sophisticated smoothing algorithms
    # This is a basic approximation
    beta = 0.45 * (period - 1) / (0.45 * (period - 1) + 2)
    alpha = beta ** np.sqrt(power)

    jma = pd.Series(index=selection.series.index, dtype=float)
    jma.iloc[0] = selection.series.iloc[0]

    for i in range(1, len(selection.series)):
        jma.iloc[i] = alpha * selection.series.iloc[i] + (1 - alpha) * jma.iloc[i-1]

    output_name = name or f"JMA_{period}"
    return attach_result(selection, jma, output_name, inplace=inplace)


def lsma(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 25,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Least Squares Moving Average (Linear Regression)."""

    selection = select_series(data, column)

    def linear_regression(window_values: pd.Series) -> float:
        if len(window_values) < 2:
            return window_values.iloc[-1]
        x = np.arange(len(window_values))
        slope, intercept = np.polyfit(x, window_values.values, 1)
        return intercept + slope * (len(window_values) - 1)

    lsma_series = rolling_apply(selection.series, period, linear_regression, min_periods=ensure_min_periods(period))

    output_name = name or f"LSMA_{period}"
    return attach_result(selection, lsma_series, output_name, inplace=inplace)


def mcginley_dynamic(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """McGinley Dynamic."""

    selection = select_series(data, column)

    md = pd.Series(index=selection.series.index, dtype=float)
    md.iloc[0] = selection.series.iloc[0]

    for i in range(1, len(selection.series)):
        md.iloc[i] = md.iloc[i-1] + (selection.series.iloc[i] - md.iloc[i-1]) / (period * (selection.series.iloc[i] / md.iloc[i-1]) ** 4)

    output_name = name or f"MCGINLEY_{period}"
    return attach_result(selection, md, output_name, inplace=inplace)


def median_price(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Median Price."""

    require_columns(data, (high, low))
    median = (data[high] + data[low]) / 2

    output_name = name or "MEDIAN_PRICE"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = median
    return target


def typical_price(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Typical Price."""

    require_columns(data, (high, low, close))
    typical = (data[high] + data[low] + data[close]) / 3

    output_name = name or "TYPICAL_PRICE"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = typical
    return target


def weighted_close_price(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Weighted Close Price."""

    require_columns(data, (high, low, close))
    weighted = (data[high] + data[low] + 2 * data[close]) / 4

    output_name = name or "WEIGHTED_CLOSE"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = weighted
    return target


def price_channel(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    period: int = 20,
    inplace: bool = False,
    prefix: str = "PC",
) -> pd.DataFrame:
    """Price Channel."""

    require_columns(data, (high, low))

    upper = data[high].rolling(window=period, min_periods=ensure_min_periods(period)).max()
    lower = data[low].rolling(window=period, min_periods=ensure_min_periods(period)).min()
    middle = (upper + lower) / 2

    target = data if inplace else data.copy()
    target[f"{prefix}_upper"] = upper
    target[f"{prefix}_lower"] = lower
    target[f"{prefix}_mid"] = middle
    return target


def regression_channel(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 20,
    std_multiplier: float = 2.0,
    inplace: bool = False,
    prefix: str = "REG",
) -> pd.DataFrame | pd.Series:
    """Regression Channel."""

    selection = select_series(data, column)

    def regression_channel_calc(window_values: pd.Series) -> tuple[float, float, float]:
        if len(window_values) < 2:
            return window_values.iloc[-1], window_values.iloc[-1], window_values.iloc[-1]

        x = np.arange(len(window_values))
        slope, intercept = np.polyfit(x, window_values.values, 1)

        regression_line = intercept + slope * x
        std = np.std(window_values.values - regression_line)

        midline = intercept + slope * (len(window_values) - 1)
        upper = midline + std_multiplier * std
        lower = midline - std_multiplier * std

        return midline, upper, lower

    results = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).apply(
        lambda x: regression_channel_calc(x)[0], raw=False
    )
    upper_results = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).apply(
        lambda x: regression_channel_calc(x)[1], raw=False
    )
    lower_results = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).apply(
        lambda x: regression_channel_calc(x)[2], raw=False
    )

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_mid": results,
            f"{prefix}_upper": upper_results,
            f"{prefix}_lower": lower_results,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_mid"] = results
    target[f"{prefix}_upper"] = upper_results
    target[f"{prefix}_lower"] = lower_results
    return target


def standard_error_channel(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 20,
    std_multiplier: float = 2.0,
    inplace: bool = False,
    prefix: str = "SEC",
) -> pd.DataFrame | pd.Series:
    """Standard Error Channel."""

    selection = select_series(data, column)

    mean = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).mean()
    std = selection.series.rolling(window=period, min_periods=ensure_min_periods(period)).std()
    se = std / np.sqrt(period)

    upper = mean + std_multiplier * se
    lower = mean - std_multiplier * se

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_mid": mean,
            f"{prefix}_upper": upper,
            f"{prefix}_lower": lower,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_mid"] = mean
    target[f"{prefix}_upper"] = upper
    target[f"{prefix}_lower"] = lower
    return target


# =============================================================================
# PATTERN RECOGNITION
# =============================================================================

def andrews_pitchfork(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    period: int = 30,
    inplace: bool = False,
    prefix: str = "APF",
) -> pd.DataFrame:
    """Andrews' Pitchfork pattern."""

    require_columns(data, (high, low, close))

    # This is a simplified implementation
    # Real Andrews' Pitchfork requires manual point selection
    # Here we use pivot points as approximation

    # Calculate median line (50% retracement)
    pivot_high = data[high].rolling(window=period).max()
    pivot_low = data[low].rolling(window=period).min()
    median = (pivot_high + pivot_low) / 2

    # Calculate upper and lower parallel lines
    range_size = pivot_high - pivot_low
    upper = median + range_size / 2
    lower = median - range_size / 2

    target = data if inplace else data.copy()
    target[f"{prefix}_median"] = median
    target[f"{prefix}_upper"] = upper
    target[f"{prefix}_lower"] = lower
    return target


def gann_angles(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    start_idx: int = 0,
    inplace: bool = False,
    prefix: str = "GANN",
) -> pd.DataFrame | pd.Series:
    """Gann Angles (1x1, 1x2, 2x1, etc.)."""

    selection = select_series(data, column)

    # Start from a significant point (could be customized)
    start_price = selection.series.iloc[start_idx] if start_idx < len(selection.series) else selection.series.iloc[0]
    start_time = selection.series.index[start_idx] if start_idx < len(selection.series) else selection.series.index[0]

    # Calculate time elapsed
    time_elapsed = (selection.series.index - start_time).days

    # Gann angles (price changes per unit time)
    angle_1x1 = start_price + time_elapsed  # 45-degree angle
    angle_1x2 = start_price + time_elapsed / 2  # 26.5-degree angle
    angle_2x1 = start_price + time_elapsed * 2  # 63.4-degree angle
    angle_1x4 = start_price + time_elapsed / 4  # 14-degree angle
    angle_4x1 = start_price + time_elapsed * 4  # 76-degree angle

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_1x1": angle_1x1,
            f"{prefix}_1x2": angle_1x2,
            f"{prefix}_2x1": angle_2x1,
            f"{prefix}_1x4": angle_1x4,
            f"{prefix}_4x1": angle_4x1,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_1x1"] = angle_1x1
    target[f"{prefix}_1x2"] = angle_1x2
    target[f"{prefix}_2x1"] = angle_2x1
    target[f"{prefix}_1x4"] = angle_1x4
    target[f"{prefix}_4x1"] = angle_4x1
    return target


def fibonacci_retracements(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    lookback: int = 50,
    inplace: bool = False,
    prefix: str = "FIB_RET",
) -> pd.DataFrame | pd.Series:
    """Fibonacci Retracement levels."""

    selection = select_series(data, column)

    # Find swing high and low
    swing_high = selection.series.rolling(window=lookback).max()
    swing_low = selection.series.rolling(window=lookback).min()
    range_size = swing_high - swing_low

    # Fibonacci retracement levels
    fib_0 = swing_high  # 0% (swing high)
    fib_23_6 = swing_high - range_size * 0.236
    fib_38_2 = swing_high - range_size * 0.382
    fib_50 = swing_high - range_size * 0.5
    fib_61_8 = swing_high - range_size * 0.618
    fib_78_6 = swing_high - range_size * 0.786
    fib_100 = swing_low  # 100% (swing low)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_0": fib_0,
            f"{prefix}_23_6": fib_23_6,
            f"{prefix}_38_2": fib_38_2,
            f"{prefix}_50": fib_50,
            f"{prefix}_61_8": fib_61_8,
            f"{prefix}_78_6": fib_78_6,
            f"{prefix}_100": fib_100,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_0"] = fib_0
    target[f"{prefix}_23_6"] = fib_23_6
    target[f"{prefix}_38_2"] = fib_38_2
    target[f"{prefix}_50"] = fib_50
    target[f"{prefix}_61_8"] = fib_61_8
    target[f"{prefix}_78_6"] = fib_78_6
    target[f"{prefix}_100"] = fib_100
    return target


def fibonacci_extensions(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    lookback: int = 50,
    inplace: bool = False,
    prefix: str = "FIB_EXT",
) -> pd.DataFrame | pd.Series:
    """Fibonacci Extension levels."""

    selection = select_series(data, column)

    # Find swing high and low
    swing_high = selection.series.rolling(window=lookback).max()
    swing_low = selection.series.rolling(window=lookback).min()
    range_size = swing_high - swing_low

    # Fibonacci extension levels (beyond 100%)
    fib_127_2 = swing_low - range_size * 0.272
    fib_161_8 = swing_low - range_size * 0.618
    fib_200 = swing_low - range_size * 1.0
    fib_261_8 = swing_low - range_size * 1.618
    fib_361_8 = swing_low - range_size * 2.618

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_127_2": fib_127_2,
            f"{prefix}_161_8": fib_161_8,
            f"{prefix}_200": fib_200,
            f"{prefix}_261_8": fib_261_8,
            f"{prefix}_361_8": fib_361_8,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_127_2"] = fib_127_2
    target[f"{prefix}_161_8"] = fib_161_8
    target[f"{prefix}_200"] = fib_200
    target[f"{prefix}_261_8"] = fib_261_8
    target[f"{prefix}_361_8"] = fib_361_8
    return target


def harmonic_patterns(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    prefix: str = "HARMONIC",
) -> pd.DataFrame:
    """Harmonic Pattern Detection (Gartley, Butterfly, Bat, Crab)."""

    require_columns(data, (high, low, close))

    # This is a simplified implementation
    # Real harmonic pattern detection requires complex geometric calculations

    # Calculate pivot points as pattern anchors
    pivot_high = data[high].rolling(window=20).max()
    pivot_low = data[low].rolling(window=20).min()

    # Calculate Fibonacci relationships (simplified)
    range_size = pivot_high - pivot_low
    fib_61_8 = pivot_low + range_size * 0.618
    fib_78_6 = pivot_low + range_size * 0.786
    fib_88_6 = pivot_low + range_size * 0.886

    # Pattern completion signals
    gartley_signal = (data[close] >= fib_78_6) & (data[close] <= fib_88_6)
    butterfly_signal = (data[close] >= fib_61_8) & (data[close] <= fib_78_6)
    bat_signal = (data[close] >= fib_61_8) & (data[close] <= fib_78_6)
    crab_signal = (data[close] >= fib_88_6) & (data[close] <= pivot_high)

    target = data if inplace else data.copy()
    target[f"{prefix}_gartley"] = gartley_signal.astype(int)
    target[f"{prefix}_butterfly"] = butterfly_signal.astype(int)
    target[f"{prefix}_bat"] = bat_signal.astype(int)
    target[f"{prefix}_crab"] = crab_signal.astype(int)
    return target


def wolfe_waves(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    prefix: str = "WOLFE",
) -> pd.DataFrame:
    """Wolfe Wave pattern detection."""

    require_columns(data, (high, low, close))

    # Simplified Wolfe Wave detection
    # Real implementation requires trend line analysis

    # Calculate trend direction
    trend_up = data[close] > data[close].shift(5)
    trend_down = data[close] < data[close].shift(5)

    # Wave completion signals (simplified)
    wave_up_signal = trend_up & (data[close] > data[high].shift(1))
    wave_down_signal = trend_down & (data[close] < data[low].shift(1))

    target = data if inplace else data.copy()
    target[f"{prefix}_up_wave"] = wave_up_signal.astype(int)
    target[f"{prefix}_down_wave"] = wave_down_signal.astype(int)
    return target


def gartley_patterns(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    prefix: str = "GARTLEY",
) -> pd.DataFrame:
    """Gartley Pattern Detection."""

    require_columns(data, (high, low, close))

    # Simplified Gartley pattern detection
    # Real Gartley requires precise Fibonacci measurements

    # Calculate potential pattern points
    pivot_high = data[high].rolling(window=15).max()
    pivot_low = data[low].rolling(window=15).min()

    # Gartley completion (XA, AB, BC, CD)
    range_hl = pivot_high - pivot_low
    point_b = pivot_high - range_hl * 0.618  # AB = 0.618 XA
    point_c = pivot_high - range_hl * 0.382  # BC = 0.382 AB
    point_d = pivot_high - range_hl * 0.786  # CD = 0.786 BC

    # Pattern completion signal
    gartley_complete = (data[close] >= point_d - range_hl * 0.05) & (data[close] <= point_d + range_hl * 0.05)

    target = data if inplace else data.copy()
    target[f"{prefix}_complete"] = gartley_complete.astype(int)
    target[f"{prefix}_point_b"] = point_b
    target[f"{prefix}_point_c"] = point_c
    target[f"{prefix}_point_d"] = point_d
    return target


def head_shoulders_patterns(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    lookback: int = 50,
    inplace: bool = False,
    prefix: str = "HS",
) -> pd.DataFrame:
    """Head and Shoulders Pattern Detection."""

    require_columns(data, (high, low, close))

    # Find local maxima and minima
    local_max = (data[high] == data[high].rolling(window=5, center=True).max())
    local_min = (data[low] == data[low].rolling(window=5, center=True).min())

    # Head and Shoulders logic (simplified)
    # Left shoulder: peak, then decline
    # Head: higher peak
    # Right shoulder: lower peak similar to left shoulder
    # Neckline: connects lows between shoulders and head

    # This is a very simplified version - real H&S detection is complex
    shoulder_height = data[high].rolling(window=lookback).max()
    head_height = data[high].rolling(window=lookback).max() * 1.1  # Head should be higher

    # Pattern completion signal
    hs_complete = (data[close] < data[close].shift(10)) & (data[high] < shoulder_height)

    target = data if inplace else data.copy()
    target[f"{prefix}_pattern"] = hs_complete.astype(int)
    target[f"{prefix}_shoulder_level"] = shoulder_height
    target[f"{prefix}_head_level"] = head_height
    return target


def double_top_bottom(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    tolerance: float = 0.02,
    lookback: int = 30,
    inplace: bool = False,
    prefix: str = "DTB",
) -> pd.DataFrame | pd.Series:
    """Double Top/Bottom Pattern Detection."""

    selection = select_series(data, column)

    # Find local maxima and minima
    local_max = selection.series.rolling(window=5, center=True).max() == selection.series
    local_min = selection.series.rolling(window=5, center=True).min() == selection.series

    # Double top/bottom logic
    max_values = selection.series[local_max].rolling(window=lookback).max()
    min_values = selection.series[local_min].rolling(window=lookback).min()

    # Check for double tops/bottoms
    double_top = local_max & (abs(selection.series - max_values) / max_values < tolerance)
    double_bottom = local_min & (abs(selection.series - min_values) / min_values < tolerance)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_double_top": double_top.astype(int),
            f"{prefix}_double_bottom": double_bottom.astype(int),
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_double_top"] = double_top.astype(int)
    target[f"{prefix}_double_bottom"] = double_bottom.astype(int)
    return target


def wedge_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 25,
    inplace: bool = False,
    prefix: str = "WEDGE",
) -> pd.DataFrame | pd.Series:
    """Wedge Pattern Detection (Rising/Falling Wedges)."""

    selection = select_series(data, column)

    # Calculate trend lines using linear regression
    def calculate_trendline(window_values: pd.Series, is_upper: bool) -> float:
        if len(window_values) < 5:
            return window_values.iloc[-1]

        x = np.arange(len(window_values))
        slope, intercept = np.polyfit(x, window_values.values, 1)

        # For wedges, upper trendline slopes down, lower slopes up (for rising wedge)
        # This is simplified - real wedge detection is more complex
        return intercept + slope * (len(window_values) - 1)

    # Upper and lower trendlines
    upper_trend = selection.series.rolling(window=period).apply(
        lambda x: calculate_trendline(x, True), raw=False
    )
    lower_trend = selection.series.rolling(window=period).apply(
        lambda x: calculate_trendline(x, False), raw=False
    )

    # Wedge completion signal
    wedge_complete = (selection.series >= lower_trend) & (selection.series <= upper_trend) & \
                    (abs(upper_trend - lower_trend) < selection.series.rolling(window=period).std())

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_complete": wedge_complete.astype(int),
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_complete"] = wedge_complete.astype(int)
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def triangle_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 30,
    inplace: bool = False,
    prefix: str = "TRIANGLE",
) -> pd.DataFrame | pd.Series:
    """Triangle Pattern Detection (Ascending/Descending/Symmetrical)."""

    selection = select_series(data, column)

    # Calculate upper and lower bounds
    upper_bound = selection.series.rolling(window=period).max()
    lower_bound = selection.series.rolling(window=period).min()

    # Triangle logic: converging trendlines
    range_size = upper_bound - lower_bound
    range_trend = range_size.pct_change(period).fillna(0)

    # Triangle completion signal (range decreasing)
    triangle_complete = (range_trend < -0.1) & (selection.series >= lower_bound) & (selection.series <= upper_bound)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_complete": triangle_complete.astype(int),
            f"{prefix}_upper_bound": upper_bound,
            f"{prefix}_lower_bound": lower_bound,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_complete"] = triangle_complete.astype(int)
    target[f"{prefix}_upper_bound"] = upper_bound
    target[f"{prefix}_lower_bound"] = lower_bound
    return target


def flag_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 20,
    inplace: bool = False,
    prefix: str = "FLAG",
) -> pd.DataFrame | pd.Series:
    """Flag Pattern Detection."""

    selection = select_series(data, column)

    # Flag patterns have a strong move (flagpole) followed by consolidation
    # Calculate recent volatility
    returns = selection.series.pct_change().fillna(0)
    volatility = returns.rolling(window=period).std()

    # Flagpole: strong directional move
    flagpole = abs(selection.series - selection.series.shift(period)) > selection.series.rolling(window=period*2).std() * 2

    # Consolidation: lower volatility after flagpole
    consolidation = volatility < volatility.shift(period).rolling(window=period).mean()

    # Flag completion
    flag_complete = flagpole & consolidation

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_complete": flag_complete.astype(int),
            f"{prefix}_flagpole": flagpole.astype(int),
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_complete"] = flag_complete.astype(int)
    target[f"{prefix}_flagpole"] = flagpole.astype(int)
    return target


def cup_handle_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    lookback: int = 50,
    inplace: bool = False,
    prefix: str = "CUP_HANDLE",
) -> pd.DataFrame | pd.Series:
    """Cup and Handle Pattern Detection."""

    selection = select_series(data, column)

    # Cup: rounded bottom formation
    # Handle: small consolidation on the right side

    # Calculate the "cup" - U-shaped formation
    min_price = selection.series.rolling(window=lookback).min()
    max_price = selection.series.rolling(window=lookback).max()
    mid_price = (max_price + min_price) / 2

    # Cup completion: price returns to previous high levels
    cup_complete = (selection.series >= max_price * 0.95) & (selection.series >= mid_price)

    # Handle: small downward move after cup
    handle = (selection.series < max_price) & (selection.series > min_price * 1.1)

    # Pattern completion
    cup_handle_complete = cup_complete & handle

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_complete": cup_handle_complete.astype(int),
            f"{prefix}_cup_complete": cup_complete.astype(int),
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_complete"] = cup_handle_complete.astype(int)
    target[f"{prefix}_cup_complete"] = cup_complete.astype(int)
    return target


# =============================================================================
# ADVANCED PATTERN RECOGNITION ENGINE
# =============================================================================

def advanced_head_shoulders(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    lookback: int = 100,
    tolerance: float = 0.05,
    inplace: bool = False,
    prefix: str = "ADV_HS",
) -> pd.DataFrame:
    """Advanced Head and Shoulders Pattern Detection with volume confirmation."""

    require_columns(data, (high, low, close))

    # Find local maxima (potential shoulders and head)
    local_max = (data[high] == data[high].rolling(window=5, center=True).max())

    # Find local minima (neckline)
    local_min = (data[low] == data[low].rolling(window=5, center=True).min())

    # Extract peak values
    peaks = data[high][local_max]
    troughs = data[low][local_min]

    # Initialize pattern signals
    head_shoulder_signal = pd.Series(0, index=data.index)

    # Look for H&S pattern within lookback window
    for i in range(lookback, len(data)):
        window_peaks = peaks.iloc[i-lookback:i]
        window_troughs = troughs.iloc[i-lookback:i]

        if len(window_peaks) >= 3 and len(window_troughs) >= 2:
            # Sort peaks by value (descending)
            sorted_peaks = window_peaks.sort_values(ascending=False)

            if len(sorted_peaks) >= 3:
                # Check for head and shoulders structure
                head = sorted_peaks.iloc[0]  # Highest peak
                shoulder1 = sorted_peaks.iloc[1]  # Second highest
                shoulder2 = sorted_peaks.iloc[2]  # Third highest

                # Head should be significantly higher than shoulders
                head_vs_shoulders = (head > shoulder1 * (1 + tolerance)) and (head > shoulder2 * (1 + tolerance))

                # Shoulders should be similar height
                shoulders_similar = abs(shoulder1 - shoulder2) / max(shoulder1, shoulder2) < tolerance

                # Check neckline (lowest troughs)
                neckline_level = window_troughs.min()

                # Pattern completion check
                if head_vs_shoulders and shoulders_similar:
                    # Mark the pattern completion point
                    head_shoulder_signal.iloc[i] = 1

    target = data if inplace else data.copy()
    target[f"{prefix}_pattern"] = head_shoulder_signal
    target[f"{prefix}_strength"] = head_shoulder_signal.rolling(window=20).sum()  # Pattern strength over time
    return target


def complex_harmonic_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    pattern_type: str = "gartley",
    tolerance: float = 0.05,
    inplace: bool = False,
    prefix: str = "HARMONIC",
) -> pd.DataFrame | pd.Series:
    """Complex Harmonic Pattern Detection (Gartley, Butterfly, Bat, Crab, Shark)."""

    selection = select_series(data, column)

    # Find swing points
    local_max = selection.series.rolling(window=5, center=True).max() == selection.series
    local_min = selection.series.rolling(window=5, center=True).min() == selection.series

    # Extract swing points
    highs = selection.series[local_max]
    lows = selection.series[local_min]

    # Pattern ratios based on Fibonacci
    ratios = {
        "gartley": {
            "XA": 1.0, "AB": 0.618, "BC": 0.382, "CD": 0.786,
            "BC_alt": 0.886, "CD_alt": 1.272, "CD_alt2": 1.618
        },
        "butterfly": {
            "XA": 1.0, "AB": 0.786, "BC": 0.382, "CD": 1.618,
            "BC_alt": 0.886, "CD_alt": 2.618
        },
        "bat": {
            "XA": 1.0, "AB": 0.382, "BC": 0.382, "CD": 0.886,
            "BC_alt": 0.5, "CD_alt": 1.618
        },
        "crab": {
            "XA": 1.0, "AB": 0.382, "BC": 0.886, "CD": 2.618,
            "BC_alt": 1.13, "CD_alt": 3.618
        },
        "shark": {
            "XA": 1.0, "AB": 1.618, "BC": 1.13, "CD": 0.886,
            "BC_alt": 1.618, "CD_alt": 1.13
        }
    }

    pattern_ratios = ratios.get(pattern_type, ratios["gartley"])

    # Initialize pattern detection
    pattern_signal = pd.Series(0, index=selection.series.index)
    pattern_strength = pd.Series(0.0, index=selection.series.index)

    # Look for harmonic patterns
    lookback = 50
    for i in range(lookback, len(selection.series)):
        recent_highs = highs.iloc[i-lookback:i]
        recent_lows = lows.iloc[i-lookback:i]

        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            # Try to find XA, AB, BC, CD points
            X = selection.series.iloc[i-lookback]  # Start point

            # Find potential A, B, C, D points
            potential_points = []
            for j in range(i-lookback+1, i):
                if local_max.iloc[j] or local_min.iloc[j]:
                    potential_points.append((j, selection.series.iloc[j]))

            if len(potential_points) >= 3:
                # Check for harmonic ratios
                for a_idx in range(len(potential_points)-2):
                    for b_idx in range(a_idx+1, len(potential_points)-1):
                        for c_idx in range(b_idx+1, len(potential_points)):
                            A = potential_points[a_idx][1]
                            B = potential_points[b_idx][1]
                            C = potential_points[c_idx][1]

                            # Calculate ratios
                            XA_ratio = abs(A - X) / abs(X) if X != 0 else 0
                            AB_ratio = abs(B - A) / abs(A - X) if abs(A - X) != 0 else 0
                            BC_ratio = abs(C - B) / abs(B - A) if abs(B - A) != 0 else 0

                            # Check if ratios match harmonic pattern
                            ratio_match = (
                                abs(XA_ratio - pattern_ratios["XA"]) < tolerance and
                                abs(AB_ratio - pattern_ratios["AB"]) < tolerance and
                                abs(BC_ratio - pattern_ratios["BC"]) < tolerance
                            )

                            if ratio_match:
                                pattern_signal.iloc[i] = 1
                                pattern_strength.iloc[i] = 1.0 - (
                                    abs(XA_ratio - pattern_ratios["XA"]) +
                                    abs(AB_ratio - pattern_ratios["AB"]) +
                                    abs(BC_ratio - pattern_ratios["BC"])
                                ) / 3

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_{pattern_type}": pattern_signal,
            f"{prefix}_{pattern_type}_strength": pattern_strength,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_{pattern_type}"] = pattern_signal
    target[f"{prefix}_{pattern_type}_strength"] = pattern_strength
    return target


def advanced_wedge_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    wedge_type: str = "rising",
    period: int = 25,
    inplace: bool = False,
    prefix: str = "ADV_WEDGE",
) -> pd.DataFrame | pd.Series:
    """Advanced Wedge Pattern Detection with trend line analysis."""

    selection = select_series(data, column)

    # Calculate upper and lower trendlines
    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]

        # Calculate linear regression for upper and lower bounds
        x = np.arange(len(window))

        # Upper trendline (connecting highs)
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            upper_slope, upper_intercept = np.polyfit(
                x[len(x)-len(upper_points.dropna()):],
                upper_points.dropna().values, 1
            )
            upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)

        # Lower trendline (connecting lows)
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            lower_slope, lower_intercept = np.polyfit(
                x[len(x)-len(lower_points.dropna()):],
                lower_points.dropna().values, 1
            )
            lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)

    # Wedge pattern logic
    wedge_signal = pd.Series(0, index=selection.series.index)

    if wedge_type == "rising":
        # Rising wedge: both trendlines slope up, but upper slope < lower slope
        upper_slope = upper_trend.diff(period).fillna(0)
        lower_slope = lower_trend.diff(period).fillna(0)
        wedge_condition = (upper_slope > 0) & (lower_slope > 0) & (upper_slope < lower_slope)

    elif wedge_type == "falling":
        # Falling wedge: both trendlines slope down, but upper slope > lower slope
        upper_slope = upper_trend.diff(period).fillna(0)
        lower_slope = lower_trend.diff(period).fillna(0)
        wedge_condition = (upper_slope < 0) & (lower_slope < 0) & (upper_slope > lower_slope)

    else:  # symmetrical
        # Converging trendlines with opposite slopes
        slope_diff = upper_trend.diff(period).fillna(0) + lower_trend.diff(period).fillna(0)
        wedge_condition = abs(slope_diff) < 0.001  # Very small slope difference

    # Price within wedge boundaries
    price_in_wedge = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    # Volume confirmation (lower volume in wedges)
    if isinstance(selection.data, pd.DataFrame) and "volume" in selection.data.columns:
        avg_volume = selection.data["volume"].rolling(window=period).mean()
        volume_confirm = selection.data["volume"] < avg_volume * 0.8
        wedge_signal = (wedge_condition & price_in_wedge & volume_confirm).astype(int)
    else:
        wedge_signal = (wedge_condition & price_in_wedge).astype(int)

    # Pattern completion (breakout from wedge)
    wedge_breakout = pd.Series(0, index=selection.series.index)
    for i in range(1, len(selection.series)):
        if wedge_signal.iloc[i-1] == 1 and wedge_signal.iloc[i] == 0:
            wedge_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_{wedge_type}": wedge_signal,
            f"{prefix}_breakout": wedge_breakout,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_{wedge_type}"] = wedge_signal
    target[f"{prefix}_breakout"] = wedge_breakout
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def advanced_triangle_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    triangle_type: str = "symmetrical",
    period: int = 30,
    inplace: bool = False,
    prefix: str = "ADV_TRIANGLE",
) -> pd.DataFrame | pd.Series:
    """Advanced Triangle Pattern Detection with volume analysis."""

    selection = select_series(data, column)

    # Calculate trendlines
    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 2:
            try:
                upper_slope, upper_intercept = np.polyfit(
                    x[-len(upper_points.dropna()):],
                    upper_points.dropna().values, 1
                )
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 2:
            try:
                lower_slope, lower_intercept = np.polyfit(
                    x[-len(lower_points.dropna()):],
                    lower_points.dropna().values, 1
                )
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Triangle pattern logic
    triangle_signal = pd.Series(0, index=selection.series.index)

    if triangle_type == "ascending":
        # Ascending triangle: horizontal upper trendline, rising lower trendline
        upper_flat = upper_trend.rolling(window=10).std() < upper_trend.rolling(window=10).mean() * 0.01
        lower_rising = lower_trend.diff(5).fillna(0) > 0
        triangle_condition = upper_flat & lower_rising

    elif triangle_type == "descending":
        # Descending triangle: horizontal lower trendline, falling upper trendline
        lower_flat = lower_trend.rolling(window=10).std() < lower_trend.rolling(window=10).mean() * 0.01
        upper_falling = upper_trend.diff(5).fillna(0) < 0
        triangle_condition = lower_flat & upper_falling

    else:  # symmetrical
        # Both trendlines converging to a point
        range_size = upper_trend - lower_trend
        range_trend = range_size.pct_change(period).fillna(0)
        triangle_condition = range_trend < -0.05  # Range decreasing

    # Price within triangle boundaries
    price_in_triangle = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    # Volume pattern (typically decreasing in triangles)
    volume_confirm = pd.Series(True, index=selection.series.index)
    if isinstance(selection.data, pd.DataFrame) and "volume" in selection.data.columns:
        volume_trend = selection.data["volume"].rolling(window=period).mean().pct_change(5).fillna(0)
        volume_confirm = volume_trend < 0  # Decreasing volume

    triangle_signal = (triangle_condition & price_in_triangle & volume_confirm).astype(int)

    # Pattern completion (breakout from triangle)
    triangle_breakout = pd.Series(0, index=selection.series.index)
    breakout_direction = pd.Series(0, index=selection.series.index)  # 1=bullish, -1=bearish

    for i in range(1, len(selection.series)):
        if triangle_signal.iloc[i-1] == 1 and triangle_signal.iloc[i] == 0:
            # Determine breakout direction
            if selection.series.iloc[i] > upper_trend.iloc[i-1]:
                breakout_direction.iloc[i] = 1  # Bullish breakout
            elif selection.series.iloc[i] < lower_trend.iloc[i-1]:
                breakout_direction.iloc[i] = -1  # Bearish breakout
            triangle_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_{triangle_type}": triangle_signal,
            f"{prefix}_breakout": triangle_breakout,
            f"{prefix}_breakout_dir": breakout_direction,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_{triangle_type}"] = triangle_signal
    target[f"{prefix}_breakout"] = triangle_breakout
    target[f"{prefix}_breakout_dir"] = breakout_direction
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def rectangle_box_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 40,
    tolerance: float = 0.03,
    inplace: bool = False,
    prefix: str = "RECTANGLE",
) -> pd.DataFrame | pd.Series:
    """Rectangle/Box Pattern Detection."""

    selection = select_series(data, column)

    # Find resistance and support levels
    resistance = selection.series.rolling(window=period).max()
    support = selection.series.rolling(window=period).min()

    # Rectangle pattern: price oscillating between two parallel levels
    rectangle_signal = pd.Series(0, index=selection.series.index)

    # Check if price stays within a narrow range
    range_size = resistance - support
    price_range = selection.series.max() - selection.series.min()

    # Rectangle condition: consistent high/low touches
    resistance_touches = (selection.series >= resistance * (1 - tolerance)).astype(int)
    support_touches = (selection.series <= support * (1 + tolerance)).astype(int)

    # Multiple touches on both levels
    resistance_touch_count = resistance_touches.rolling(window=period).sum()
    support_touch_count = support_touches.rolling(window=period).sum()

    # Rectangle formation
    rectangle_condition = (
        (resistance_touch_count >= 2) &
        (support_touch_count >= 2) &
        (range_size / selection.series.rolling(window=period).mean() < 0.1)  # Narrow range
    )

    rectangle_signal = rectangle_condition.astype(int)

    # Pattern completion (breakout from rectangle)
    rectangle_breakout = pd.Series(0, index=selection.series.index)
    breakout_direction = pd.Series(0, index=selection.series.index)

    for i in range(1, len(selection.series)):
        if rectangle_signal.iloc[i-1] == 1 and rectangle_signal.iloc[i] == 0:
            # Determine breakout direction
            if selection.series.iloc[i] > resistance.iloc[i-1]:
                breakout_direction.iloc[i] = 1  # Bullish breakout
            elif selection.series.iloc[i] < support.iloc[i-1]:
                breakout_direction.iloc[i] = -1  # Bearish breakout
            rectangle_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": rectangle_signal,
            f"{prefix}_breakout": rectangle_breakout,
            f"{prefix}_breakout_dir": breakout_direction,
            f"{prefix}_resistance": resistance,
            f"{prefix}_support": support,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = rectangle_signal
    target[f"{prefix}_breakout"] = rectangle_breakout
    target[f"{prefix}_breakout_dir"] = breakout_direction
    target[f"{prefix}_resistance"] = resistance
    target[f"{prefix}_support"] = support
    return target


def diamond_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 35,
    inplace: bool = False,
    prefix: str = "DIAMOND",
) -> pd.DataFrame | pd.Series:
    """Diamond Pattern Detection."""

    selection = select_series(data, column)

    # Diamond pattern combines broadening and contracting phases
    # First expanding, then contracting

    # Calculate volatility to detect expansion/contraction
    returns = selection.series.pct_change().fillna(0)
    volatility = returns.rolling(window=10).std()

    # First half: expanding (broadening pattern)
    first_half_vol = volatility.iloc[:period//2].mean()
    # Second half: contracting (triangle pattern)
    second_half_vol = volatility.iloc[period//2:period].mean()

    # Diamond condition: first expanding, then contracting
    diamond_condition = (first_half_vol > second_half_vol * 1.2) & (volatility < volatility.rolling(window=period).quantile(0.8))

    # Volume confirmation (typically high volume at breakout)
    volume_confirm = pd.Series(True, index=selection.series.index)
    if isinstance(selection.data, pd.DataFrame) and "volume" in selection.data.columns:
        volume_trend = selection.data["volume"].rolling(window=period).mean()
        volume_confirm = selection.data["volume"] > volume_trend

    diamond_signal = (diamond_condition & volume_confirm).astype(int)

    # Pattern completion (breakout from diamond)
    diamond_breakout = pd.Series(0, index=selection.series.index)
    for i in range(period, len(selection.series)):
        if diamond_signal.iloc[i] == 1:
            # Check for breakout from recent high/low
            recent_high = selection.series.iloc[i-period:i].max()
            recent_low = selection.series.iloc[i-period:i].min()

            if selection.series.iloc[i] > recent_high * 1.02 or selection.series.iloc[i] < recent_low * 0.98:
                diamond_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": diamond_signal,
            f"{prefix}_breakout": diamond_breakout,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = diamond_signal
    target[f"{prefix}_breakout"] = diamond_breakout
    return target


def broadening_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 25,
    inplace: bool = False,
    prefix: str = "BROADENING",
) -> pd.DataFrame | pd.Series:
    """Broadening Pattern Detection (Megaphone)."""

    selection = select_series(data, column)

    # Broadening patterns have expanding ranges
    # Both upper and lower trendlines diverge

    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline (expanding upward)
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            try:
                upper_slope, upper_intercept = np.polyfit(
                    x[-len(upper_points.dropna()):],
                    upper_points.dropna().values, 1
                )
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline (expanding downward)
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            try:
                lower_slope, lower_intercept = np.polyfit(
                    x[-len(lower_points.dropna()):],
                    lower_points.dropna().values, 1
                )
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Broadening condition: both trendlines diverging
    upper_slope = upper_trend.diff(period).fillna(0)
    lower_slope = lower_trend.diff(period).fillna(0)

    # Opposite slopes indicate broadening
    broadening_condition = (upper_slope > 0) & (lower_slope < 0) & (abs(upper_slope) > abs(lower_slope) * 0.5)

    # Price within broadening boundaries
    price_in_pattern = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    broadening_signal = (broadening_condition & price_in_pattern).astype(int)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": broadening_signal,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = broadening_signal
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def contracting_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 25,
    inplace: bool = False,
    prefix: str = "CONTRACTING",
) -> pd.DataFrame | pd.Series:
    """Contracting Pattern Detection."""

    selection = select_series(data, column)

    # Contracting patterns have decreasing ranges
    # Trendlines converge

    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline (converging)
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            try:
                upper_slope, upper_intercept = np.polyfit(
                    x[-len(upper_points.dropna()):],
                    upper_points.dropna().values, 1
                )
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline (converging)
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            try:
                lower_slope, lower_intercept = np.polyfit(
                    x[-len(lower_points.dropna()):],
                    lower_points.dropna().values, 1
                )
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Contracting condition: trendlines converging
    range_size = upper_trend - lower_trend
    range_trend = range_size.pct_change(period).fillna(0)

    contracting_condition = range_trend < -0.05  # Range decreasing significantly

    # Price within contracting boundaries
    price_in_pattern = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    contracting_signal = (contracting_condition & price_in_pattern).astype(int)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": contracting_signal,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = contracting_signal
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def advanced_flag_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    flag_type: str = "bullish",
    period: int = 20,
    inplace: bool = False,
    prefix: str = "ADV_FLAG",
) -> pd.DataFrame | pd.Series:
    """Advanced Flag Pattern Detection with pole and flag analysis."""

    selection = select_series(data, column)

    # Flag patterns consist of:
    # 1. Flagpole: strong directional move
    # 2. Flag: consolidation in opposite direction

    # Detect flagpole
    returns = selection.series.pct_change().fillna(0)
    flagpole_signal = pd.Series(0, index=selection.series.index)

    if flag_type == "bullish":
        # Bullish flagpole: strong upward move
        flagpole_signal = (selection.series > selection.series.shift(period) * 1.05).astype(int)
    else:
        # Bearish flagpole: strong downward move
        flagpole_signal = (selection.series < selection.series.shift(period) * 0.95).astype(int)

    # Detect flag consolidation
    flag_consolidation = pd.Series(0, index=selection.series.index)

    for i in range(period, len(selection.series)):
        if flagpole_signal.iloc[i-period:i].sum() > 0:  # Flagpole detected
            # Check for consolidation after flagpole
            consolidation_window = selection.series.iloc[i-period:i]

            # Consolidation should be narrow range compared to flagpole
            consolidation_range = consolidation_window.max() - consolidation_window.min()
            flagpole_range = abs(selection.series.iloc[i-period] - selection.series.iloc[i-2*period])

            if flagpole_range > 0:
                range_ratio = consolidation_range / flagpole_range
                if range_ratio < 0.5:  # Consolidation is much smaller than flagpole
                    flag_consolidation.iloc[i] = 1

    # Complete flag pattern
    flag_pattern = (flagpole_signal.rolling(window=period).max() > 0) & flag_consolidation

    # Pattern completion (breakout from flag)
    flag_breakout = pd.Series(0, index=selection.series.index)
    breakout_direction = pd.Series(0, index=selection.series.index)

    for i in range(1, len(selection.series)):
        if flag_pattern.iloc[i-1] == 1 and flag_pattern.iloc[i] == 0:
            # Determine breakout direction
            if flag_type == "bullish":
                breakout_direction.iloc[i] = 1  # Continue upward
            else:
                breakout_direction.iloc[i] = -1  # Continue downward
            flag_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_{flag_type}": flag_pattern.astype(int),
            f"{prefix}_breakout": flag_breakout,
            f"{prefix}_breakout_dir": breakout_direction,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_{flag_type}"] = flag_pattern.astype(int)
    target[f"{prefix}_breakout"] = flag_breakout
    target[f"{prefix}_breakout_dir"] = breakout_direction
    return target


def pennant_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 18,
    inplace: bool = False,
    prefix: str = "PENNANT",
) -> pd.DataFrame | pd.Series:
    """Pennant Pattern Detection."""

    selection = select_series(data, column)

    # Pennant is similar to flag but triangular consolidation
    # Flagpole followed by small symmetrical triangle

    # Detect flagpole (same as flag pattern)
    flagpole_signal = (abs(selection.series - selection.series.shift(period)) / selection.series.shift(period) > 0.03).astype(int)

    # Detect pennant (small symmetrical triangle)
    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            try:
                upper_slope, upper_intercept = np.polyfit(x[-len(upper_points.dropna()):], upper_points.dropna().values, 1)
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            try:
                lower_slope, lower_intercept = np.polyfit(x[-len(lower_points.dropna()):], lower_points.dropna().values, 1)
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Pennant condition: converging trendlines after flagpole
    range_size = upper_trend - lower_trend
    range_trend = range_size.pct_change(period).fillna(0)

    pennant_condition = (range_trend < -0.03) & (flagpole_signal.rolling(window=period).sum() > 0)
    price_in_pennant = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    pennant_signal = (pennant_condition & price_in_pennant).astype(int)

    # Pattern completion (breakout from pennant)
    pennant_breakout = pd.Series(0, index=selection.series.index)

    for i in range(1, len(selection.series)):
        if pennant_signal.iloc[i-1] == 1 and pennant_signal.iloc[i] == 0:
            pennant_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": pennant_signal,
            f"{prefix}_breakout": pennant_breakout,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = pennant_signal
    target[f"{prefix}_breakout"] = pennant_breakout
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def inverse_head_shoulders(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    lookback: int = 100,
    tolerance: float = 0.05,
    inplace: bool = False,
    prefix: str = "INV_HS",
) -> pd.DataFrame:
    """Inverse Head and Shoulders Pattern Detection."""

    require_columns(data, (high, low, close))

    # Find local minima (potential shoulders and head)
    local_min = (data[low] == data[low].rolling(window=5, center=True).min())

    # Find local maxima (neckline)
    local_max = (data[high] == data[high].rolling(window=5, center=True).max())

    # Extract trough values
    troughs = data[low][local_min]
    peaks = data[high][local_max]

    # Initialize pattern signals
    inv_hs_signal = pd.Series(0, index=data.index)

    # Look for inverse H&S pattern within lookback window
    for i in range(lookback, len(data)):
        window_troughs = troughs.iloc[i-lookback:i]
        window_peaks = peaks.iloc[i-lookback:i]

        if len(window_troughs) >= 3 and len(window_peaks) >= 2:
            # Sort troughs by value (ascending - lowest first)
            sorted_troughs = window_troughs.sort_values(ascending=True)

            if len(sorted_troughs) >= 3:
                # Check for inverse head and shoulders structure
                head = sorted_troughs.iloc[0]  # Lowest trough
                shoulder1 = sorted_troughs.iloc[1]  # Second lowest
                shoulder2 = sorted_troughs.iloc[2]  # Third lowest

                # Head should be significantly lower than shoulders
                head_vs_shoulders = (head < shoulder1 * (1 - tolerance)) and (head < shoulder2 * (1 - tolerance))

                # Shoulders should be similar height
                shoulders_similar = abs(shoulder1 - shoulder2) / max(shoulder1, shoulder2) < tolerance

                # Check neckline (highest peaks)
                neckline_level = window_peaks.max()

                # Pattern completion check
                if head_vs_shoulders and shoulders_similar:
                    # Mark the pattern completion point
                    inv_hs_signal.iloc[i] = 1

    target = data if inplace else data.copy()
    target[f"{prefix}_pattern"] = inv_hs_signal
    target[f"{prefix}_strength"] = inv_hs_signal.rolling(window=20).sum()
    return target


def rounding_patterns(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 50,
    inplace: bool = False,
    prefix: str = "ROUNDING",
) -> pd.DataFrame | pd.Series:
    """Rounding Pattern Detection (Cup and Handle, Saucer)."""

    selection = select_series(data, column)

    # Rounding patterns are U-shaped formations
    # Price gradually declines then recovers

    # Calculate smoothed price for pattern recognition
    smoothed_price = selection.series.rolling(window=10).mean()

    # Find the lowest point in the period
    lowest_point = smoothed_price.rolling(window=period).min()
    lowest_idx = smoothed_price.rolling(window=period).idxmin()

    # Calculate symmetry around the lowest point
    rounding_signal = pd.Series(0, index=selection.series.index)

    for i in range(period, len(selection.series)):
        window = smoothed_price.iloc[i-period:i]

        if len(window) >= period//2:
            # Check if the pattern resembles a rounded bottom
            left_side = window.iloc[:period//2]
            right_side = window.iloc[period//2:]

            # Both sides should be relatively smooth and symmetrical
            left_volatility = left_side.std() / left_side.mean()
            right_volatility = right_side.std() / right_side.mean()

            # Low volatility indicates smooth rounding
            symmetry = abs(left_volatility - right_volatility) < 0.02

            # Price should recover significantly after the low
            recovery = (window.iloc[-1] - window.min()) / window.min() > 0.05

            if symmetry and recovery:
                rounding_signal.iloc[i] = 1

    # Volume confirmation (higher volume on the right side)
    volume_confirm = pd.Series(True, index=selection.series.index)
    if isinstance(selection.data, pd.DataFrame) and "volume" in selection.data.columns:
        volume_trend = selection.data["volume"].rolling(window=period).mean()
        volume_confirm = selection.data["volume"] > volume_trend

    rounding_signal = (rounding_signal & volume_confirm).astype(int)

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": rounding_signal,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = rounding_signal
    return target


def ascending_channel(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 30,
    inplace: bool = False,
    prefix: str = "ASC_CHANNEL",
) -> pd.DataFrame | pd.Series:
    """Ascending Channel Pattern Detection."""

    selection = select_series(data, column)

    # Ascending channel: parallel upward sloping trendlines
    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            try:
                upper_slope, upper_intercept = np.polyfit(
                    x[-len(upper_points.dropna()):],
                    upper_points.dropna().values, 1
                )
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            try:
                lower_slope, lower_intercept = np.polyfit(
                    x[-len(lower_points.dropna()):],
                    lower_points.dropna().values, 1
                )
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Ascending channel condition: both trendlines rising, roughly parallel
    upper_slope = upper_trend.diff(period).fillna(0)
    lower_slope = lower_trend.diff(period).fillna(0)

    parallel_condition = abs(upper_slope - lower_slope) / np.maximum(abs(upper_slope), abs(lower_slope)).replace(0, 1) < 0.3
    ascending_condition = (upper_slope > 0) & (lower_slope > 0) & parallel_condition

    # Price within channel boundaries
    price_in_channel = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    channel_signal = (ascending_condition & price_in_channel).astype(int)

    # Pattern completion (breakout from channel)
    channel_breakout = pd.Series(0, index=selection.series.index)

    for i in range(1, len(selection.series)):
        if channel_signal.iloc[i-1] == 1 and channel_signal.iloc[i] == 0:
            channel_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": channel_signal,
            f"{prefix}_breakout": channel_breakout,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = channel_signal
    target[f"{prefix}_breakout"] = channel_breakout
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


def descending_channel(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 30,
    inplace: bool = False,
    prefix: str = "DESC_CHANNEL",
) -> pd.DataFrame | pd.Series:
    """Descending Channel Pattern Detection."""

    selection = select_series(data, column)

    # Descending channel: parallel downward sloping trendlines
    upper_trend = pd.Series(index=selection.series.index, dtype=float)
    lower_trend = pd.Series(index=selection.series.index, dtype=float)

    for i in range(period, len(selection.series)):
        window = selection.series.iloc[i-period:i]
        x = np.arange(len(window))

        # Upper trendline
        upper_points = window.rolling(window=3, center=True).max()
        if len(upper_points.dropna()) >= 3:
            try:
                upper_slope, upper_intercept = np.polyfit(
                    x[-len(upper_points.dropna()):],
                    upper_points.dropna().values, 1
                )
                upper_trend.iloc[i] = upper_intercept + upper_slope * (period - 1)
            except:
                upper_trend.iloc[i] = upper_points.iloc[-1]

        # Lower trendline
        lower_points = window.rolling(window=3, center=True).min()
        if len(lower_points.dropna()) >= 3:
            try:
                lower_slope, lower_intercept = np.polyfit(
                    x[-len(lower_points.dropna()):],
                    lower_points.dropna().values, 1
                )
                lower_trend.iloc[i] = lower_intercept + lower_slope * (period - 1)
            except:
                lower_trend.iloc[i] = lower_points.iloc[-1]

    # Descending channel condition: both trendlines falling, roughly parallel
    upper_slope = upper_trend.diff(period).fillna(0)
    lower_slope = lower_trend.diff(period).fillna(0)

    parallel_condition = abs(upper_slope - lower_slope) / np.maximum(abs(upper_slope), abs(lower_slope)).replace(0, 1) < 0.3
    descending_condition = (upper_slope < 0) & (lower_slope < 0) & parallel_condition

    # Price within channel boundaries
    price_in_channel = (selection.series <= upper_trend) & (selection.series >= lower_trend)

    channel_signal = (descending_condition & price_in_channel).astype(int)

    # Pattern completion (breakout from channel)
    channel_breakout = pd.Series(0, index=selection.series.index)

    for i in range(1, len(selection.series)):
        if channel_signal.iloc[i-1] == 1 and channel_signal.iloc[i] == 0:
            channel_breakout.iloc[i] = 1

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_pattern": channel_signal,
            f"{prefix}_breakout": channel_breakout,
            f"{prefix}_upper_trend": upper_trend,
            f"{prefix}_lower_trend": lower_trend,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_pattern"] = channel_signal
    target[f"{prefix}_breakout"] = channel_breakout
    target[f"{prefix}_upper_trend"] = upper_trend
    target[f"{prefix}_lower_trend"] = lower_trend
    return target


# =============================================================================
# MACHINE LEARNING-BASED SIGNAL GENERATION
# =============================================================================

def clustering_market_regime_signals(
    data: pd.DataFrame,
    *,
    features: List[str] = None,
    n_clusters: int = 3,
    method: str = "kmeans",
    lookback: int = 252,
    inplace: bool = False,
    prefix: str = "CLUSTER_REGIME",
) -> pd.DataFrame:
    """ML-based market regime detection using clustering algorithms."""

    try:
        from sklearn.cluster import KMeans, DBSCAN
        from sklearn.mixture import GaussianMixture
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn is required for ML-based signals")

    # Default features if not provided
    if features is None:
        features = ["close", "volume"] if "volume" in data.columns else ["close"]

    require_columns(data, features)

    # Create feature matrix
    feature_data = data[features].copy()

    # Add technical indicators as features
    if len(data) > 50:
        try:
            feature_data["returns"] = data["close"].pct_change().fillna(0)
            feature_data["volatility"] = data["close"].pct_change().rolling(20).std().fillna(0)
            feature_data["momentum"] = data["close"] / data["close"].shift(20).fillna(data["close"])
            feature_data["rsi"] = rsi(data, period=14)["RSI_14"].fillna(50)
            feature_data["macd"] = macd(data)["MACD_12_26_9"].fillna(0)
        except:
            pass  # Skip if indicators fail

    # Prepare data for clustering
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_data.fillna(0))

    # Initialize regime signals
    regime_signal = pd.Series(0, index=data.index)
    regime_probability = pd.Series(0.0, index=data.index)
    regime_change = pd.Series(0, index=data.index)

    # Apply clustering for each lookback window
    for i in range(lookback, len(data)):
        window_data = scaled_features[i-lookback:i]

        # Apply clustering algorithm
        if method == "kmeans":
            cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif method == "dbscan":
            cluster_model = DBSCAN(eps=0.5, min_samples=5)
        elif method == "gmm":
            cluster_model = GaussianMixture(n_components=n_clusters, random_state=42)
        else:
            raise ValueError("Method must be 'kmeans', 'dbscan', or 'gmm'")

        try:
            if method == "gmm":
                labels = cluster_model.fit_predict(window_data)
                probabilities = cluster_model.predict_proba(window_data[-1].reshape(1, -1))[0]
                regime_probability.iloc[i] = max(probabilities)
            else:
                labels = cluster_model.fit_predict(window_data)

            # Current regime is the cluster of the most recent point
            current_regime = labels[-1]
            regime_signal.iloc[i] = current_regime

            # Detect regime changes
            if i > lookback and regime_signal.iloc[i-1] != current_regime:
                regime_change.iloc[i] = 1

        except:
            # Skip clustering if it fails
            continue

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = regime_signal
    target[f"{prefix}_change"] = regime_change
    target[f"{prefix}_probability"] = regime_probability
    return target


def autoencoder_anomaly_signals(
    data: pd.DataFrame,
    *,
    features: List[str] = None,
    encoding_dim: int = 8,
    threshold_percentile: float = 95,
    lookback: int = 252,
    inplace: bool = False,
    prefix: str = "AUTOENCODER_ANOMALY",
) -> pd.DataFrame:
    """Autoencoder-based anomaly detection for signal generation."""

    try:
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Dense
        from tensorflow.keras.optimizers import Adam
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow warnings
    except ImportError:
        raise ImportError("tensorflow is required for autoencoder signals")

    # Default features
    if features is None:
        features = ["close", "volume"] if "volume" in data.columns else ["close"]

    require_columns(data, features)

    # Create feature matrix
    feature_data = data[features].copy()

    # Add technical features
    if len(data) > 50:
        try:
            feature_data["returns"] = data["close"].pct_change().fillna(0)
            feature_data["volatility"] = data["close"].pct_change().rolling(20).std().fillna(0)
            feature_data["rsi"] = rsi(data, period=14)["RSI_14"].fillna(50)
            feature_data["bb_upper"] = bollinger_bands(data)["BBU_20_2.0"]
            feature_data["bb_lower"] = bollinger_bands(data)["BBL_20_2.0"]
        except:
            pass

    # Scale features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_data.fillna(0))

    # Build autoencoder
    input_dim = scaled_features.shape[1]
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(encoding_dim, activation='relu')(input_layer)
    decoded = Dense(input_dim, activation='linear')(encoded)

    autoencoder = Model(input_layer, decoded)
    autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    # Train autoencoder
    try:
        autoencoder.fit(
            scaled_features[:lookback],
            scaled_features[:lookback],
            epochs=50,
            batch_size=32,
            verbose=0
        )

        # Calculate reconstruction errors
        reconstructed = autoencoder.predict(scaled_features, verbose=0)
        reconstruction_errors = np.mean((scaled_features - reconstructed) ** 2, axis=1)

        # Normalize errors
        normalized_errors = (reconstruction_errors - np.mean(reconstruction_errors)) / np.std(reconstruction_errors)

        # Anomaly threshold
        threshold = np.percentile(normalized_errors, threshold_percentile)

        # Generate signals
        anomaly_signal = (normalized_errors > threshold).astype(int)

    except:
        # Fallback if training fails
        anomaly_signal = pd.Series(0, index=data.index)
        normalized_errors = pd.Series(0.0, index=data.index)

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = anomaly_signal
    target[f"{prefix}_score"] = normalized_errors
    target[f"{prefix}_threshold"] = threshold if 'threshold' in locals() else 0
    return target


def lstm_price_prediction_signals(
    data: pd.DataFrame,
    *,
    lookback: int = 60,
    prediction_horizon: int = 5,
    n_features: int = None,
    inplace: bool = False,
    prefix: str = "LSTM_PREDICT",
) -> pd.DataFrame:
    """LSTM-based price prediction signals."""

    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        raise ImportError("tensorflow is required for LSTM signals")

    # Prepare data
    prices = data["close"].values.reshape(-1, 1)

    # Create features
    features = []
    if n_features is None:
        n_features = min(10, len(data.columns))

    feature_cols = data.select_dtypes(include=[np.number]).columns[:n_features]
    feature_data = data[feature_cols].fillna(0).values

    # Normalize data
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(feature_data)

    # Create sequences for LSTM
    def create_sequences(data, lookback, horizon):
        X, y = [], []
        for i in range(len(data) - lookback - horizon + 1):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback:i+lookback+horizon, 0])  # Predict close price
        return np.array(X), np.array(y)

    X, y = create_sequences(scaled_features, lookback, prediction_horizon)

    if len(X) < 50:  # Not enough data
        prediction_signal = pd.Series(0, index=data.index)
        confidence = pd.Series(0.0, index=data.index)
    else:
        # Build LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(lookback, X.shape[2])),
            Dropout(0.2),
            LSTM(30, return_sequences=False),
            Dropout(0.2),
            Dense(prediction_horizon)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

        # Train model
        try:
            model.fit(X, y, epochs=20, batch_size=32, verbose=0, validation_split=0.1)

            # Generate predictions
            predictions = []
            confidence_scores = []

            for i in range(lookback, len(scaled_features) - prediction_horizon + 1):
                seq = scaled_features[i-lookback:i].reshape(1, lookback, -1)
                pred = model.predict(seq, verbose=0)[0]
                predictions.append(pred[-1])  # Last prediction

                # Calculate confidence based on prediction variance
                pred_std = np.std(pred)
                confidence_scores.append(1.0 / (1.0 + pred_std))

            # Create signal series
            prediction_signal = pd.Series(0, index=data.index)
            confidence = pd.Series(0.0, index=data.index)

            pred_idx = 0
            for i in range(lookback, len(data) - prediction_horizon + 1):
                if pred_idx < len(predictions):
                    current_price = data["close"].iloc[i]
                    predicted_price = scaler.inverse_transform(
                        np.column_stack([predictions[pred_idx]] + [scaled_features[i, 1:]] * (scaled_features.shape[1]-1))
                    )[0, 0]

                    # Generate signal based on prediction
                    if predicted_price > current_price * 1.02:  # Bullish prediction
                        prediction_signal.iloc[i] = 1
                    elif predicted_price < current_price * 0.98:  # Bearish prediction
                        prediction_signal.iloc[i] = -1

                    confidence.iloc[i] = confidence_scores[pred_idx]
                    pred_idx += 1

        except:
            prediction_signal = pd.Series(0, index=data.index)
            confidence = pd.Series(0.0, index=data.index)

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = prediction_signal
    target[f"{prefix}_confidence"] = confidence
    return target


def reinforcement_learning_signals(
    data: pd.DataFrame,
    *,
    features: List[str] = None,
    n_actions: int = 3,  # -1: sell, 0: hold, 1: buy
    learning_rate: float = 0.1,
    discount_factor: float = 0.95,
    epsilon: float = 0.1,
    inplace: bool = False,
    prefix: str = "RL_SIGNAL",
) -> pd.DataFrame:
    """Reinforcement learning-based signal generation using Q-learning."""

    try:
        import numpy as np
    except ImportError:
        raise ImportError("numpy is required for RL signals")

    if features is None:
        features = ["close", "volume"] if "volume" in data.columns else ["close"]

    require_columns(data, features)

    # Discretize features for Q-table
    def discretize_features(data, n_bins=10):
        discretized = {}
        for col in features:
            values = data[col].fillna(data[col].mean())
            discretized[col] = pd.qcut(values, n_bins, labels=False, duplicates='drop')
        return discretized

    disc_features = discretize_features(data)

    # Initialize Q-table
    state_space_size = 10 ** len(features)  # Assuming 10 bins per feature
    q_table = np.zeros((state_space_size, n_actions))

    # Calculate returns for rewards
    returns = data["close"].pct_change().fillna(0)

    # Training phase
    for i in range(1, len(data)):
        # Create state representation
        state = 0
        for j, col in enumerate(features):
            state += disc_features[col].iloc[i] * (10 ** j)

        # Choose action (epsilon-greedy)
        if np.random.random() < epsilon:
            action = np.random.randint(n_actions)
        else:
            action = np.argmax(q_table[state])

        # Calculate reward
        reward = returns.iloc[i] * 100  # Scale returns

        # Update Q-table
        next_state = min(state, state_space_size - 1)
        q_table[state, action] = q_table[state, action] + learning_rate * (
            reward + discount_factor * np.max(q_table[next_state]) - q_table[state, action]
        )

    # Generate signals based on learned Q-values
    signal = pd.Series(0, index=data.index)
    confidence = pd.Series(0.0, index=data.index)

    for i in range(len(data)):
        state = 0
        for j, col in enumerate(features):
            state += disc_features[col].iloc[i] * (10 ** j)

        # Get best action
        best_action = np.argmax(q_table[state])
        confidence_score = np.max(q_table[state]) / np.sum(q_table[state]) if np.sum(q_table[state]) > 0 else 0

        # Convert action to signal (-1, 0, 1)
        if n_actions == 3:
            signal.iloc[i] = best_action - 1  # 0->-1, 1->0, 2->1
        else:
            signal.iloc[i] = best_action

        confidence.iloc[i] = confidence_score

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = signal
    target[f"{prefix}_confidence"] = confidence
    return target


def neural_network_regime_classifier(
    data: pd.DataFrame,
    *,
    features: List[str] = None,
    n_regimes: int = 3,
    lookback: int = 100,
    inplace: bool = False,
    prefix: str = "NN_REGIME",
) -> pd.DataFrame:
    """Neural network-based market regime classification."""

    try:
        from sklearn.neural_network import MLPClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.model_selection import train_test_split
    except ImportError:
        raise ImportError("scikit-learn is required for neural network signals")

    if features is None:
        features = ["close", "volume"] if "volume" in data.columns else ["close"]

    require_columns(data, features)

    # Create comprehensive feature set
    feature_data = data[features].copy()

    # Add technical indicators
    if len(data) > 50:
        try:
            feature_data["returns"] = data["close"].pct_change().fillna(0)
            feature_data["volatility"] = data["close"].pct_change().rolling(20).std().fillna(0)
            feature_data["momentum"] = data["close"] / data["close"].shift(20).fillna(data["close"])
            feature_data["rsi"] = rsi(data, period=14)["RSI_14"].fillna(50)
            feature_data["macd"] = macd(data)["MACD_12_26_9"].fillna(0)
            feature_data["bb_position"] = (data["close"] - bollinger_bands(data)["BBL_20_2.0"]) / (bollinger_bands(data)["BBU_20_2.0"] - bollinger_bands(data)["BBL_20_2.0"]).fillna(0)
        except:
            pass

    # Create regime labels based on volatility and trend
    volatility = data["close"].pct_change().rolling(20).std().fillna(0)
    trend = data["close"].pct_change(20).fillna(0)

    # Simple regime classification
    regimes = pd.Series(0, index=data.index)
    for i in range(len(data)):
        if volatility.iloc[i] > volatility.quantile(0.75):
            regimes.iloc[i] = 2  # High volatility
        elif trend.iloc[i] > 0.05:
            regimes.iloc[i] = 1  # Bullish trend
        else:
            regimes.iloc[i] = 0  # Normal/low volatility

    # Prepare training data
    X = feature_data.fillna(0).values
    y = regimes.values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train neural network
    nn_model = MLPClassifier(
        hidden_layer_sizes=(50, 25),
        activation='relu',
        solver='adam',
        alpha=0.001,
        max_iter=500,
        random_state=42
    )

    try:
        # Split data for training
        if len(X_scaled) > lookback:
            X_train = X_scaled[:-lookback]
            y_train = y[:-lookback]
            X_test = X_scaled[-lookback:]
            y_test = y[-lookback:]

            nn_model.fit(X_train, y_train)

            # Predict regimes
            regime_predictions = nn_model.predict(X_scaled)
            regime_probabilities = nn_model.predict_proba(X_scaled)
        else:
            regime_predictions = np.zeros(len(data))
            regime_probabilities = np.zeros((len(data), n_regimes))
    except:
        regime_predictions = np.zeros(len(data))
        regime_probabilities = np.zeros((len(data), n_regimes))

    # Convert to series
    regime_signal = pd.Series(regime_predictions, index=data.index)
    regime_confidence = pd.Series(np.max(regime_probabilities, axis=1), index=data.index)

    # Detect regime changes
    regime_change = pd.Series(0, index=data.index)
    for i in range(1, len(regime_signal)):
        if regime_signal.iloc[i] != regime_signal.iloc[i-1]:
            regime_change.iloc[i] = 1

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = regime_signal
    target[f"{prefix}_confidence"] = regime_confidence
    target[f"{prefix}_change"] = regime_change
    return target


def ensemble_ml_signals(
    data: pd.DataFrame,
    *,
    signal_functions: List[callable] = None,
    weights: List[float] = None,
    threshold: float = 0.6,
    inplace: bool = False,
    prefix: str = "ENSEMBLE_ML",
) -> pd.DataFrame:
    """Ensemble ML signal combination from multiple ML models."""

    if signal_functions is None:
        signal_functions = [
            lambda d: clustering_market_regime_signals(d, prefix="CLUSTER"),
            lambda d: neural_network_regime_classifier(d, prefix="NN"),
            lambda d: reinforcement_learning_signals(d, prefix="RL"),
        ]

    if weights is None:
        weights = [1.0 / len(signal_functions)] * len(signal_functions)

    # Generate signals from each model
    individual_signals = []
    individual_confidences = []

    for func in signal_functions:
        try:
            result = func(data)
            # Extract signal and confidence columns
            signal_col = [col for col in result.columns if col.endswith('_signal')][0]
            conf_col = [col for col in result.columns if col.endswith('_confidence')][0]

            individual_signals.append(result[signal_col])
            individual_confidences.append(result[conf_col])
        except:
            # Fallback if a model fails
            individual_signals.append(pd.Series(0, index=data.index))
            individual_confidences.append(pd.Series(0.5, index=data.index))

    # Combine signals using weighted voting
    combined_signal = pd.Series(0, index=data.index)
    combined_confidence = pd.Series(0.0, index=data.index)

    for i in range(len(data)):
        signals_at_i = [sig.iloc[i] for sig in individual_signals]
        confidences_at_i = [conf.iloc[i] for conf in individual_confidences]

        # Weighted average signal
        weighted_signal = sum(s * w for s, w in zip(signals_at_i, weights))

        # Combined confidence
        avg_confidence = sum(confidences_at_i) / len(confidences_at_i)

        combined_signal.iloc[i] = 1 if weighted_signal > threshold else (-1 if weighted_signal < -threshold else 0)
        combined_confidence.iloc[i] = avg_confidence

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = combined_signal
    target[f"{prefix}_confidence"] = combined_confidence
    target[f"{prefix}_raw_signal"] = combined_signal  # Unfiltered signal
    return target


def feature_importance_signals(
    data: pd.DataFrame,
    *,
    target_feature: str = "close",
    prediction_horizon: int = 5,
    n_features: int = 20,
    inplace: bool = False,
    prefix: str = "FEATURE_IMPORTANCE",
) -> pd.DataFrame:
    """ML feature importance-based signal generation."""

    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.feature_selection import SelectKBest, f_regression
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn is required for feature importance signals")

    # Create comprehensive feature set
    features = {}
    feature_names = []

    # Price-based features
    for lag in [1, 5, 10, 20]:
        features[f"close_lag_{lag}"] = data["close"].shift(lag).fillna(data["close"])
        feature_names.append(f"close_lag_{lag}")

    # Technical indicators
    if len(data) > 50:
        try:
            rsi_data = rsi(data, period=14)
            features["rsi"] = rsi_data["RSI_14"]
            feature_names.append("rsi")

            macd_data = macd(data)
            features["macd"] = macd_data["MACD_12_26_9"]
            features["macd_signal"] = macd_data["MACDs_12_26_9"]
            feature_names.extend(["macd", "macd_signal"])

            bb_data = bollinger_bands(data)
            features["bb_position"] = (data["close"] - bb_data["BBL_20_2.0"]) / (bb_data["BBU_20_2.0"] - bb_data["BBL_20_2.0"])
            feature_names.append("bb_position")
        except:
            pass

    # Volume features
    if "volume" in data.columns:
        features["volume"] = data["volume"]
        features["volume_change"] = data["volume"].pct_change().fillna(0)
        feature_names.extend(["volume", "volume_change"])

    # Create feature matrix
    feature_df = pd.DataFrame(features)
    feature_df = feature_df.fillna(0)

    # Create target (future price movement)
    future_price = data[target_feature].shift(-prediction_horizon)
    target = ((future_price - data[target_feature]) / data[target_feature]).fillna(0)

    # Remove NaN rows
    valid_idx = ~(feature_df.isna().any(axis=1) | target.isna())
    X = feature_df[valid_idx].values
    y = target[valid_idx].values

    if len(X) < 50:  # Not enough data
        importance_signal = pd.Series(0, index=data.index)
        importance_score = pd.Series(0.0, index=data.index)
    else:
        # Train random forest for feature importance
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)

        # Get feature importances
        importances = rf_model.feature_importances_

        # Create importance-based signals
        importance_signal = pd.Series(0, index=data.index)
        importance_score = pd.Series(0.0, index=data.index)

        # For each data point, calculate importance-weighted prediction
        for i in range(len(feature_df)):
            if valid_idx.iloc[i]:
                # Get prediction and importance score
                prediction = rf_model.predict(X[valid_idx.cumsum().iloc[i] - 1].reshape(1, -1))[0]

                # Weighted importance score
                importance_score.iloc[i] = sum(importances * np.abs(X[valid_idx.cumsum().iloc[i] - 1]))

                # Generate signal based on prediction
                if prediction > 0.02:  # Bullish prediction
                    importance_signal.iloc[i] = 1
                elif prediction < -0.02:  # Bearish prediction
                    importance_signal.iloc[i] = -1

    target_df = data if inplace else data.copy()
    target_df[f"{prefix}_signal"] = importance_signal
    target_df[f"{prefix}_score"] = importance_score
    return target_df


def anomaly_detection_signals(
    data: pd.DataFrame,
    *,
    method: str = "isolation_forest",
    features: List[str] = None,
    contamination: float = 0.1,
    inplace: bool = False,
    prefix: str = "ANOMALY_DETECT",
) -> pd.DataFrame:
    """Multiple anomaly detection methods for signal generation."""

    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        from sklearn.svm import OneClassSVM
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn is required for anomaly detection signals")

    if features is None:
        features = ["close", "volume"] if "volume" in data.columns else ["close"]

    require_columns(data, features)

    # Create feature matrix
    feature_data = data[features].copy()

    # Add technical features
    if len(data) > 50:
        try:
            feature_data["returns"] = data["close"].pct_change().fillna(0)
            feature_data["volatility"] = data["close"].pct_change().rolling(20).std().fillna(0)
            feature_data["rsi"] = rsi(data, period=14)["RSI_14"].fillna(50)
            feature_data["momentum"] = data["close"] / data["close"].shift(20).fillna(data["close"])
        except:
            pass

    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_data.fillna(0))

    # Apply anomaly detection
    if method == "isolation_forest":
        detector = IsolationForest(contamination=contamination, random_state=42)
        anomaly_scores = detector.fit_predict(scaled_features)
        anomaly_scores = (anomaly_scores == -1).astype(int)  # Convert to 0/1

    elif method == "local_outlier_factor":
        detector = LocalOutlierFactor(contamination=contamination, n_neighbors=20)
        anomaly_scores = detector.fit_predict(scaled_features)
        anomaly_scores = (anomaly_scores == -1).astype(int)

    elif method == "one_class_svm":
        detector = OneClassSVM(nu=contamination, kernel="rbf", gamma="auto")
        anomaly_scores = detector.fit_predict(scaled_features)
        anomaly_scores = (anomaly_scores == -1).astype(int)

    else:
        raise ValueError("Method must be 'isolation_forest', 'local_outlier_factor', or 'one_class_svm'")

    # Calculate anomaly scores/probabilities
    if hasattr(detector, 'decision_function'):
        anomaly_probabilities = detector.decision_function(scaled_features)
        # Normalize to 0-1 scale
        anomaly_probabilities = (anomaly_probabilities - anomaly_probabilities.min()) / (anomaly_probabilities.max() - anomaly_probabilities.min())
    else:
        anomaly_probabilities = pd.Series(0.5, index=data.index)

    # Convert to series
    anomaly_signal = pd.Series(anomaly_scores, index=data.index)
    anomaly_probability = pd.Series(anomaly_probabilities, index=data.index)

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = anomaly_signal
    target[f"{prefix}_probability"] = anomaly_probability
    return target


def time_series_forecast_signals(
    data: pd.DataFrame,
    *,
    model_type: str = "arima",
    forecast_horizon: int = 5,
    confidence_threshold: float = 0.8,
    inplace: bool = False,
    prefix: str = "TS_FORECAST",
) -> pd.DataFrame:
    """Time series forecasting-based signal generation."""

    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        from sklearn.metrics import mean_squared_error
    except ImportError:
        raise ImportError("statsmodels is required for time series forecasting")

    prices = data["close"].fillna(method='ffill').fillna(0)

    if len(prices) < 50:
        forecast_signal = pd.Series(0, index=data.index)
        forecast_confidence = pd.Series(0.0, index=data.index)
    else:
        # Rolling forecast
        forecast_signal = pd.Series(0, index=data.index)
        forecast_confidence = pd.Series(0.0, index=data.index)

        min_train_size = 30

        for i in range(min_train_size, len(prices) - forecast_horizon):
            try:
                # Training data
                train_data = prices.iloc[i-min_train_size:i]

                # Fit model
                if model_type == "arima":
                    model = ARIMA(train_data, order=(5, 1, 0))
                elif model_type == "sarima":
                    model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                else:
                    raise ValueError("model_type must be 'arima' or 'sarima'")

                fitted_model = model.fit(disp=False)

                # Forecast
                forecast = fitted_model.forecast(steps=forecast_horizon)

                # Calculate forecast confidence
                current_price = prices.iloc[i]
                forecasted_price = forecast.iloc[-1]

                # Simple confidence based on forecast vs current price ratio
                price_ratio = abs(forecasted_price - current_price) / current_price
                confidence = max(0, 1 - price_ratio)  # Higher confidence for smaller changes

                # Generate signal
                if confidence > confidence_threshold:
                    if forecasted_price > current_price * 1.01:
                        forecast_signal.iloc[i] = 1  # Bullish
                    elif forecasted_price < current_price * 0.99:
                        forecast_signal.iloc[i] = -1  # Bearish

                forecast_confidence.iloc[i] = confidence

            except:
                # Skip if forecasting fails
                continue

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = forecast_signal
    target[f"{prefix}_confidence"] = forecast_confidence
    return target


# =============================================================================
# RISK MANAGEMENT SIGNALS
# =============================================================================

def value_at_risk_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    confidence_level: float = 0.95,
    method: str = "historical",
    lookback: int = 252,
    position_size: float = 1.0,
    inplace: bool = False,
    prefix: str = "VAR",
) -> pd.DataFrame | pd.Series:
    """Value at Risk (VaR) based risk signals."""

    try:
        from scipy import stats
    except ImportError:
        raise ImportError("scipy is required for VaR calculations")

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    if len(returns) < lookback:
        var_signal = pd.Series(0, index=selection.series.index)
        var_value = pd.Series(0.0, index=selection.series.index)
        breach_signal = pd.Series(0, index=selection.series.index)
    else:
        var_signal = pd.Series(0, index=selection.series.index)
        var_value = pd.Series(0.0, index=selection.series.index)
        breach_signal = pd.Series(0, index=selection.series.index)

        for i in range(lookback, len(returns)):
            window_returns = returns.iloc[i-lookback:i]

            if method == "historical":
                # Historical VaR
                var = np.percentile(window_returns, (1 - confidence_level) * 100)
            elif method == "parametric":
                # Parametric VaR (assuming normal distribution)
                mean_return = window_returns.mean()
                std_return = window_returns.std()
                z_score = stats.norm.ppf(1 - confidence_level)
                var = mean_return + z_score * std_return
            elif method == "monte_carlo":
                # Monte Carlo VaR
                n_simulations = 1000
                simulated_returns = np.random.normal(
                    window_returns.mean(),
                    window_returns.std(),
                    n_simulations
                )
                var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
            else:
                raise ValueError("Method must be 'historical', 'parametric', or 'monte_carlo'")

            var_value.iloc[i] = abs(var) * position_size

            # Check for VaR breach
            current_return = returns.iloc[i]
            if current_return < var:
                breach_signal.iloc[i] = 1

            # Generate risk signal based on VaR level
            if abs(var) > 0.05:  # High risk
                var_signal.iloc[i] = -2
            elif abs(var) > 0.03:  # Medium risk
                var_signal.iloc[i] = -1
            elif abs(var) > 0.01:  # Low risk
                var_signal.iloc[i] = 1
            else:  # Very low risk
                var_signal.iloc[i] = 2

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_signal": var_signal,
            f"{prefix}_value": var_value,
            f"{prefix}_breach": breach_signal,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_signal"] = var_signal
    target[f"{prefix}_value"] = var_value
    target[f"{prefix}_breach"] = breach_signal
    return target


def drawdown_risk_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    inplace: bool = False,
    prefix: str = "DRAWDOWN",
) -> pd.DataFrame | pd.Series:
    """Drawdown-based risk signals."""

    selection = select_series(data, column)

    # Calculate drawdowns
    cumulative = (1 + selection.series.pct_change().fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max

    # Maximum drawdown
    max_drawdown = drawdown.expanding().min()

    # Drawdown duration
    drawdown_duration = pd.Series(0, index=selection.series.index)
    in_drawdown = False
    duration_count = 0

    for i in range(len(drawdown)):
        if drawdown.iloc[i] < 0:
            if not in_drawdown:
                in_drawdown = True
                duration_count = 1
            else:
                duration_count += 1
        else:
            in_drawdown = False
            duration_count = 0
        drawdown_duration.iloc[i] = duration_count

    # Recovery signals
    recovery_signal = pd.Series(0, index=selection.series.index)

    # Detect when drawdown ends (recovery starts)
    for i in range(1, len(drawdown)):
        if drawdown.iloc[i-1] < 0 and drawdown.iloc[i] >= 0:
            recovery_signal.iloc[i] = 1

    # Drawdown depth categories
    depth_signal = pd.Series(0, index=selection.series.index)
    for i in range(len(drawdown)):
        dd = abs(drawdown.iloc[i])
        if dd > 0.20:  # Severe drawdown
            depth_signal.iloc[i] = -3
        elif dd > 0.10:  # Significant drawdown
            depth_signal.iloc[i] = -2
        elif dd > 0.05:  # Moderate drawdown
            depth_signal.iloc[i] = -1
        elif dd > 0.02:  # Minor drawdown
            depth_signal.iloc[i] = 1
        else:  # No significant drawdown
            depth_signal.iloc[i] = 2

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_depth_signal": depth_signal,
            f"{prefix}_current": drawdown,
            f"{prefix}_max": max_drawdown,
            f"{prefix}_duration": drawdown_duration,
            f"{prefix}_recovery": recovery_signal,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_depth_signal"] = depth_signal
    target[f"{prefix}_current"] = drawdown
    target[f"{prefix}_max"] = max_drawdown
    target[f"{prefix}_duration"] = drawdown_duration
    target[f"{prefix}_recovery"] = recovery_signal
    return target


def volatility_adjusted_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    risk_free_rate: float = 0.02,
    inplace: bool = False,
    prefix: str = "VOL_ADJ",
) -> pd.DataFrame | pd.Series:
    """Volatility-adjusted risk-return signals."""

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    # Rolling volatility (risk)
    volatility = returns.rolling(window=20).std() * np.sqrt(252)  # Annualized

    # Rolling Sharpe ratio
    excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
    rolling_sharpe = excess_returns.rolling(window=60).mean() / volatility

    # Sortino ratio (downside deviation)
    downside_returns = returns[returns < 0]
    downside_volatility = downside_returns.rolling(window=60).std() * np.sqrt(252)
    rolling_sortino = excess_returns.rolling(window=60).mean() / downside_volatility

    # Calmar ratio (return vs max drawdown)
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.expanding().min()

    # Annual return calculation
    annual_return = (cumulative - 1).rolling(window=252).mean()

    # Calmar ratio
    calmar_ratio = pd.Series(0.0, index=selection.series.index)
    valid_idx = (max_dd != 0) & (~np.isinf(max_dd))
    calmar_ratio[valid_idx] = annual_return[valid_idx] / abs(max_dd[valid_idx])

    # Generate signals based on risk-adjusted metrics
    sharpe_signal = pd.Series(0, index=selection.series.index)
    sortino_signal = pd.Series(0, index=selection.series.index)
    calmar_signal = pd.Series(0, index=selection.series.index)

    # Sharpe signal
    sharpe_valid = ~np.isnan(rolling_sharpe)
    sharpe_signal[sharpe_valid & (rolling_sharpe > 2)] = 2  # Excellent
    sharpe_signal[sharpe_valid & (rolling_sharpe > 1)] = 1  # Good
    sharpe_signal[sharpe_valid & (rolling_sharpe < 0)] = -1  # Poor

    # Sortino signal
    sortino_valid = ~np.isnan(rolling_sortino)
    sortino_signal[sortino_valid & (rolling_sortino > 2)] = 2  # Excellent
    sortino_signal[sortino_valid & (rolling_sortino > 1)] = 1  # Good
    sortino_signal[sortino_valid & (rolling_sortino < 0)] = -1  # Poor

    # Calmar signal
    calmar_valid = ~np.isnan(calmar_ratio)
    calmar_signal[calmar_valid & (calmar_ratio > 3)] = 2  # Excellent
    calmar_signal[calmar_valid & (calmar_ratio > 1)] = 1  # Good
    calmar_signal[calmar_valid & (calmar_ratio < 0)] = -1  # Poor

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_sharpe_signal": sharpe_signal,
            f"{prefix}_sharpe_ratio": rolling_sharpe,
            f"{prefix}_sortino_signal": sortino_signal,
            f"{prefix}_sortino_ratio": rolling_sortino,
            f"{prefix}_calmar_signal": calmar_signal,
            f"{prefix}_calmar_ratio": calmar_ratio,
            f"{prefix}_volatility": volatility,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_sharpe_signal"] = sharpe_signal
    target[f"{prefix}_sharpe_ratio"] = rolling_sharpe
    target[f"{prefix}_sortino_signal"] = sortino_signal
    target[f"{prefix}_sortino_ratio"] = rolling_sortino
    target[f"{prefix}_calmar_signal"] = calmar_signal
    target[f"{prefix}_calmar_ratio"] = calmar_ratio
    target[f"{prefix}_volatility"] = volatility
    return target


def kelly_criterion_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    win_rate: Optional[float] = None,
    win_loss_ratio: Optional[float] = None,
    lookback: int = 100,
    inplace: bool = False,
    prefix: str = "KELLY",
) -> pd.DataFrame | pd.Series:
    """Kelly Criterion based position sizing signals."""

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    if win_rate is None or win_loss_ratio is None:
        # Calculate from historical data
        winning_trades = (returns > 0).rolling(window=lookback).sum()
        total_trades = lookback
        win_rate = winning_trades / total_trades

        # Average win/loss ratio
        avg_win = returns[returns > 0].rolling(window=lookback).mean()
        avg_loss = abs(returns[returns < 0].rolling(window=lookback).mean())
        win_loss_ratio = avg_win / avg_loss
        win_loss_ratio = win_loss_ratio.fillna(1.0)

    # Kelly formula: K = (bp - q) / b
    # where b = odds (win_loss_ratio), p = win probability, q = loss probability
    kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # Position size signals
    position_signal = pd.Series(0, index=selection.series.index)

    # Kelly suggests position sizes
    kelly_valid = ~np.isnan(kelly_fraction) & (kelly_fraction > 0)
    position_signal[kelly_valid & (kelly_fraction > 0.10)] = 3  # Aggressive sizing
    position_signal[kelly_valid & (kelly_fraction > 0.05)] = 2  # Moderate sizing
    position_signal[kelly_valid & (kelly_fraction > 0.02)] = 1  # Conservative sizing
    position_signal[kelly_valid & (kelly_fraction <= 0.02)] = -1  # Too risky
    position_signal[~kelly_valid] = -2  # Invalid Kelly

    # Half-Kelly for risk management
    half_kelly = kelly_fraction * 0.5

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_position_signal": position_signal,
            f"{prefix}_fraction": kelly_fraction,
            f"{prefix}_half_fraction": half_kelly,
            f"{prefix}_win_rate": win_rate,
            f"{prefix}_win_loss_ratio": win_loss_ratio,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_position_signal"] = position_signal
    target[f"{prefix}_fraction"] = kelly_fraction
    target[f"{prefix}_half_fraction"] = half_kelly
    target[f"{prefix}_win_rate"] = win_rate
    target[f"{prefix}_win_loss_ratio"] = win_loss_ratio
    return target


def conditional_value_at_risk_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    confidence_level: float = 0.95,
    lookback: int = 252,
    inplace: bool = False,
    prefix: str = "CVAR",
) -> pd.DataFrame | pd.Series:
    """Conditional Value at Risk (CVaR) based risk signals."""

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    if len(returns) < lookback:
        cvar_signal = pd.Series(0, index=selection.series.index)
        cvar_value = pd.Series(0.0, index=selection.series.index)
    else:
        cvar_signal = pd.Series(0, index=selection.series.index)
        cvar_value = pd.Series(0.0, index=selection.series.index)

        for i in range(lookback, len(returns)):
            window_returns = returns.iloc[i-lookback:i]

            # Calculate VaR first
            var_threshold = np.percentile(window_returns, (1 - confidence_level) * 100)

            # CVaR is the expected loss given that loss exceeds VaR
            tail_losses = window_returns[window_returns <= var_threshold]

            if len(tail_losses) > 0:
                cvar = tail_losses.mean()
            else:
                cvar = var_threshold

            cvar_value.iloc[i] = abs(cvar)

            # CVaR signals
            if abs(cvar) > 0.08:  # Severe tail risk
                cvar_signal.iloc[i] = -3
            elif abs(cvar) > 0.05:  # High tail risk
                cvar_signal.iloc[i] = -2
            elif abs(cvar) > 0.03:  # Moderate tail risk
                cvar_signal.iloc[i] = -1
            elif abs(cvar) > 0.01:  # Low tail risk
                cvar_signal.iloc[i] = 1
            else:  # Minimal tail risk
                cvar_signal.iloc[i] = 2

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_signal": cvar_signal,
            f"{prefix}_value": cvar_value,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_signal"] = cvar_signal
    target[f"{prefix}_value"] = cvar_value
    return target


def risk_parity_signals(
    data: pd.DataFrame,
    *,
    columns: List[str] = None,
    lookback: int = 60,
    target_risk: float = 0.10,
    inplace: bool = False,
    prefix: str = "RISK_PARITY",
) -> pd.DataFrame:
    """Risk Parity portfolio allocation signals."""

    if columns is None:
        # Assume multiple assets in dataframe
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for risk parity")
        columns = list(numeric_cols[:min(5, len(numeric_cols))])  # Max 5 assets

    require_columns(data, columns)

    asset_returns = data[columns].pct_change().fillna(0)

    if len(asset_returns) < lookback:
        risk_signal = pd.Series(0, index=data.index)
        allocation_signal = pd.DataFrame(0, index=data.index, columns=[f"{prefix}_{col}" for col in columns])
    else:
        risk_signal = pd.Series(0, index=data.index)
        allocation_signal = pd.DataFrame(0, index=data.index, columns=[f"{prefix}_{col}" for col in columns])

        for i in range(lookback, len(asset_returns)):
            window_returns = asset_returns.iloc[i-lookback:i]

            # Calculate covariance matrix
            cov_matrix = window_returns.cov()

            # Calculate volatilities
            volatilities = np.sqrt(np.diag(cov_matrix))

            # Risk parity weights (inverse volatility weighting)
            inv_vol_weights = 1.0 / volatilities
            risk_parity_weights = inv_vol_weights / inv_vol_weights.sum()

            # Scale to target risk
            portfolio_vol = np.sqrt(risk_parity_weights.T @ cov_matrix @ risk_parity_weights)
            if portfolio_vol > 0:
                scaled_weights = risk_parity_weights * (target_risk / portfolio_vol)
            else:
                scaled_weights = risk_parity_weights

            # Generate allocation signals
            for j, col in enumerate(columns):
                weight = scaled_weights[j]
                if weight > 0.30:  # Overweight
                    allocation_signal.iloc[i, j] = 2
                elif weight > 0.20:  # Moderate overweight
                    allocation_signal.iloc[i, j] = 1
                elif weight > 0.10:  # Underweight
                    allocation_signal.iloc[i, j] = -1
                else:  # Significant underweight
                    allocation_signal.iloc[i, j] = -2

            # Overall risk signal
            portfolio_risk = np.sqrt(scaled_weights.T @ cov_matrix @ scaled_weights)
            if portfolio_risk > target_risk * 1.5:  # Too risky
                risk_signal.iloc[i] = -2
            elif portfolio_risk > target_risk * 1.2:  # Risky
                risk_signal.iloc[i] = -1
            elif portfolio_risk < target_risk * 0.8:  # Too conservative
                risk_signal.iloc[i] = 1
            else:  # Optimal risk
                risk_signal.iloc[i] = 2

    target = data if inplace else data.copy()
    target[f"{prefix}_overall_signal"] = risk_signal
    for col in allocation_signal.columns:
        target[col] = allocation_signal[col]
    return target


def stress_testing_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    scenarios: Dict[str, float] = None,
    inplace: bool = False,
    prefix: str = "STRESS",
) -> pd.DataFrame | pd.Series:
    """Stress testing based risk signals."""

    if scenarios is None:
        scenarios = {
            "mild_stress": -0.05,      # -5% drop
            "moderate_stress": -0.10,  # -10% drop
            "severe_stress": -0.20,    # -20% drop
            "black_swan": -0.30,       # -30% drop
        }

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    # Calculate Value at Risk for different scenarios
    stress_signals = pd.DataFrame(index=selection.series.index)

    for scenario_name, stress_level in scenarios.items():
        # Simulate stress impact
        stress_returns = returns + stress_level  # Additive stress

        # Calculate potential loss
        stress_impact = stress_returns.rolling(window=20).quantile(0.05)  # 5% worst case

        # Generate stress signal
        stress_signal = pd.Series(0, index=selection.series.index)
        stress_signal[stress_impact < stress_level * 1.5] = -2  # Severe stress
        stress_signal[stress_impact < stress_level * 1.2] = -1  # Moderate stress
        stress_signal[stress_impact >= stress_level * 0.8] = 1  # Mild stress

        stress_signals[f"{prefix}_{scenario_name}_signal"] = stress_signal
        stress_signals[f"{prefix}_{scenario_name}_impact"] = stress_impact

    # Overall stress signal (worst case scenario)
    overall_stress = stress_signals.filter(like=f"{prefix}_signal").min(axis=1)

    if isinstance(selection.data, pd.Series):
        stress_signals[f"{prefix}_overall_signal"] = overall_stress
        return stress_signals

    target = selection.data if inplace else selection.data.copy()
    for col in stress_signals.columns:
        target[col] = stress_signals[col]
    return target


def liquidity_risk_signals(
    data: pd.DataFrame,
    *,
    price_column: str = "close",
    volume_column: str = "volume",
    spread_column: Optional[str] = None,
    inplace: bool = False,
    prefix: str = "LIQUIDITY",
) -> pd.DataFrame:
    """Liquidity risk assessment signals."""

    require_columns(data, [price_column, volume_column])

    # Volume-based liquidity
    volume_ma = data[volume_column].rolling(window=20).mean()
    volume_ratio = data[volume_column] / volume_ma

    # Price impact (using volume-weighted average price if available)
    if "vwap" in data.columns:
        price_impact = abs(data[price_column] - data["vwap"]) / data["vwap"]
    else:
        price_impact = data[price_column].pct_change().abs()

    # Bid-ask spread proxy (high-low range as % of price)
    if "high" in data.columns and "low" in data.columns:
        spread_proxy = (data["high"] - data["low"]) / data["close"]
    else:
        spread_proxy = pd.Series(0.01, index=data.index)  # Default assumption

    # Turnover ratio (volume / outstanding shares approximation)
    # Using relative volume as proxy
    turnover_proxy = volume_ratio

    # Liquidity risk signals
    volume_signal = pd.Series(0, index=data.index)
    volume_signal[volume_ratio < 0.5] = -2  # Very low liquidity
    volume_signal[volume_ratio < 0.8] = -1  # Low liquidity
    volume_signal[volume_ratio > 1.5] = 1   # High liquidity

    spread_signal = pd.Series(0, index=data.index)
    spread_signal[spread_proxy > 0.05] = -2  # Wide spread
    spread_signal[spread_proxy > 0.02] = -1  # Moderate spread
    spread_signal[spread_proxy < 0.005] = 1  # Tight spread

    impact_signal = pd.Series(0, index=data.index)
    impact_signal[price_impact > 0.02] = -2  # High impact
    impact_signal[price_impact > 0.01] = -1  # Moderate impact
    impact_signal[price_impact < 0.002] = 1  # Low impact

    # Overall liquidity signal
    overall_liquidity = (volume_signal + spread_signal + impact_signal) / 3

    target = data if inplace else data.copy()
    target[f"{prefix}_volume_signal"] = volume_signal
    target[f"{prefix}_spread_signal"] = spread_signal
    target[f"{prefix}_impact_signal"] = impact_signal
    target[f"{prefix}_overall_signal"] = overall_liquidity
    target[f"{prefix}_volume_ratio"] = volume_ratio
    target[f"{prefix}_spread_proxy"] = spread_proxy
    target[f"{prefix}_price_impact"] = price_impact
    return target


def concentration_risk_signals(
    data: pd.DataFrame,
    *,
    columns: List[str] = None,
    lookback: int = 60,
    inplace: bool = False,
    prefix: str = "CONCENTRATION",
) -> pd.DataFrame:
    """Portfolio concentration risk signals."""

    if columns is None:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        columns = list(numeric_cols[:min(10, len(numeric_cols))])

    require_columns(data, columns)

    # Calculate weights (assume equal weighting if not specified)
    asset_prices = data[columns]
    asset_returns = asset_prices.pct_change().fillna(0)

    # Portfolio weights (equal weighting)
    n_assets = len(columns)
    weights = np.ones(n_assets) / n_assets

    # Concentration metrics
    concentration_signals = pd.DataFrame(index=data.index)

    # Herfindahl-Hirschman Index (HHI) for concentration
    hhi = pd.Series(0.0, index=data.index)
    for i in range(lookback, len(asset_returns)):
        # Calculate asset volatilities as proxy for "size"
        volatilities = asset_returns.iloc[i-lookback:i].std()
        total_vol = volatilities.sum()

        if total_vol > 0:
            # HHI = sum of squared market shares
            market_shares = volatilities / total_vol
            hhi.iloc[i] = (market_shares ** 2).sum()

    # Concentration signals based on HHI
    hhi_signal = pd.Series(0, index=data.index)
    hhi_signal[hhi > 0.25] = -3  # Highly concentrated (HHI > 2500 in standard scale)
    hhi_signal[hhi > 0.18] = -2  # Moderately concentrated
    hhi_signal[hhi > 0.10] = -1  # Somewhat concentrated
    hhi_signal[hhi < 0.05] = 1   # Well diversified

    # Maximum weight in portfolio
    max_weight_signal = pd.Series(0, index=data.index)

    # Diversification ratio
    diversification_ratio = 1.0 / hhi.replace(0, 0.01)  # Avoid division by zero

    div_signal = pd.Series(0, index=data.index)
    div_signal[diversification_ratio > 10] = 2  # Excellent diversification
    div_signal[diversification_ratio > 5] = 1   # Good diversification
    div_signal[diversification_ratio < 2] = -2  # Poor diversification

    target = data if inplace else data.copy()
    target[f"{prefix}_hhi_signal"] = hhi_signal
    target[f"{prefix}_hhi_index"] = hhi
    target[f"{prefix}_diversification_signal"] = div_signal
    target[f"{prefix}_diversification_ratio"] = diversification_ratio
    return target


def margin_risk_signals(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    initial_capital: float = 100000,
    maintenance_margin: float = 0.25,
    leverage_ratio: float = 2.0,
    inplace: bool = False,
    prefix: str = "MARGIN",
) -> pd.DataFrame | pd.Series:
    """Margin risk and leverage signals."""

    selection = select_series(data, column)

    returns = selection.series.pct_change().fillna(0)

    # Simulate portfolio value with leverage
    portfolio_value = pd.Series(initial_capital, index=selection.series.index)
    equity_value = pd.Series(initial_capital, index=selection.series.index)

    for i in range(1, len(selection.series)):
        # Leveraged return
        leveraged_return = returns.iloc[i] * leverage_ratio
        portfolio_value.iloc[i] = portfolio_value.iloc[i-1] * (1 + leveraged_return)

        # Equity changes (simplified - assuming no margin calls)
        equity_value.iloc[i] = portfolio_value.iloc[i]

    # Maintenance margin check
    margin_call_signal = pd.Series(0, index=selection.series.index)

    # Calculate margin requirement
    market_value = portfolio_value * (1 / leverage_ratio)  # Notional exposure
    maintenance_requirement = market_value * maintenance_margin

    # Margin call when equity < maintenance requirement
    margin_call = equity_value < maintenance_requirement
    margin_call_signal[margin_call] = -3  # Critical margin call

    # Margin utilization
    margin_utilization = maintenance_requirement / equity_value

    utilization_signal = pd.Series(0, index=selection.series.index)
    utilization_signal[margin_utilization > 0.9] = -3  # Over 90% utilization
    utilization_signal[margin_utilization > 0.7] = -2  # Over 70% utilization
    utilization_signal[margin_utilization > 0.5] = -1  # Over 50% utilization
    utilization_signal[margin_utilization < 0.3] = 1   # Under 30% utilization

    # Leverage risk signal
    leverage_signal = pd.Series(0, index=selection.series.index)
    if leverage_ratio > 5:
        leverage_signal[:] = -3  # Extreme leverage
    elif leverage_ratio > 3:
        leverage_signal[:] = -2  # High leverage
    elif leverage_ratio > 2:
        leverage_signal[:] = -1  # Moderate leverage
    else:
        leverage_signal[:] = 1   # Conservative leverage

    if isinstance(selection.data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_call_signal": margin_call_signal,
            f"{prefix}_utilization_signal": utilization_signal,
            f"{prefix}_leverage_signal": leverage_signal,
            f"{prefix}_portfolio_value": portfolio_value,
            f"{prefix}_equity_value": equity_value,
            f"{prefix}_utilization_ratio": margin_utilization,
        })
        return frame

    target = selection.data if inplace else selection.data.copy()
    target[f"{prefix}_call_signal"] = margin_call_signal
    target[f"{prefix}_utilization_signal"] = utilization_signal
    target[f"{prefix}_leverage_signal"] = leverage_signal
    target[f"{prefix}_portfolio_value"] = portfolio_value
    target[f"{prefix}_equity_value"] = equity_value
    target[f"{prefix}_utilization_ratio"] = margin_utilization
    return target


# =============================================================================
# MULTI-TIMEFRAME ANALYSIS
# =============================================================================

def resample_to_timeframe(
    data: pd.DataFrame,
    *,
    timeframe: str = "1H",
    price_column: str = "close",
    volume_column: str = "volume",
    aggregation: Dict[str, str] = None,
    inplace: bool = False,
    prefix: str = "RESAMPLED",
) -> pd.DataFrame:
    """Resample data to different timeframe for multi-timeframe analysis."""

    if aggregation is None:
        aggregation = {
            price_column: "last",  # Close price
            "high": "max",
            "low": "min",
            "open": "first",
            volume_column: "sum" if volume_column in data.columns else "last",
        }

    # Ensure datetime index
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex for resampling")

    # Resample data
    resampled = data.resample(timeframe).agg(aggregation)

    # Forward fill missing values
    resampled = resampled.fillna(method="ffill")

    target = data if inplace else data.copy()
    for col in resampled.columns:
        target[f"{prefix}_{timeframe}_{col}"] = resampled[col]

    return target


def align_multiple_timeframes(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["1H", "4H", "1D"],
    base_timeframe: str = "5T",
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "MTF",
) -> pd.DataFrame:
    """Align multiple timeframes for synchronized analysis."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    aligned_data = {}

    # Resample each timeframe
    for tf in timeframes:
        resampled = data.resample(tf).agg({
            price_column: "last",
            "high": "max",
            "low": "min",
            "open": "first",
            "volume": "sum" if "volume" in data.columns else "last",
        }).fillna(method="ffill")

        aligned_data[tf] = resampled

    # Align all timeframes to base timeframe
    base_resampled = data.resample(base_timeframe).agg({
        price_column: "last",
        "high": "max",
        "low": "min",
        "open": "first",
        "volume": "sum" if "volume" in data.columns else "last",
    }).fillna(method="ffill")

    # Merge all timeframes
    result = base_resampled.copy()

    for tf in timeframes:
        tf_data = aligned_data[tf]
        # Reindex to base timeframe
        tf_aligned = tf_data.reindex(base_resampled.index, method="ffill")

        for col in tf_data.columns:
            result[f"{prefix}_{tf}_{col}"] = tf_aligned[col]

    target = data if inplace else data.copy()
    for col in result.columns:
        if col not in target.columns:
            target[col] = result[col]

    return target


def cross_timeframe_correlation_signals(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["1H", "4H", "1D"],
    price_column: str = "close",
    correlation_window: int = 50,
    inplace: bool = False,
    prefix: str = "MTF_CORR",
) -> pd.DataFrame:
    """Calculate cross-timeframe correlation signals."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    # Get aligned timeframes
    aligned_data = align_multiple_timeframes(
        data,
        timeframes=timeframes,
        price_column=price_column,
        prefix="MTF_ALIGN"
    )

    correlations = pd.DataFrame(index=data.index)

    # Calculate correlations between timeframes
    for i, tf1 in enumerate(timeframes):
        for j, tf2 in enumerate(timeframes):
            if i < j:  # Avoid duplicate calculations
                col1 = f"MTF_ALIGN_{tf1}_{price_column}"
                col2 = f"MTF_ALIGN_{tf2}_{price_column}"

                if col1 in aligned_data.columns and col2 in aligned_data.columns:
                    # Rolling correlation
                    corr = aligned_data[col1].rolling(window=correlation_window).corr(aligned_data[col2])
                    correlations[f"{prefix}_{tf1}_{tf2}"] = corr

    # Generate correlation signals
    signals = pd.DataFrame(index=data.index)

    # High correlation signal (momentum across timeframes)
    mean_corr = correlations.mean(axis=1)
    signals[f"{prefix}_high_corr_signal"] = (mean_corr > 0.7).astype(int)

    # Low correlation signal (divergence)
    signals[f"{prefix}_low_corr_signal"] = (mean_corr < 0.3).astype(int)

    # Correlation trend
    corr_trend = mean_corr.diff(10).fillna(0)
    signals[f"{prefix}_corr_trend_signal"] = (corr_trend > 0).astype(int) - (corr_trend < 0).astype(int)

    target = data if inplace else data.copy()
    for col in signals.columns:
        target[col] = signals[col]

    # Add correlation matrix
    for col in correlations.columns:
        target[col] = correlations[col]

    return target


def hierarchical_signal_synthesis(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["5T", "15T", "1H", "4H", "1D"],
    signal_functions: List[callable] = None,
    weights: Dict[str, float] = None,
    aggregation_method: str = "weighted",
    inplace: bool = False,
    prefix: str = "HIERARCHICAL",
) -> pd.DataFrame:
    """Synthesize signals hierarchically across multiple timeframes."""

    if signal_functions is None:
        signal_functions = [rsi, macd, bollinger_bands]  # Use basic indicators

    if weights is None:
        # Equal weights for all timeframes
        weights = {tf: 1.0 / len(timeframes) for tf in timeframes}

    # Generate signals for each timeframe
    timeframe_signals = {}

    for tf in timeframes:
        try:
            # Resample data to timeframe
            tf_data = data.resample(tf).agg({
                "close": "last",
                "high": "max",
                "low": "min",
                "open": "first",
                "volume": "sum" if "volume" in data.columns else "last",
            }).fillna(method="ffill")

            # Apply signal functions
            tf_signals = []
            for signal_func in signal_functions:
                try:
                    result = signal_func(tf_data)
                    # Extract signal columns (ending with '_signal')
                    signal_cols = [col for col in result.columns if col.endswith('_signal')]
                    if signal_cols:
                        tf_signals.append(result[signal_cols].mean(axis=1))
                except:
                    continue

            if tf_signals:
                # Combine signals for this timeframe
                tf_combined = pd.concat(tf_signals, axis=1).mean(axis=1)
                timeframe_signals[tf] = tf_combined

        except:
            continue

    # Aggregate signals hierarchically
    if aggregation_method == "weighted":
        # Weighted average of timeframe signals
        hierarchical_signal = pd.Series(0.0, index=data.index)

        for tf, signals in timeframe_signals.items():
            # Reindex to original timeframe
            aligned_signals = signals.reindex(data.index, method="ffill").fillna(0)
            hierarchical_signal += aligned_signals * weights.get(tf, 1.0)

        hierarchical_signal = hierarchical_signal / sum(weights.values())

    elif aggregation_method == "voting":
        # Majority voting across timeframes
        all_signals = pd.DataFrame(index=data.index)

        for tf, signals in timeframe_signals.items():
            aligned_signals = signals.reindex(data.index, method="ffill").fillna(0)
            all_signals[f"{tf}_signal"] = (aligned_signals > 0).astype(int)

        # Count positive signals across timeframes
        vote_count = all_signals.sum(axis=1)
        hierarchical_signal = (vote_count > len(timeframes) / 2).astype(int)

    else:
        hierarchical_signal = pd.Series(0, index=data.index)

    # Generate confidence based on signal consistency
    signal_consistency = pd.Series(0.0, index=data.index)

    if len(timeframe_signals) > 1:
        signal_matrix = pd.DataFrame(index=data.index)

        for tf, signals in timeframe_signals.items():
            aligned_signals = signals.reindex(data.index, method="ffill").fillna(0)
            signal_matrix[f"{tf}_signal"] = np.sign(aligned_signals)

        # Calculate agreement ratio
        agreement = signal_matrix.abs().sum(axis=1) / len(timeframe_signals)
        signal_consistency = agreement / len(timeframe_signals)

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = hierarchical_signal
    target[f"{prefix}_confidence"] = signal_consistency
    target[f"{prefix}_timeframe_count"] = len(timeframe_signals)

    return target


def multi_timeframe_momentum_signals(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["1H", "4H", "1D"],
    momentum_periods: List[int] = [10, 20, 50],
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "MTF_MOMENTUM",
) -> pd.DataFrame:
    """Calculate multi-timeframe momentum signals."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    momentum_signals = pd.DataFrame(index=data.index)

    for tf in timeframes:
        # Resample to timeframe
        tf_data = data.resample(tf).agg({
            price_column: "last",
            "high": "max",
            "low": "min",
            "open": "first",
        }).fillna(method="ffill")

        for period in momentum_periods:
            # Calculate momentum
            momentum = (tf_data[price_column] - tf_data[price_column].shift(period)) / tf_data[price_column].shift(period)
            momentum = momentum.fillna(0)

            # Reindex to original timeframe
            momentum_aligned = momentum.reindex(data.index, method="ffill").fillna(0)

            momentum_signals[f"{prefix}_{tf}_{period}"] = momentum_aligned

    # Generate composite momentum signals
    composite_signals = pd.DataFrame(index=data.index)

    # Momentum agreement across timeframes
    for period in momentum_periods:
        tf_momentum_cols = [f"{prefix}_{tf}_{period}" for tf in timeframes]
        if all(col in momentum_signals.columns for col in tf_momentum_cols):
            # Average momentum across timeframes
            avg_momentum = momentum_signals[tf_momentum_cols].mean(axis=1)

            # Generate signals
            composite_signals[f"{prefix}_composite_{period}_signal"] = (
                (avg_momentum > 0.02).astype(int) - (avg_momentum < -0.02).astype(int)
            )

            # Momentum strength
            composite_signals[f"{prefix}_composite_{period}_strength"] = avg_momentum.abs()

    # Momentum divergence signals
    for period in momentum_periods:
        tf_momentum_cols = [f"{prefix}_{tf}_{period}" for tf in timeframes]
        if len(tf_momentum_cols) >= 2:
            # Check if shorter timeframe momentum > longer timeframe momentum
            short_tf = timeframes[0]  # Shortest timeframe
            long_tf = timeframes[-1]  # Longest timeframe

            short_col = f"{prefix}_{short_tf}_{period}"
            long_col = f"{prefix}_{long_tf}_{period}"

            if short_col in momentum_signals.columns and long_col in momentum_signals.columns:
                divergence = momentum_signals[short_col] - momentum_signals[long_col]
                composite_signals[f"{prefix}_divergence_{period}"] = (divergence > 0.01).astype(int)

    target = data if inplace else data.copy()
    for col in momentum_signals.columns:
        target[col] = momentum_signals[col]

    for col in composite_signals.columns:
        target[col] = composite_signals[col]

    return target


def timeframe_synchronization_signals(
    data: pd.DataFrame,
    *,
    primary_timeframe: str = "5T",
    secondary_timeframes: List[str] = ["15T", "1H", "4H"],
    sync_threshold: float = 0.8,
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "SYNC",
) -> pd.DataFrame:
    """Analyze timeframe synchronization and generate sync signals."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    # Calculate trends for each timeframe
    timeframe_trends = {}

    for tf in [primary_timeframe] + secondary_timeframes:
        tf_data = data.resample(tf).agg({
            price_column: "last",
            "high": "max",
            "low": "min",
        }).fillna(method="ffill")

        # Calculate short-term trend (20-period MA vs price)
        ma_20 = tf_data[price_column].rolling(window=20).mean()
        trend = (tf_data[price_column] - ma_20) / ma_20
        trend = trend.fillna(0)

        timeframe_trends[tf] = trend

    # Analyze synchronization
    sync_signals = pd.DataFrame(index=data.index)

    # Reindex all trends to primary timeframe
    primary_trend = timeframe_trends[primary_timeframe]

    for tf in secondary_timeframes:
        tf_trend = timeframe_trends[tf]
        aligned_trend = tf_trend.reindex(data.index, method="ffill").fillna(0)

        # Calculate synchronization score
        sync_score = primary_trend.corr(aligned_trend)
        if np.isnan(sync_score):
            sync_score = 0.0

        # Create sync score series
        sync_score_series = pd.Series(sync_score, index=data.index)
        sync_signals[f"{prefix}_{tf}_sync_score"] = sync_score_series

        # Synchronization signal
        sync_signals[f"{prefix}_{tf}_sync_signal"] = (sync_score_series > sync_threshold).astype(int)

    # Overall synchronization
    sync_scores = sync_signals.filter(like=f"{prefix}_sync_score")
    overall_sync = sync_scores.mean(axis=1)
    sync_signals[f"{prefix}_overall_sync"] = overall_sync
    sync_signals[f"{prefix}_overall_sync_signal"] = (overall_sync > sync_threshold).astype(int)

    # Synchronization changes (important for trading signals)
    sync_changes = overall_sync.diff(10).fillna(0)
    sync_signals[f"{prefix}_sync_change_signal"] = (
        (sync_changes > 0.1).astype(int) - (sync_changes < -0.1).astype(int)
    )

    target = data if inplace else data.copy()
    for col in sync_signals.columns:
        target[col] = sync_signals[col]

    return target


def multi_timeframe_pattern_recognition(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["1H", "4H", "1D"],
    patterns: List[str] = ["head_shoulders", "double_top", "wedge"],
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "MTF_PATTERN",
) -> pd.DataFrame:
    """Multi-timeframe pattern recognition synthesis."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    pattern_signals = pd.DataFrame(index=data.index)

    # Available pattern functions
    pattern_functions = {
        "head_shoulders": advanced_head_shoulders,
        "double_top": lambda d: double_top_bottom(d, pattern_type="double_top"),
        "wedge": lambda d: advanced_wedge_patterns(d, wedge_type="rising"),
        "triangle": advanced_triangle_patterns,
        "rectangle": rectangle_box_patterns,
    }

    for tf in timeframes:
        # Resample data
        tf_data = data.resample(tf).agg({
            price_column: "last",
            "high": "max",
            "low": "min",
            "open": "first",
        }).fillna(method="ffill")

        for pattern in patterns:
            if pattern in pattern_functions:
                try:
                    pattern_func = pattern_functions[pattern]
                    result = pattern_func(tf_data, prefix=f"PATTERN_{pattern.upper()}")

                    # Extract pattern signal
                    pattern_cols = [col for col in result.columns if "pattern" in col.lower()]
                    if pattern_cols:
                        pattern_signal = result[pattern_cols[0]]
                        # Reindex to original timeframe
                        aligned_signal = pattern_signal.reindex(data.index, method="ffill").fillna(0)

                        pattern_signals[f"{prefix}_{tf}_{pattern}"] = aligned_signal.astype(int)

                except:
                    # Pattern detection failed
                    pattern_signals[f"{prefix}_{tf}_{pattern}"] = 0

    # Generate multi-timeframe pattern signals
    composite_signals = pd.DataFrame(index=data.index)

    # Pattern agreement across timeframes
    for pattern in patterns:
        pattern_cols = [f"{prefix}_{tf}_{pattern}" for tf in timeframes]
        if all(col in pattern_signals.columns for col in pattern_cols):
            # Count patterns detected across timeframes
            pattern_count = pattern_signals[pattern_cols].sum(axis=1)
            composite_signals[f"{prefix}_composite_{pattern}"] = (pattern_count > 0).astype(int)

            # Pattern strength (more timeframes = stronger signal)
            composite_signals[f"{prefix}_strength_{pattern}"] = pattern_count / len(timeframes)

    # Pattern sequence analysis
    if len(timeframes) >= 2:
        # Check if pattern develops from lower to higher timeframes
        for pattern in patterns:
            pattern_cols = [f"{prefix}_{tf}_{pattern}" for tf in timeframes]
            if all(col in pattern_signals.columns for col in pattern_cols):
                # Pattern sequence signal
                sequence_signal = pd.Series(0, index=data.index)

                # Simple sequence: pattern appears in multiple consecutive timeframes
                for i in range(1, len(timeframes)):
                    current_tf_signal = pattern_signals[pattern_cols[i]]
                    prev_tf_signal = pattern_signals[pattern_cols[i-1]]

                    # Sequence: pattern in longer timeframe, then shorter
                    sequence = (current_tf_signal == 1) & (prev_tf_signal == 1)
                    sequence_signal = sequence_signal | sequence.astype(int)

                composite_signals[f"{prefix}_sequence_{pattern}"] = sequence_signal

    target = data if inplace else data.copy()
    for col in pattern_signals.columns:
        target[col] = pattern_signals[col]

    for col in composite_signals.columns:
        target[col] = composite_signals[col]

    return target


def hierarchical_signal_aggregation(
    data: pd.DataFrame,
    *,
    hierarchy_levels: List[str] = ["micro", "short", "medium", "long"],
    level_timeframes: Dict[str, str] = None,
    signal_weights: Dict[str, float] = None,
    aggregation_method: str = "weighted_hierarchy",
    inplace: bool = False,
    prefix: str = "HIERARCHY",
) -> pd.DataFrame:
    """Hierarchical signal aggregation across different market scales."""

    if level_timeframes is None:
        level_timeframes = {
            "micro": "5T",
            "short": "1H",
            "medium": "4H",
            "long": "1D",
        }

    if signal_weights is None:
        signal_weights = {
            "micro": 0.1,
            "short": 0.3,
            "medium": 0.4,
            "long": 0.2,
        }

    # Generate signals for each hierarchy level
    level_signals = {}

    for level, tf in level_timeframes.items():
        try:
            # Resample to timeframe
            tf_data = data.resample(tf).agg({
                "close": "last",
                "high": "max",
                "low": "min",
                "open": "first",
                "volume": "sum" if "volume" in data.columns else "last",
            }).fillna(method="ffill")

            # Generate multiple signals for this timeframe
            signals = []

            # RSI signal
            try:
                rsi_data = rsi(tf_data)
                rsi_signal = (rsi_data["RSI_14"] < 30).astype(int) - (rsi_data["RSI_14"] > 70).astype(int)
                signals.append(rsi_signal)
            except:
                pass

            # MACD signal
            try:
                macd_data = macd(tf_data)
                macd_signal = (macd_data["MACD_12_26_9"] > macd_data["MACDs_12_26_9"]).astype(int) * 2 - 1
                signals.append(macd_signal)
            except:
                pass

            # Bollinger Band signal
            try:
                bb_data = bollinger_bands(tf_data)
                bb_position = (tf_data["close"] - bb_data["BBL_20_2.0"]) / (bb_data["BBU_20_2.0"] - bb_data["BBL_20_2.0"])
                bb_signal = ((bb_position < 0.2).astype(int) - (bb_position > 0.8).astype(int))
                signals.append(bb_signal)
            except:
                pass

            if signals:
                # Combine signals for this level
                level_combined = pd.concat(signals, axis=1).mean(axis=1)
                level_signals[level] = level_combined

        except:
            continue

    # Hierarchical aggregation
    if aggregation_method == "weighted_hierarchy":
        # Weight signals by hierarchy importance
        hierarchical_signal = pd.Series(0.0, index=data.index)

        for level, signals in level_signals.items():
            aligned_signals = signals.reindex(data.index, method="ffill").fillna(0)
            weight = signal_weights.get(level, 1.0)
            hierarchical_signal += aligned_signals * weight

        # Normalize by total weight
        total_weight = sum(signal_weights.get(level, 1.0) for level in level_signals.keys())
        if total_weight > 0:
            hierarchical_signal = hierarchical_signal / total_weight

    elif aggregation_method == "bottom_up":
        # Bottom-up: micro influences short, short influences medium, etc.
        hierarchical_signal = pd.Series(0.0, index=data.index)

        # Start with micro level
        if "micro" in level_signals:
            micro_signals = level_signals["micro"].reindex(data.index, method="ffill").fillna(0)
            hierarchical_signal = micro_signals * 0.4

        # Add short-term influence
        if "short" in level_signals:
            short_signals = level_signals["short"].reindex(data.index, method="ffill").fillna(0)
            hierarchical_signal += short_signals * 0.3

        # Add medium-term influence
        if "medium" in level_signals:
            medium_signals = level_signals["medium"].reindex(data.index, method="ffill").fillna(0)
            hierarchical_signal += medium_signals * 0.2

        # Add long-term influence
        if "long" in level_signals:
            long_signals = level_signals["long"].reindex(data.index, method="ffill").fillna(0)
            hierarchical_signal += long_signals * 0.1

    else:
        hierarchical_signal = pd.Series(0.0, index=data.index)

    # Calculate signal confidence based on agreement across levels
    confidence_score = pd.Series(0.0, index=data.index)

    if len(level_signals) > 1:
        signal_matrix = pd.DataFrame(index=data.index)

        for level, signals in level_signals.items():
            aligned_signals = signals.reindex(data.index, method="ffill").fillna(0)
            signal_matrix[f"{level}_signal"] = np.sign(aligned_signals)

        # Agreement ratio across hierarchy levels
        agreement = signal_matrix.abs().sum(axis=1) / len(level_signals)
        confidence_score = agreement / len(level_signals)

    # Generate final signals
    final_signal = pd.Series(0, index=data.index)
    final_signal[hierarchical_signal > 0.2] = 1
    final_signal[hierarchical_signal < -0.2] = -1

    target = data if inplace else data.copy()
    target[f"{prefix}_signal"] = final_signal
    target[f"{prefix}_raw_score"] = hierarchical_signal
    target[f"{prefix}_confidence"] = confidence_score
    target[f"{prefix}_level_count"] = len(level_signals)

    return target


def multi_timeframe_volatility_signals(
    data: pd.DataFrame,
    *,
    timeframes: List[str] = ["15T", "1H", "4H", "1D"],
    volatility_window: int = 20,
    price_column: str = "close",
    inplace: bool = False,
    prefix: str = "MTF_VOL",
) -> pd.DataFrame:
    """Multi-timeframe volatility analysis and signals."""

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have DatetimeIndex")

    volatility_signals = pd.DataFrame(index=data.index)

    # Calculate volatility for each timeframe
    timeframe_volatilities = {}

    for tf in timeframes:
        tf_data = data.resample(tf).agg({
            price_column: "last",
            "high": "max",
            "low": "min",
        }).fillna(method="ffill")

        # Calculate returns and volatility
        returns = tf_data[price_column].pct_change().fillna(0)
        volatility = returns.rolling(window=volatility_window).std() * np.sqrt(252)  # Annualized

        timeframe_volatilities[tf] = volatility

    # Generate multi-timeframe volatility signals
    for tf, vol in timeframe_volatilities.items():
        aligned_vol = vol.reindex(data.index, method="ffill").fillna(0)
        volatility_signals[f"{prefix}_{tf}_volatility"] = aligned_vol

        # Volatility regime signals
        vol_quantile = aligned_vol.rolling(window=100).quantile(0.8)
        volatility_signals[f"{prefix}_{tf}_high_vol_signal"] = (aligned_vol > vol_quantile).astype(int)

    # Volatility spread analysis
    if len(timeframes) >= 2:
        # Compare volatility across timeframes
        short_tf_vol = volatility_signals[f"{prefix}_{timeframes[0]}_volatility"]
        long_tf_vol = volatility_signals[f"{prefix}_{timeframes[-1]}_volatility"]

        # Volatility spread
        vol_spread = short_tf_vol - long_tf_vol
        volatility_signals[f"{prefix}_vol_spread"] = vol_spread

        # Volatility divergence signals
        volatility_signals[f"{prefix}_vol_divergence"] = (
            ((short_tf_vol > short_tf_vol.quantile(0.8)) & (long_tf_vol < long_tf_vol.quantile(0.2))).astype(int) -
            ((short_tf_vol < short_tf_vol.quantile(0.2)) & (long_tf_vol > long_tf_vol.quantile(0.8))).astype(int)
        )

    # Volatility trend analysis
    vol_trends = pd.DataFrame(index=data.index)

    for tf in timeframes:
        vol_series = volatility_signals[f"{prefix}_{tf}_volatility"]
        vol_trend = vol_series.diff(10).fillna(0)
        vol_trends[f"{tf}_trend"] = vol_trend

        # Trend signals
        vol_trends[f"{tf}_trend_signal"] = (
            (vol_trend > vol_series.rolling(50).std() * 0.5).astype(int) -
            (vol_trend < -vol_series.rolling(50).std() * 0.5).astype(int)
        )

    # Composite volatility signals
    composite_signals = pd.DataFrame(index=data.index)

    # Average volatility across timeframes
    vol_cols = [f"{prefix}_{tf}_volatility" for tf in timeframes]
    if all(col in volatility_signals.columns for col in vol_cols):
        avg_volatility = volatility_signals[vol_cols].mean(axis=1)
        composite_signals[f"{prefix}_composite_volatility"] = avg_volatility

        # Composite volatility signal
        vol_threshold = avg_volatility.rolling(window=50).quantile(0.75)
        composite_signals[f"{prefix}_composite_signal"] = (avg_volatility > vol_threshold).astype(int)

    target = data if inplace else data.copy()
    for col in volatility_signals.columns:
        target[col] = volatility_signals[col]

    for col in vol_trends.columns:
        target[f"{prefix}_trend_{col}"] = vol_trends[col]

    for col in composite_signals.columns:
        target[col] = composite_signals[col]

    return target


# =============================================================================
# CANDLESTICK PATTERNS
# =============================================================================

def bullish_engulfing(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Bullish Engulfing Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Previous candle is bearish
    prev_bearish = data["close"].shift(1) < data["open"].shift(1)

    # Current candle is bullish
    curr_bullish = data["close"] > data["open"]

    # Current candle engulfs previous candle
    engulfing = (data["open"] <= data["close"].shift(1)) & (data["close"] >= data["open"].shift(1))

    pattern = prev_bearish & curr_bullish & engulfing

    output_name = name or "BULLISH_ENGULFING"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def bearish_engulfing(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Bearish Engulfing Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Previous candle is bullish
    prev_bullish = data["close"].shift(1) > data["open"].shift(1)

    # Current candle is bearish
    curr_bearish = data["close"] < data["open"]

    # Current candle engulfs previous candle
    engulfing = (data["open"] >= data["close"].shift(1)) & (data["close"] <= data["open"].shift(1))

    pattern = prev_bullish & curr_bearish & engulfing

    output_name = name or "BEARISH_ENGULFING"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def hammer(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Hammer Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Body is small (less than 30% of total range)
    body_size = abs(data["close"] - data["open"])
    total_range = data["high"] - data["low"]
    small_body = body_size <= total_range * 0.3

    # Lower shadow is at least 2x the body
    lower_shadow = data["open"].clip(lower=data["close"]) - data["low"]
    hammer_condition = lower_shadow >= body_size * 2

    # Upper shadow is small
    upper_shadow = data["high"] - data["open"].clip(upper=data["close"])
    small_upper_shadow = upper_shadow <= body_size

    pattern = small_body & hammer_condition & small_upper_shadow

    output_name = name or "HAMMER"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def shooting_star(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Shooting Star Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Body is small (less than 30% of total range)
    body_size = abs(data["close"] - data["open"])
    total_range = data["high"] - data["low"]
    small_body = body_size <= total_range * 0.3

    # Upper shadow is at least 2x the body
    upper_shadow = data["high"] - data["open"].clip(upper=data["close"])
    shooting_condition = upper_shadow >= body_size * 2

    # Lower shadow is small
    lower_shadow = data["open"].clip(lower=data["close"]) - data["low"]
    small_lower_shadow = lower_shadow <= body_size

    pattern = small_body & shooting_condition & small_lower_shadow

    output_name = name or "SHOOTING_STAR"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def doji(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Doji Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Body is very small (less than 5% of total range)
    body_size = abs(data["close"] - data["open"])
    total_range = data["high"] - data["low"]
    very_small_body = body_size <= total_range * 0.05

    pattern = very_small_body

    output_name = name or "DOJI"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def morning_star(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Morning Star Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Three candle pattern
    # 1st: Large bearish candle
    first_bearish = (data["close"].shift(2) < data["open"].shift(2)) & \
                   (abs(data["close"].shift(2) - data["open"].shift(2)) > (data["high"].shift(2) - data["low"].shift(2)) * 0.6)

    # 2nd: Small body (star)
    second_small = abs(data["close"].shift(1) - data["open"].shift(1)) < (data["high"].shift(1) - data["low"].shift(1)) * 0.3

    # 3rd: Large bullish candle
    third_bullish = (data["close"] > data["open"]) & \
                   (abs(data["close"] - data["open"]) > (data["high"] - data["low"]) * 0.6)

    # 2nd candle gaps down from 1st
    gap_down = data["high"].shift(1) < data["close"].shift(2)

    # 3rd candle closes above midpoint of 1st candle
    close_above_mid = data["close"] > (data["open"].shift(2) + data["close"].shift(2)) / 2

    pattern = first_bearish & second_small & third_bullish & gap_down & close_above_mid

    output_name = name or "MORNING_STAR"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def evening_star(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Evening Star Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Three candle pattern (opposite of morning star)
    # 1st: Large bullish candle
    first_bullish = (data["close"].shift(2) > data["open"].shift(2)) & \
                   (abs(data["close"].shift(2) - data["open"].shift(2)) > (data["high"].shift(2) - data["low"].shift(2)) * 0.6)

    # 2nd: Small body (star)
    second_small = abs(data["close"].shift(1) - data["open"].shift(1)) < (data["high"].shift(1) - data["low"].shift(1)) * 0.3

    # 3rd: Large bearish candle
    third_bearish = (data["close"] < data["open"]) & \
                   (abs(data["close"] - data["open"]) > (data["high"] - data["low"]) * 0.6)

    # 2nd candle gaps up from 1st
    gap_up = data["low"].shift(1) > data["close"].shift(2)

    # 3rd candle closes below midpoint of 1st candle
    close_below_mid = data["close"] < (data["open"].shift(2) + data["close"].shift(2)) / 2

    pattern = first_bullish & second_small & third_bearish & gap_up & close_below_mid

    output_name = name or "EVENING_STAR"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def three_white_soldiers(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Three White Soldiers Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Three consecutive bullish candles
    bullish1 = data["close"].shift(2) > data["open"].shift(2)
    bullish2 = data["close"].shift(1) > data["open"].shift(1)
    bullish3 = data["close"] > data["open"]

    # Each candle opens within previous body and closes higher
    open_in_body1 = data["open"].shift(1).between(data["close"].shift(2), data["open"].shift(2))
    open_in_body2 = data["open"].between(data["close"].shift(1), data["open"].shift(1))

    close_higher1 = data["close"].shift(1) > data["close"].shift(2)
    close_higher2 = data["close"] > data["close"].shift(1)

    # Small or no upper shadows
    small_upper1 = (data["high"].shift(2) - data["close"].shift(2)) <= abs(data["close"].shift(2) - data["open"].shift(2))
    small_upper2 = (data["high"].shift(1) - data["close"].shift(1)) <= abs(data["close"].shift(1) - data["open"].shift(1))
    small_upper3 = (data["high"] - data["close"]) <= abs(data["close"] - data["open"])

    pattern = bullish1 & bullish2 & bullish3 & open_in_body1 & open_in_body2 & \
             close_higher1 & close_higher2 & small_upper1 & small_upper2 & small_upper3

    output_name = name or "THREE_WHITE_SOLDIERS"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def three_black_crows(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Three Black Crows Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Three consecutive bearish candles
    bearish1 = data["close"].shift(2) < data["open"].shift(2)
    bearish2 = data["close"].shift(1) < data["open"].shift(1)
    bearish3 = data["close"] < data["open"]

    # Each candle opens within previous body and closes lower
    open_in_body1 = data["open"].shift(1).between(data["close"].shift(2), data["open"].shift(2))
    open_in_body2 = data["open"].between(data["close"].shift(1), data["open"].shift(1))

    close_lower1 = data["close"].shift(1) < data["close"].shift(2)
    close_lower2 = data["close"] < data["close"].shift(1)

    # Small or no lower shadows
    small_lower1 = (data["open"].shift(2) - data["low"].shift(2)) <= abs(data["close"].shift(2) - data["open"].shift(2))
    small_lower2 = (data["open"].shift(1) - data["low"].shift(1)) <= abs(data["close"].shift(1) - data["open"].shift(1))
    small_lower3 = (data["open"] - data["low"]) <= abs(data["close"] - data["open"])

    pattern = bearish1 & bearish2 & bearish3 & open_in_body1 & open_in_body2 & \
             close_lower1 & close_lower2 & small_lower1 & small_lower2 & small_lower3

    output_name = name or "THREE_BLACK_CROWS"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def piercing_pattern(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Piercing Pattern Candlestick."""

    require_columns(data, ("open", "high", "low", "close"))

    # Previous candle is bearish
    prev_bearish = data["close"].shift(1) < data["open"].shift(1)

    # Current candle is bullish
    curr_bullish = data["close"] > data["open"]

    # Current candle opens below previous low
    opens_below = data["open"] < data["low"].shift(1)

    # Current candle closes above previous midpoint
    closes_above_mid = data["close"] > (data["open"].shift(1) + data["close"].shift(1)) / 2

    # Closes in upper half of previous candle
    closes_high = data["close"] > data["open"].shift(1)

    pattern = prev_bearish & curr_bullish & opens_below & closes_above_mid & closes_high

    output_name = name or "PIERCING"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


def dark_cloud_cover(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Dark Cloud Cover Candlestick Pattern."""

    require_columns(data, ("open", "high", "low", "close"))

    # Previous candle is bullish
    prev_bullish = data["close"].shift(1) > data["open"].shift(1)

    # Current candle is bearish
    curr_bearish = data["close"] < data["open"]

    # Current candle opens above previous high
    opens_above = data["open"] > data["high"].shift(1)

    # Current candle closes below previous midpoint
    closes_below_mid = data["close"] < (data["open"].shift(1) + data["close"].shift(1)) / 2

    # Closes in lower half of previous candle
    closes_low = data["close"] < data["close"].shift(1)

    pattern = prev_bullish & curr_bearish & opens_above & closes_below_mid & closes_low

    output_name = name or "DARK_CLOUD_COVER"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pattern.astype(int)
    return target


# =============================================================================
# ADVANCED VOLUME ANALYSIS
# =============================================================================

def volume_price_analysis(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    prefix: str = "VPA",
) -> pd.DataFrame:
    """Comprehensive Volume Price Analysis."""

    require_columns(data, ("open", "high", "low", "close", "volume"))

    # Calculate typical price
    typical_price = (data["high"] + data["low"] + data["close"]) / 3

    # Volume Price Trend (already implemented above, but let's enhance it)
    vpt = (data["close"].pct_change().fillna(0) * data["volume"]).cumsum()

    # Intraday Intensity
    ii = (typical_price - typical_price.shift(1)).fillna(0) * data["volume"] / (data["high"] - data["low"]).replace(0, np.nan)
    ii = ii.fillna(0).cumsum()

    # Volume Flow Indicator
    vfi = pd.Series(0.0, index=data.index)
    cutoff = data["volume"].rolling(window=30).mean() * 2.5

    for i in range(1, len(data)):
        inter = (typical_price.iloc[i] - typical_price.iloc[i-1]) / typical_price.iloc[i-1] * 100
        vfi_val = inter * data["volume"].iloc[i] / cutoff.iloc[i] if cutoff.iloc[i] != 0 else 0
        vfi.iloc[i] = vfi.iloc[i-1] + vfi_val

    # Ease of Movement (already implemented above, but let's include it here)
    distance = ((data["high"] + data["low"]) / 2 - (data["high"].shift(1) + data["low"].shift(1)) / 2).fillna(0)
    box_ratio = data["volume"] / 100000000 / (data["high"] - data["low"]).replace(0, np.nan)
    box_ratio = box_ratio.fillna(0)
    eom = distance / box_ratio
    eom = eom.fillna(0).rolling(window=14).mean()

    target = data if inplace else data.copy()
    target[f"{prefix}_VPT"] = vpt
    target[f"{prefix}_II"] = ii
    target[f"{prefix}_VFI"] = vfi
    target[f"{prefix}_EOM"] = eom
    return target


def market_profile(
    data: pd.DataFrame,
    *,
    period: int = 20,
    bins: int = 10,
    inplace: bool = False,
    prefix: str = "MP",
) -> pd.DataFrame:
    """Market Profile Analysis."""

    require_columns(data, ("high", "low", "close", "volume"))

    # Point of Control (POC) - price level with highest volume
    poc_values = pd.Series(index=data.index, dtype=float)

    for i in range(period-1, len(data)):
        window_data = data.iloc[i-period+1:i+1]
        price_range = window_data["high"].max() - window_data["low"].min()
        price_bins = np.linspace(window_data["low"].min(), window_data["high"].max(), bins)

        # Simple volume distribution approximation
        poc_values.iloc[i] = window_data["close"].iloc[-1]  # Simplified

    # Value Area High/Low
    vah = poc_values + (data["high"].rolling(period).max() - data["low"].rolling(period).min()) * 0.25
    val = poc_values - (data["high"].rolling(period).max() - data["low"].rolling(period).min()) * 0.25

    target = data if inplace else data.copy()
    target[f"{prefix}_POC"] = poc_values
    target[f"{prefix}_VAH"] = vah
    target[f"{prefix}_VAL"] = val
    return target


def volume_profile(
    data: pd.DataFrame,
    *,
    period: int = 20,
    bins: int = 20,
    inplace: bool = False,
    prefix: str = "VP",
) -> pd.DataFrame:
    """Volume Profile Analysis."""

    require_columns(data, ("high", "low", "close", "volume"))

    # Calculate volume profile for each period
    vp_poc = pd.Series(index=data.index, dtype=float)
    vp_vah = pd.Series(index=data.index, dtype=float)
    vp_val = pd.Series(index=data.index, dtype=float)

    for i in range(period-1, len(data)):
        window = data.iloc[i-period+1:i+1]

        # Create price bins
        price_min = window["low"].min()
        price_max = window["high"].max()
        price_bins = np.linspace(price_min, price_max, bins)

        # Distribute volume across price bins (simplified)
        total_volume = window["volume"].sum()
        avg_volume_per_bin = total_volume / bins

        # POC is the price level with highest volume concentration
        vp_poc.iloc[i] = window["close"].iloc[-1]  # Simplified approximation

        # VAH/VAL around POC
        range_size = price_max - price_min
        vp_vah.iloc[i] = vp_poc.iloc[i] + range_size * 0.3
        vp_val.iloc[i] = vp_poc.iloc[i] - range_size * 0.3

    target = data if inplace else data.copy()
    target[f"{prefix}_POC"] = vp_poc
    target[f"{prefix}_VAH"] = vp_vah
    target[f"{prefix}_VAL"] = vp_val
    return target


def order_flow(
    data: pd.DataFrame,
    *,
    tick_size: float = 0.01,
    inplace: bool = False,
    prefix: str = "OF",
) -> pd.DataFrame:
    """Order Flow Analysis."""

    require_columns(data, ("open", "high", "low", "close", "volume"))

    # Simplified order flow calculation
    # In reality, this would require tick-by-tick data

    # Buying vs Selling pressure
    price_change = data["close"] - data["open"]
    volume_weighted_change = price_change * data["volume"]

    # Cumulative order flow
    order_flow_cum = volume_weighted_change.cumsum()

    # Order flow imbalance
    ofi = (data["close"] > data["open"]).astype(int) - (data["close"] < data["open"]).astype(int)
    ofi = ofi * data["volume"]

    target = data if inplace else data.copy()
    target[f"{prefix}_CUMULATIVE"] = order_flow_cum
    target[f"{prefix}_IMBALANCE"] = ofi
    return target


def time_price_opportunity(
    data: pd.DataFrame,
    *,
    period: int = 20,
    inplace: bool = False,
    prefix: str = "TPO",
) -> pd.DataFrame:
    """Time Price Opportunity Analysis."""

    require_columns(data, ("high", "low", "close", "volume"))

    # TPO Profile (simplified)
    # In practice, TPO requires time-based price distribution

    price_range = data["high"] - data["low"]
    volume_weighted_price = (data["close"] * data["volume"]).rolling(period).sum() / data["volume"].rolling(period).sum()

    # Value areas based on time distribution
    vah = volume_weighted_price + price_range.rolling(period).std()
    val = volume_weighted_price - price_range.rolling(period).std()

    target = data if inplace else data.copy()
    target[f"{prefix}_VWAP"] = volume_weighted_price
    target[f"{prefix}_VAH"] = vah
    target[f"{prefix}_VAL"] = val
    return target


def market_facilitation_index(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Market Facilitation Index (MFI) - Bill Williams."""

    require_columns(data, ("high", "low", "volume"))

    # MFI = (High - Low) / Volume
    mfi = (data["high"] - data["low"]) / data["volume"].replace(0, np.nan)
    mfi = mfi.fillna(0)

    output_name = name or "MFI"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = mfi
    return target


def tick_volume(
    data: pd.DataFrame,
    *,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Tick Volume Analysis."""

    require_columns(data, ("high", "low", "close", "volume"))

    # Simplified tick volume (in practice needs tick data)
    # Positive ticks vs negative ticks
    positive_ticks = (data["close"] > data["open"]).astype(int)
    negative_ticks = (data["close"] < data["open"]).astype(int)

    # Volume per tick
    positive_volume = positive_ticks * data["volume"]
    negative_volume = negative_ticks * data["volume"]

    # Tick volume ratio
    tick_volume_ratio = positive_volume / negative_volume.replace(0, np.nan)
    tick_volume_ratio = tick_volume_ratio.fillna(1.0)

    output_name = name or "TICK_VOLUME_RATIO"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = tick_volume_ratio
    return target


def volume_oscillator(
    data: pd.DataFrame,
    *,
    volume: str = "volume",
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    inplace: bool = False,
    prefix: str = "VO",
) -> pd.DataFrame | pd.Series:
    """Volume Oscillator."""

    require_columns(data, (volume,))

    # Calculate fast and slow EMA of volume
    fast_ema = data[volume].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data[volume].ewm(span=slow_period, adjust=False).mean()

    # Volume oscillator
    vo = ((fast_ema - slow_ema) / slow_ema.replace(0, np.nan)) * 100
    vo = vo.fillna(0)

    # Signal line
    vo_signal = vo.ewm(span=signal_period, adjust=False).mean()

    if isinstance(data, pd.Series):
        frame = pd.DataFrame({
            f"{prefix}_line": vo,
            f"{prefix}_signal": vo_signal,
        })
        return frame

    target = data if inplace else data.copy()
    target[f"{prefix}_line"] = vo
    target[f"{prefix}_signal"] = vo_signal
    return target


def price_volume_trend(
    data: pd.DataFrame,
    *,
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Price Volume Trend."""

    require_columns(data, (close, volume))

    # PVT = Previous PVT + (Current Close - Previous Close) / Previous Close * Volume
    pvt = pd.Series(0.0, index=data.index)

    for i in range(1, len(data)):
        price_change_pct = (data[close].iloc[i] - data[close].iloc[i-1]) / data[close].iloc[i-1]
        pvt.iloc[i] = pvt.iloc[i-1] + price_change_pct * data[volume].iloc[i]

    output_name = name or "PVT"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = pvt
    return target


def volume_relative_strength_index(
    data: pd.DataFrame,
    *,
    volume: str = "volume",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume Relative Strength Index."""

    require_columns(data, (volume,))

    # Calculate volume changes
    volume_change = data[volume].diff()

    # Separate gains and losses
    volume_gain = volume_change.where(volume_change > 0, 0.0)
    volume_loss = -volume_change.where(volume_change < 0, 0.0)

    # Calculate averages
    avg_gain = volume_gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = volume_loss.ewm(alpha=1/period, adjust=False).mean()

    # Calculate VRSI
    vrsi = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.nan)))
    vrsi = vrsi.fillna(50.0)

    output_name = name or f"VRSI_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = vrsi
    return target


def volume_flow_indicator(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume Flow Indicator."""

    require_columns(data, (high, low, close, volume))

    # Calculate typical price
    typical_price = (data[high] + data[low] + data[close]) / 3

    # Calculate raw money flow
    raw_mf = typical_price * data[volume]

    # Calculate money flow ratio
    positive_mf = raw_mf.where(typical_price > typical_price.shift(1), 0.0)
    negative_mf = raw_mf.where(typical_price < typical_price.shift(1), 0.0)

    # Sum over period
    pos_sum = positive_mf.rolling(window=period).sum()
    neg_sum = negative_mf.rolling(window=period).sum()

    # Volume Flow Indicator
    vfi = 100 - (100 / (1 + pos_sum / neg_sum.replace(0, np.nan)))
    vfi = vfi.fillna(50.0)

    output_name = name or f"VFI_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = vfi
    return target


def volume_weighted_average_price(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume Weighted Average Price (VWAP)."""

    require_columns(data, (high, low, close, volume))

    # Calculate typical price
    typical_price = (data[high] + data[low] + data[close]) / 3

    # Calculate cumulative price-volume and cumulative volume
    pv_cumsum = (typical_price * data[volume]).cumsum()
    volume_cumsum = data[volume].cumsum()

    # VWAP
    vwap = pv_cumsum / volume_cumsum.replace(0, np.nan)
    vwap = vwap.fillna(typical_price)

    output_name = name or "VWAP"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = vwap
    return target


def volume_weighted_moving_average(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    volume_column: str = "volume",
    window: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Volume Weighted Moving Average."""

    selection = select_series(data, column)

    # Get volume data
    if isinstance(selection.data, pd.DataFrame):
        volume_data = selection.data[volume_column]
    else:
        raise ValueError("Volume Weighted MA requires DataFrame with volume column")

    # Calculate VWMA
    pv_sum = (selection.series * volume_data).rolling(window=window, min_periods=ensure_min_periods(window)).sum()
    volume_sum = volume_data.rolling(window=window, min_periods=ensure_min_periods(window)).sum()

    vwma = pv_sum / volume_sum.replace(0, np.nan)
    vwma = vwma.fillna(selection.series)

    output_name = name or f"VWMA_{window}"
    return attach_result(selection, vwma, output_name, inplace=inplace)


def intraday_intensity(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Intraday Intensity Index."""

    require_columns(data, (high, low, close, volume))

    # Calculate intraday intensity
    intensity = ((data[close] * 2 - data[high] - data[low]) / (data[high] - data[low]).replace(0, np.nan)) * data[volume]
    intensity = intensity.fillna(0).cumsum()

    output_name = name or "INTRADAY_INTENSITY"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = intensity
    return target


def money_flow_multiplier(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Money Flow Multiplier."""

    require_columns(data, (high, low, close))

    # Calculate money flow multiplier
    mfm = ((data[close] - data[low]) - (data[high] - data[close])) / (data[high] - data[low]).replace(0, np.nan)
    mfm = mfm.fillna(0)

    output_name = name or "MFM"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = mfm
    return target


# =============================================================================
# ADDITIONAL MISSING FUNCTIONS
# =============================================================================

def money_flow_index(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Money Flow Index (MFI)."""

    require_columns(data, (high, low, close, volume))

    # Calculate typical price
    typical_price = (data[high] + data[low] + data[close]) / 3

    # Calculate raw money flow
    raw_mf = typical_price * data[volume]

    # Calculate money flow ratio
    positive_mf = raw_mf.where(typical_price > typical_price.shift(1), 0.0)
    negative_mf = raw_mf.where(typical_price < typical_price.shift(1), 0.0)

    # Sum over period
    pos_sum = positive_mf.rolling(window=period).sum()
    neg_sum = negative_mf.rolling(window=period).sum()

    # Money Flow Index
    mfi = 100 - (100 / (1 + pos_sum / neg_sum.replace(0, np.nan)))
    mfi = mfi.fillna(50.0)

    output_name = name or f"MFI_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = mfi
    return target


def commodity_channel_index(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    period: int = 20,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Commodity Channel Index (CCI)."""

    require_columns(data, (high, low, close))

    # Calculate typical price
    typical_price = (data[high] + data[low] + data[close]) / 3

    # Calculate SMA of typical price
    sma_tp = typical_price.rolling(window=period).mean()

    # Calculate mean deviation
    mean_dev = (typical_price - sma_tp).abs().rolling(window=period).mean()

    # Calculate CCI
    cci = (typical_price - sma_tp) / (0.015 * mean_dev)
    cci = cci.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    output_name = name or f"CCI_{period}"
    if inplace:
        target = data
    else:
        target = data.copy()
    target[output_name] = cci
    return target


def klinger_oscillator(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    volume: str = "volume",
    fast_period: int = 34,
    slow_period: int = 55,
    signal_period: int = 13,
    inplace: bool = False,
    prefix: str = "KO",
) -> pd.DataFrame:
    """Klinger Oscillator."""

    require_columns(data, (high, low, close, volume))

    # Calculate trend
    trend = pd.Series(0, index=data.index)
    dm = pd.Series(0, index=data.index)

    for i in range(1, len(data)):
        if data[close].iloc[i] > data[close].iloc[i-1]:
            trend.iloc[i] = 1
        elif data[close].iloc[i] < data[close].iloc[i-1]:
            trend.iloc[i] = -1
        else:
            trend.iloc[i] = trend.iloc[i-1]

        dm.iloc[i] = data[high].iloc[i] - data[low].iloc[i]

    # Calculate volume force
    vf = data[volume] * abs(2 * (dm / data[volume].shift(1).replace(0, np.nan)) - 1) * trend * 100
    vf = vf.fillna(0)

    # Calculate fast and slow EMAs
    fast_ema = vf.ewm(span=fast_period, adjust=False).mean()
    slow_ema = vf.ewm(span=slow_period, adjust=False).mean()

    # Klinger Oscillator
    ko = fast_ema - slow_ema
    ko_signal = ko.ewm(span=signal_period, adjust=False).mean()

    target = data if inplace else data.copy()
    target[f"{prefix}_line"] = ko
    target[f"{prefix}_signal"] = ko_signal
    return target


def schaff_trend_cycle(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    cycle_period: int = 10,
    short_cycle: int = 23,
    long_cycle: int = 50,
    k_period: int = 10,
    d_period: int = 3,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Schaff Trend Cycle."""

    selection = select_series(data, column)

    # Calculate cycle values using EMA
    cycle = selection.series.ewm(span=cycle_period, adjust=False).mean()

    # Calculate short and long cycle EMAs
    short_ema = selection.series.ewm(span=short_cycle, adjust=False).mean()
    long_ema = selection.series.ewm(span=long_cycle, adjust=False).mean()

    # Calculate stochastic of cycle
    cycle_max = cycle.rolling(window=cycle_period).max()
    cycle_min = cycle.rolling(window=cycle_period).min()
    range_size = cycle_max - cycle_min

    k_value = 100 * (cycle - cycle_min) / range_size.replace(0, np.nan)
    k_value = k_value.fillna(50)

    # Smooth K with EMA
    k_smooth = k_value.ewm(span=k_period, adjust=False).mean()

    # Calculate D (signal line)
    d_value = k_smooth.ewm(span=d_period, adjust=False).mean()

    # Schaff Trend Cycle
    stc = d_value.fillna(50)

    output_name = name or f"STC_{cycle_period}_{short_cycle}_{long_cycle}"
    return attach_result(selection, stc, output_name, inplace=inplace)


def coppock_curve(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    short_roc: int = 11,
    long_roc: int = 14,
    wma_period: int = 10,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Coppock Curve."""

    selection = select_series(data, column)

    # Calculate ROC for short and long periods
    short_roc_val = (selection.series / selection.series.shift(short_roc) - 1) * 100
    long_roc_val = (selection.series / selection.series.shift(long_roc) - 1) * 100

    # Sum of ROCs
    roc_sum = short_roc_val + long_roc_val

    # Apply WMA
    weights = np.arange(1, wma_period + 1)
    coppock = roc_sum.rolling(window=wma_period, min_periods=ensure_min_periods(wma_period)).apply(
        lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum() if len(x) > 0 else 0, raw=True
    )

    output_name = name or f"COPPOCK_{short_roc}_{long_roc}_{wma_period}"
    return attach_result(selection, coppock, output_name, inplace=inplace)


def rainbow_oscillator(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 2,
    levels: int = 9,
    inplace: bool = False,
    prefix: str = "RAINBOW",
) -> pd.DataFrame | pd.Series:
    """Rainbow Oscillator."""

    selection = select_series(data, column)

    # Calculate multiple SMAs with increasing periods
    smas = {}
    for i in range(levels):
        period_i = period * (i + 1)
        smas[f"sma_{i}"] = selection.series.rolling(window=period_i, min_periods=ensure_min_periods(period_i)).mean()

    # Rainbow Oscillator is the difference between fast and slow SMAs
    rainbow = smas["sma_0"] - smas[f"sma_{levels-1}"]

    output_name = f"{prefix}_{period}_{levels}"
    return attach_result(selection, rainbow, output_name, inplace=inplace)


def dynamic_momentum_index(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 14,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Dynamic Momentum Index."""

    selection = select_series(data, column)

    # Calculate RSI
    rsi = rsi(data, column=column, period=period, inplace=False)

    # Dynamic Momentum Index (simplified)
    # In practice, this involves more complex calculations
    dmi = rsi.rolling(window=period).mean() if isinstance(rsi, pd.Series) else rsi.iloc[:, 0].rolling(window=period).mean()

    output_name = name or f"DMI_{period}"
    return attach_result(selection, dmi, output_name, inplace=inplace)


def relative_vigor_index(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    high: str = "high",
    low: str = "low",
    close: str = "close",
    period: int = 10,
    inplace: bool = False,
    prefix: str = "RVI",
) -> pd.DataFrame:
    """Relative Vigor Index."""

    require_columns(data, (open_col, high, low, close))

    # Calculate RVI components
    co = data[close] - data[open_col]
    ho = data[high] - data[open_col]
    lo = data[low] - data[open_col]

    # RVI numerator and denominator
    numerator = co.rolling(window=period).sum()
    denominator = (ho + lo).rolling(window=period).sum()

    rvi = numerator / denominator.replace(0, np.nan)
    rvi = rvi.fillna(0)

    # Signal line (SMA of RVI)
    rvi_signal = rvi.rolling(window=4).mean()

    target = data if inplace else data.copy()
    target[f"{prefix}_line"] = rvi
    target[f"{prefix}_signal"] = rvi_signal
    return target


def stochastic_momentum_index(
    data: pd.DataFrame,
    *,
    high: str = "high",
    low: str = "low",
    close: str = "close",
    k_period: int = 14,
    smooth_k: int = 3,
    d_period: int = 3,
    inplace: bool = False,
    prefix: str = "SMI",
) -> pd.DataFrame:
    """Stochastic Momentum Index."""

    require_columns(data, (high, low, close))

    # Calculate %K
    highest_high = data[high].rolling(window=k_period).max()
    lowest_low = data[low].rolling(window=k_period).min()
    range_size = highest_high - lowest_low

    percent_k = 100 * (data[close] - lowest_low) / range_size.replace(0, np.nan)
    percent_k = percent_k.fillna(50)

    # Double smooth %K
    k_smooth1 = percent_k.ewm(span=smooth_k, adjust=False).mean()
    k_smooth2 = k_smooth1.ewm(span=smooth_k, adjust=False).mean()

    # Calculate highest/lowest of smoothed %K
    hh_smooth = k_smooth2.rolling(window=k_period).max()
    ll_smooth = k_smooth2.rolling(window=k_period).min()
    range_smooth = hh_smooth - ll_smooth

    # SMI %K
    smi_k = 100 * (k_smooth2 - ll_smooth) / range_smooth.replace(0, np.nan)
    smi_k = smi_k.fillna(0)

    # SMI %D
    smi_d = smi_k.ewm(span=d_period, adjust=False).mean()

    target = data if inplace else data.copy()
    target[f"{prefix}_%K"] = smi_k
    target[f"{prefix}_%D"] = smi_d
    return target


def triple_ema_oscillator(
    data: pd.DataFrame | pd.Series,
    *,
    column: Optional[str] = "close",
    period: int = 15,
    inplace: bool = False,
    name: Optional[str] = None,
) -> pd.DataFrame | pd.Series:
    """Triple EMA Oscillator."""

    selection = select_series(data, column)

    # Calculate triple EMA
    ema1 = selection.series.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()
    ema2 = ema1.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()
    ema3 = ema2.ewm(span=period, adjust=False, min_periods=ensure_min_periods(period)).mean()

    # Triple EMA Oscillator
    tema_osc = (3 * ema1 - 3 * ema2 + ema3).pct_change() * 100

    output_name = name or f"TEMA_OSC_{period}"
    return attach_result(selection, tema_osc, output_name, inplace=inplace)
