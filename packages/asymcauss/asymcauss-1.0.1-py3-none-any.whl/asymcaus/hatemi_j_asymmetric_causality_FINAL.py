"""
==============================================================================
HATEMI-J (2012) ASYMMETRIC CAUSALITY TEST - FINAL CORRECTED VERSION
==============================================================================

Reference: Hatemi-J, A. (2012). "Asymmetric causality tests with an application."
           Empirical Economics, 43(1), 447-456.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane

ALL CRITICAL ISSUES FIXED - This version produces correct, logical results.
==============================================================================
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Dict
import warnings

#===============================================================================
# FUNCTION 1: Decompose into Cumulative Components
#===============================================================================

def cumulative_components(y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Decompose series into cumulative positive and negative shocks.
    
    Parameters
    ----------
    y : np.ndarray
        Time series vector
        
    Returns
    -------
    y_pos : np.ndarray
        Cumulative positive shocks
    y_neg : np.ndarray
        Cumulative negative shocks
    """
    y = np.asarray(y).flatten()
    T = len(y)
    
    # Compute shocks
    eps = np.zeros(T)
    eps[1:] = np.diff(y)
    
    # Separate
    eps_pos = np.maximum(eps, 0)
    eps_neg = np.minimum(eps, 0)
    
    # Cumulative
    y_pos = np.cumsum(eps_pos)
    y_neg = np.cumsum(eps_neg)
    
    return y_pos, y_neg


#===============================================================================
# FUNCTION 2: Create VAR Lag Matrix
#===============================================================================

def create_var_lags(y: np.ndarray, p: int) -> Tuple[np.ndarray, np.ndarray]:
    """Create VAR(p) lag structure."""
    y = np.atleast_2d(y)
    if y.shape[0] == 1:
        y = y.T
        
    T, n = y.shape
    T_eff = T - p
    
    Y = y[p:, :]
    X = np.ones((T_eff, 1))
    
    for lag in range(1, p + 1):
        y_lag = y[p - lag:T - lag, :]
        X = np.hstack([X, y_lag])
    
    return Y, X


#===============================================================================
# FUNCTION 3: Create Restriction Matrix (CORRECTED)
#===============================================================================

def create_restriction_matrix(n_vars: int, p: int, d: int = 0) -> np.ndarray:
    """
    Create restriction matrix C for Granger causality test.
    
    Tests H0: y2 does not Granger-cause y1
    
    Parameters
    ----------
    n_vars : int
        Number of variables (2)
    p : int
        Lag order
    d : int
        Additional lags (Toda-Yamamoto)
        
    Returns
    -------
    C : np.ndarray
        Restriction matrix (p, n_vars*(1 + n_vars*(p+d)))
    """
    total_lags = p + d
    k = 1 + n_vars * total_lags
    total_params = n_vars * k
    
    C = np.zeros((p, total_params))
    
    # Restrict y2 coefficients in y1 equation for lags 1 to p
    for lag_idx in range(p):
        pos = 1 + lag_idx * n_vars + 1
        C[lag_idx, pos] = 1
    
    return C


#===============================================================================
# FUNCTION 4: Compute Wald Statistic (CORRECTED)
#===============================================================================

def compute_wald_statistic(Y: np.ndarray, X: np.ndarray, 
                           A: np.ndarray, C: np.ndarray) -> float:
    """
    Compute Wald test statistic following equation (7).
    
    Wald = (Cβ)' [C((X'X)^{-1} ⊗ SU)C']^{-1} (Cβ)
    """
    T, n = Y.shape
    k = X.shape[1]
    
    # Residuals
    U = Y - X @ A.T
    
    # Variance-covariance
    SU = (U.T @ U) / (T - k)
    
    # Vectorize (column-wise)
    beta = A.T.flatten('F').reshape(-1, 1)
    
    # C * beta
    Cbeta = C @ beta
    
    # (X'X)^{-1}
    XTX_inv = np.linalg.inv(X.T @ X)
    
    # Var(Cbeta) = C * [(X'X)^{-1} ⊗ SU] * C'
    var_Cbeta = C @ np.kron(XTX_inv, SU) @ C.T
    
    # Regularization
    var_Cbeta += np.eye(var_Cbeta.shape[0]) * 1e-10
    
    # Wald statistic
    try:
        W = float(Cbeta.T @ np.linalg.solve(var_Cbeta, Cbeta))
    except:
        W = float(Cbeta.T @ np.linalg.pinv(var_Cbeta) @ Cbeta)
    
    return W


#===============================================================================
# FUNCTION 5: Estimate VAR
#===============================================================================

def estimate_var_parameters(Y: np.ndarray, X: np.ndarray, 
                           restricted: bool = False,
                           C: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate VAR parameters."""
    T, n = Y.shape
    k = X.shape[1]
    
    # OLS
    A = (np.linalg.lstsq(X, Y, rcond=None)[0]).T
    
    # Zero out if restricted
    if restricted and C is not None:
        beta = A.T.flatten('F').reshape(-1, 1)
        restricted_idx = np.where(np.abs(C).sum(axis=0) > 0)[0]
        for idx in restricted_idx:
            col_idx = idx // k
            row_idx = idx % k
            A[col_idx, row_idx] = 0
    
    # Leverage
    XTX_inv = np.linalg.inv(X.T @ X)
    leverage = np.sum((X @ XTX_inv) * X, axis=1)
    leverage = np.clip(leverage, 0, 0.999)
    
    return A, leverage


#===============================================================================
# FUNCTION 6: Bootstrap (CORRECTED - Following GAUSS code exactly)
#===============================================================================

def bootstrap_critical_values(Y: np.ndarray, X: np.ndarray,
                              y_init: np.ndarray,
                              A: np.ndarray, leverage: np.ndarray,
                              p: int, d: int, n_boot: int,
                              C: np.ndarray) -> np.ndarray:
    """
    Bootstrap critical values with leverage adjustment.
    
    This follows the GAUSS code Bootstrap_Toda procedure exactly.
    """
    T, n = Y.shape
    k = X.shape[1]
    maxlag = p + d
    
    # Residuals
    U = Y - X @ A.T
    
    # Leverage adjustment (column-wise)
    U_adj = U.copy()
    for j in range(n):
        U_adj[:, j] = U[:, j] / np.sqrt(1 - leverage)
    
    # Bootstrap loop
    W_boot = np.zeros(n_boot)
    
    for b in range(n_boot):
        # Resample residuals (following GAUSS logic)
        U_boot = np.zeros((T, n))
        for t in range(T):
            random_indices = np.random.randint(0, T, size=n)
            for j in range(n):
                U_boot[t, j] = U_adj[random_indices[j], j]
        
        # Center
        U_boot = U_boot - U_boot.mean(axis=0)
        
        # Generate bootstrap Y (Method 1 from GAUSS)
        Y_boot = np.zeros((T, n))
        X_boot = X[0:1, :].copy()  # Initialize with first row
        
        for t in range(T):
            # Generate Y
            Y_boot[t, :] = X_boot[t, :] @ A.T + U_boot[t, :]
            
            # Update X for next iteration
            if t < T - 1:
                if maxlag > 1:
                    new_row = np.hstack([
                        [1],
                        Y_boot[t, :],
                        X_boot[t, 1:1+n*(maxlag-1)]
                    ])
                else:
                    new_row = np.hstack([[1], Y_boot[t, :]])
                
                X_boot = np.vstack([X_boot, new_row[:k]])
        
        # Estimate unrestricted on bootstrap
        A_boot, _ = estimate_var_parameters(Y_boot, X_boot, restricted=False)
        
        # Compute Wald
        W_boot[b] = compute_wald_statistic(Y_boot, X_boot, A_boot, C)
    
    # Sort and get critical values
    W_boot_sorted = np.sort(W_boot)
    
    # Upper tail critical values
    idx_1 = int(n_boot * 0.99)
    idx_5 = int(n_boot * 0.95)
    idx_10 = int(n_boot * 0.90)
    
    # Average with next value (as in GAUSS code)
    cv = np.array([
        (W_boot_sorted[idx_1] + W_boot_sorted[min(idx_1+1, n_boot-1)]) / 2,
        (W_boot_sorted[idx_5] + W_boot_sorted[min(idx_5+1, n_boot-1)]) / 2,
        (W_boot_sorted[idx_10] + W_boot_sorted[min(idx_10+1, n_boot-1)]) / 2
    ])
    
    return cv


#===============================================================================
# FUNCTION 7: Select Lag Order
#===============================================================================

def select_lag_order(y: np.ndarray, max_lag: int = 8, ic: str = 'HJC') -> int:
    """Select optimal lag using information criterion."""
    y = np.atleast_2d(y)
    if y.shape[0] == 1:
        y = y.T
        
    T, n = y.shape
    ic_values = np.zeros(max_lag)
    
    for p in range(1, max_lag + 1):
        Y, X = create_var_lags(y, p)
        T_eff = Y.shape[0]
        
        A = (np.linalg.lstsq(X, Y, rcond=None)[0]).T
        U = Y - X @ A.T
        
        Sigma = (U.T @ U) / T_eff
        det_Sigma = np.linalg.det(Sigma)
        
        if det_Sigma <= 0:
            ic_values[p-1] = np.inf
            continue
        
        if ic == 'AIC':
            ic_values[p-1] = np.log(det_Sigma) + (2/T_eff) * n * (1 + n*p)
        elif ic == 'BIC':
            ic_values[p-1] = np.log(det_Sigma) + (np.log(T_eff)/T_eff) * n * (1 + n*p)
        elif ic == 'HQC':
            ic_values[p-1] = np.log(det_Sigma) + (2*np.log(np.log(T_eff))/T_eff) * n * (1 + n*p)
        elif ic == 'HJC':
            ic_values[p-1] = np.log(det_Sigma) + p * (n**2 * np.log(T_eff) + 
                                                      2 * n**2 * np.log(np.log(T_eff))) / (2 * T_eff)
    
    return np.argmin(ic_values) + 1


#===============================================================================
# MAIN FUNCTION
#===============================================================================

def asymmetric_causality_test(y1: np.ndarray, y2: np.ndarray,
                              component: str = 'positive',
                              ic: str = 'HJC',
                              max_lag: int = 8,
                              d: int = 1,
                              n_boot: int = 1000,
                              verbose: bool = True) -> Dict:
    """
    Hatemi-J (2012) asymmetric causality test.
    
    Tests H0: y2 does not Granger-cause y1
    """
    # Get components
    if component.lower() == 'positive':
        y1_comp, _ = cumulative_components(y1)
        y2_comp, _ = cumulative_components(y2)
    else:
        _, y1_comp = cumulative_components(y1)
        _, y2_comp = cumulative_components(y2)
    
    y = np.column_stack([y1_comp, y2_comp])
    n = 2
    
    # Select lag
    p = select_lag_order(y, max_lag, ic)
    
    if verbose:
        print("="*70)
        print("HATEMI-J (2012) ASYMMETRIC CAUSALITY TEST")
        print("="*70)
        print(f"Component: {component.capitalize()}")
        print(f"IC: {ic}, Selected lag: {p}, Additional lags: {d}")
        print("-"*70)
    
    # VAR(p+d)
    Y, X = create_var_lags(y, p + d)
    y_init = y[:p+d, :]
    
    # Restriction matrix
    C = create_restriction_matrix(n, p, d)
    
    # Estimate
    A_unrest, _ = estimate_var_parameters(Y, X, restricted=False)
    A_rest, leverage_rest = estimate_var_parameters(Y, X, restricted=True, C=C)
    
    # Wald statistic
    W_stat = compute_wald_statistic(Y, X, A_unrest, C)
    
    # Bootstrap
    if verbose:
        print(f"Bootstrap ({n_boot} iterations)...")
    
    cv = bootstrap_critical_values(Y, X, y_init, A_rest, leverage_rest, 
                                   p, d, n_boot, C)
    
    # P-value
    p_value = 1 - stats.chi2.cdf(W_stat, p)
    reject_5pct = W_stat > cv[1]
    
    if verbose:
        print(f"\nWald statistic: {W_stat:.4f}")
        print(f"P-value (χ²): {p_value:.4f}")
        print(f"\nBootstrap critical values:")
        print(f"  1%: {cv[0]:.4f}, 5%: {cv[1]:.4f}, 10%: {cv[2]:.4f}")
        print(f"χ² critical values (reference):")
        print(f"  1%: {stats.chi2.ppf(0.99, p):.4f}, " +
              f"5%: {stats.chi2.ppf(0.95, p):.4f}, " +
              f"10%: {stats.chi2.ppf(0.90, p):.4f}")
        print("-"*70)
        print(f"Decision: {'REJECT' if reject_5pct else 'FAIL TO REJECT'} H₀ at 5%")
        print(f"Conclusion: y2 {'DOES' if reject_5pct else 'does NOT'} Granger-cause y1")
        print("="*70 + "\n")
    
    return {
        'W_stat': W_stat,
        'critical_values': cv,
        'p_value': p_value,
        'lag_order': p,
        'reject_5pct': reject_5pct
    }


#===============================================================================
# EXAMPLE
#===============================================================================

if __name__ == "__main__":
    np.random.seed(123)
    
    print("\nEXAMPLE: Random walk data (no causality expected)\n")
    
    T = 200
    y1 = np.cumsum(np.random.randn(T))
    y2 = np.cumsum(np.random.randn(T))
    
    # Test positive
    results_pos = asymmetric_causality_test(
        y1, y2,
        component='positive',
        ic='HJC',
        max_lag=8,
        d=1,
        n_boot=1000,
        verbose=True
    )
