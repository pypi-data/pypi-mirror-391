"""
asymcaus: Asymmetric Causality Testing (GAUSS-Compatible)

A Python implementation fully compatible with the original GAUSS code
by Abdulnasser Hatemi-J (2012).

This package provides functions for testing asymmetric causality between
positive and negative shocks in time series data.

Reference:
    Hatemi-J, A. (2012). "Asymmetric causality tests with an application."
    Empirical Economics, 43(1), 447-456.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/asymcaus

Main Functions (GAUSS-compatible):
-----------------------------------
- asymmetric_causality_test: Main testing function (equivalent to asymCause)
- cumulative_component: Decompose into positive/negative components
- select_lag_order: Select optimal lag using information criteria
- compute_wald_statistic: Calculate Wald test statistic
- bootstrap_critical_values: Calculate bootstrap critical values
- varlags: Create lagged data matrix
- rstrctvm: Create restriction matrices
- estvar_params: Estimate VAR parameters

Visualization Functions:
-----------------------
- plot_components: Plot cumulative components
- plot_causality_results: Plot test results
- plot_multiple_tests: Compare multiple tests
- plot_p_values: Plot p-values
- create_dashboard: Comprehensive dashboard

Example:
--------
>>> import numpy as np
>>> from asymcaus import asymmetric_causality_test, cumulative_component
>>> 
>>> # Generate sample data
>>> np.random.seed(42)
>>> y = np.random.randn(200, 1).cumsum(axis=0)
>>> z = np.random.randn(200, 1).cumsum(axis=0)
>>> 
>>> # Test asymmetric causality (positive components)
>>> Wstat, cv, lag, azd = asymmetric_causality_test(
...     y, z, pos=1, infocrit=3, bootmaxiter=1000
... )
>>> 
>>> print(f"Wald statistic: {Wstat:.4f}")
>>> print(f"Critical values (1%, 5%, 10%): {cv}")
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
__license__ = "MIT"

# Core functions (GAUSS-compatible)
from .core import (
    # Main testing function
    asymmetric_causality_test,
    
    # Component decomposition
    cumulative_component,
    
    # Lag selection
    select_lag_order,
    
    # VAR estimation and testing
    estvar_params,
    compute_wald_statistic,
    bootstrap_critical_values,
    
    # Helper functions
    varlags,
    rstrctvm,
    insrtzero,
    
    # Convenience function
    test_all_combinations
)

# Visualization functions
from .visualization import (
    plot_components,
    plot_causality_results,
    plot_multiple_tests,
    plot_p_values,
    create_dashboard,
    export_plots
)

__all__ = [
    # Main functions
    'asymmetric_causality_test',
    'cumulative_component',
    'select_lag_order',
    'compute_wald_statistic',
    'bootstrap_critical_values',
    
    # VAR helpers
    'estvar_params',
    'varlags',
    'rstrctvm',
    'insrtzero',
    
    # Convenience
    'test_all_combinations',
    
    # Visualization
    'plot_components',
    'plot_causality_results',
    'plot_multiple_tests',
    'plot_p_values',
    'create_dashboard',
    'export_plots'
]

# Information criterion constants (GAUSS-compatible)
IC_AIC = 1
IC_AICC = 2
IC_SBC = 3  # Same as BIC
IC_HQC = 4
IC_HJC = 5  # Hatemi-J Criterion
IC_MAXLAGS = 6

# Component type constants
COMPONENT_POSITIVE = 1
COMPONENT_NEGATIVE = 0
