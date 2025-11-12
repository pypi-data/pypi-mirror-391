"""
Visualization module for Asymmetric Causality Testing.

This module provides visualization functions compatible with the 
asymmetric causality test results.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/asymcaus
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List
import plotly.express as px


def plot_components(data: np.ndarray, pos_components: np.ndarray,
                   neg_components: np.ndarray, var_names: Optional[List[str]] = None,
                   title: str = "Cumulative Components") -> go.Figure:
    """
    Plot original data with cumulative positive and negative components.
    
    Equivalent to plotting cumulative components from GAUSS code.
    
    Parameters
    ----------
    data : np.ndarray
        Original time series data (T x n)
    pos_components : np.ndarray
        Cumulative positive components (T x n)
    neg_components : np.ndarray
        Cumulative negative components (T x n)
    var_names : list of str, optional
        Variable names
    title : str, optional
        Plot title
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive plot
    """
    T, n_vars = data.shape
    
    if var_names is None:
        var_names = [f"Variable {i+1}" for i in range(n_vars)]
    
    # Create subplots
    fig = make_subplots(
        rows=n_vars, cols=1,
        subplot_titles=var_names,
        vertical_spacing=0.10
    )
    
    time_index = np.arange(T)
    
    for i in range(n_vars):
        # Original series
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=data[:, i],
                name=f'{var_names[i]} (Original)',
                line=dict(color='black', width=2.5),
                legendgroup=f"var{i}",
                showlegend=(i == 0)
            ),
            row=i+1, col=1
        )
        
        # Positive components
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=pos_components[:, i],
                name='Positive Component',
                line=dict(color='green', width=2, dash='dash'),
                legendgroup=f"var{i}",
                showlegend=(i == 0)
            ),
            row=i+1, col=1
        )
        
        # Negative components
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=neg_components[:, i],
                name='Negative Component',
                line=dict(color='red', width=2, dash='dot'),
                legendgroup=f"var{i}",
                showlegend=(i == 0)
            ),
            row=i+1, col=1
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time Period", row=i+1, col=1)
        fig.update_yaxes(title_text="Value", row=i+1, col=1)
    
    fig.update_layout(
        title=title,
        height=350 * n_vars,
        showlegend=True,
        template='plotly_white',
        hovermode='x unified',
        font=dict(size=11)
    )
    
    return fig


def plot_causality_results(Wstat: float, critical_values: np.ndarray,
                          test_name: str = "Asymmetric Causality Test",
                          component_type: str = "Positive") -> go.Figure:
    """
    Plot test statistic against critical values.
    
    Parameters
    ----------
    Wstat : float
        Wald test statistic
    critical_values : np.ndarray
        Bootstrap critical values [1%, 5%, 10%]
    test_name : str, optional
        Test name for title
    component_type : str, optional
        Component type ('Positive' or 'Negative')
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Bar chart with test statistic and critical values
    """
    categories = ['Test Statistic', '1% CV', '5% CV', '10% CV']
    values = [Wstat, critical_values[0], critical_values[1], critical_values[2]]
    
    # Determine colors
    colors = []
    if Wstat > critical_values[1]:  # Significant at 5%
        colors.append('lightcoral')
    else:
        colors.append('lightblue')
    colors.extend(['darkred', 'red', 'orange'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f"{val:.4f}" for val in values],
        textposition='outside',
        showlegend=False
    ))
    
    # Add decision line at 5% CV
    fig.add_hline(
        y=critical_values[1],
        line_dash="dash",
        line_color="red",
        annotation_text="5% Critical Value",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f"{test_name} - {component_type} Components",
        xaxis_title="",
        yaxis_title="Wald Statistic Value",
        template='plotly_white',
        height=500,
        font=dict(size=12)
    )
    
    return fig


def plot_multiple_tests(results: Dict, test_labels: Optional[List[str]] = None) -> go.Figure:
    """
    Plot results from multiple asymmetric causality tests.
    
    Parameters
    ----------
    results : dict
        Dictionary containing test results for different combinations
    test_labels : list of str, optional
        Labels for each test
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Comparison plot
    """
    if test_labels is None:
        test_labels = list(results.keys())
    
    # Extract statistics
    wstats = []
    cv_5pct = []
    for key in test_labels:
        wstats.append(results[key]['Wstat'])
        cv_5pct.append(results[key]['critical_values'][1])
    
    fig = go.Figure()
    
    # Add test statistics
    fig.add_trace(go.Bar(
        x=test_labels,
        y=wstats,
        name='Test Statistic',
        marker_color='lightblue',
        text=[f"{val:.2f}" for val in wstats],
        textposition='outside'
    ))
    
    # Add critical values as line
    fig.add_trace(go.Scatter(
        x=test_labels,
        y=cv_5pct,
        name='5% Critical Value',
        mode='lines+markers',
        line=dict(color='red', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond')
    ))
    
    fig.update_layout(
        title="Comparison of Asymmetric Causality Tests",
        xaxis_title="Test Type",
        yaxis_title="Wald Statistic",
        template='plotly_white',
        height=500,
        showlegend=True,
        font=dict(size=12),
        hovermode='x unified'
    )
    
    return fig


def plot_p_values(results: Dict, significance_levels: List[float] = [0.01, 0.05, 0.10]) -> go.Figure:
    """
    Plot p-values for multiple tests with significance level lines.
    
    Parameters
    ----------
    results : dict
        Test results dictionary
    significance_levels : list of float, optional
        Significance levels to display
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
        P-value comparison plot
    """
    from scipy import stats
    
    test_labels = list(results.keys())
    p_values = []
    
    # Calculate p-values from Wald statistics
    for key in test_labels:
        Wstat = results[key]['Wstat']
        lag_order = results[key]['lag_order']
        p_val = 1 - stats.chi2.cdf(Wstat, lag_order)
        p_values.append(p_val)
    
    # Determine colors based on significance
    colors = []
    for p in p_values:
        if p < 0.01:
            colors.append('#d62728')  # Dark red
        elif p < 0.05:
            colors.append('#ff7f0e')  # Orange
        elif p < 0.10:
            colors.append('#ffbb78')  # Light orange
        else:
            colors.append('#1f77b4')  # Blue
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=test_labels,
        y=p_values,
        marker_color=colors,
        text=[f"{val:.4f}" for val in p_values],
        textposition='outside',
        showlegend=False
    ))
    
    # Add significance lines
    for level, color, name in [(0.01, 'red', '1%'), (0.05, 'orange', '5%'), (0.10, 'yellow', '10%')]:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{name} level",
            annotation_position="right"
        )
    
    fig.update_layout(
        title="P-values for Asymmetric Causality Tests",
        xaxis_title="Test Type",
        yaxis_title="P-value",
        template='plotly_white',
        height=500,
        yaxis_range=[0, max(p_values) * 1.2 if max(p_values) > 0 else 0.5],
        font=dict(size=12)
    )
    
    return fig


def create_dashboard(data: np.ndarray, results: Dict, 
                    pos_components: np.ndarray, neg_components: np.ndarray,
                    var_names: Optional[List[str]] = None) -> go.Figure:
    """
    Create comprehensive dashboard with all visualizations.
    
    Parameters
    ----------
    data : np.ndarray
        Original data
    results : dict
        Test results
    pos_components : np.ndarray
        Positive components
    neg_components : np.ndarray
        Negative components
    var_names : list of str, optional
        Variable names
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Dashboard figure
    """
    from scipy import stats
    
    T, n_vars = data.shape
    
    if var_names is None:
        var_names = [f"Var {i+1}" for i in range(n_vars)]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Time Series with Components',
            'Test Statistics vs Critical Values',
            'P-values',
            'Component Comparison'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    time_index = np.arange(T)
    
    # 1. Time series with components (first variable)
    fig.add_trace(
        go.Scatter(x=time_index, y=data[:, 0], name='Original', 
                  line=dict(color='black', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_index, y=pos_components[:, 0], name='Pos Component',
                  line=dict(color='green', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_index, y=neg_components[:, 0], name='Neg Component',
                  line=dict(color='red', dash='dot')),
        row=1, col=1
    )
    
    # 2. Test statistics
    test_labels = list(results.keys())
    wstats = [results[key]['Wstat'] for key in test_labels]
    cv_5 = [results[key]['critical_values'][1] for key in test_labels]
    
    fig.add_trace(
        go.Bar(x=test_labels, y=wstats, name='Wald Stat', marker_color='lightblue',
              showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=test_labels, y=cv_5, name='5% CV', mode='lines+markers',
                  line=dict(color='red', dash='dash'), showlegend=False),
        row=1, col=2
    )
    
    # 3. P-values
    p_values = []
    for key in test_labels:
        Wstat = results[key]['Wstat']
        lag = results[key]['lag_order']
        p = 1 - stats.chi2.cdf(Wstat, lag)
        p_values.append(p)
    
    colors = ['lightcoral' if p < 0.05 else 'lightblue' for p in p_values]
    fig.add_trace(
        go.Bar(x=test_labels, y=p_values, marker_color=colors, showlegend=False),
        row=2, col=1
    )
    fig.add_hline(y=0.05, line_dash="dash", line_color="red", row=2, col=1)
    
    # 4. Component sums
    pos_sum = pos_components.sum(axis=0)
    neg_sum = neg_components.sum(axis=0)
    
    fig.add_trace(
        go.Bar(x=var_names, y=pos_sum, name='Pos Sum', marker_color='green',
              showlegend=False),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(x=var_names, y=neg_sum, name='Neg Sum', marker_color='red',
              showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="Asymmetric Causality Analysis Dashboard",
        showlegend=True,
        height=800,
        template='plotly_white',
        font=dict(size=10)
    )
    
    return fig


def export_plots(figures: Dict[str, go.Figure], output_dir: str = ".", 
                format: str = "html"):
    """
    Export multiple plots to files.
    
    Parameters
    ----------
    figures : dict
        Dictionary of figure names and Plotly figures
    output_dir : str, optional
        Output directory
    format : str, optional
        File format ('html' or 'png')
    """
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    for name, fig in figures.items():
        filepath = os.path.join(output_dir, f"{name}.{format}")
        
        if format == 'html':
            fig.write_html(filepath)
        elif format == 'png':
            fig.write_image(filepath)
        
        print(f"Exported: {filepath}")
