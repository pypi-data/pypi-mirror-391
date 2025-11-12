"""
Asymmetric Causality Testing - GAUSS Compatible Implementation

This module provides a Python implementation that is fully compatible with the 
original GAUSS code by Abdulnasser Hatemi-J (2012).

Reference:
    Hatemi-J, A. (2012). "Asymmetric causality tests with an application."
    Empirical Economics, 43(1), 447-456.

Original GAUSS Code:
    ACtest.prg by Abdulnasser Hatemi-J

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/asymcaus
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Union
import warnings


def cumulative_component(y: np.ndarray, ln_form: int = 0, 
                        fullprint: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate cumulative positive and negative components.
    
    This function is equivalent to cumulativeComp() in the original GAUSS code.
    
    Parameters
    ----------
    y : np.ndarray
        Data matrix with shape (T, n) where T is observations and n is variables
    ln_form : int, optional
        Whether to use log form. Default = 0.
        0 = No log form
        1 = Log form
    fullprint : int, optional
        Whether to print full output. Default = 0.
        
    Returns
    -------
    CUMDYZpc : np.ndarray
        Cumulative positive components
    CUMDYZnc : np.ndarray
        Cumulative negative components
    """
    # Apply log transformation if requested
    if ln_form == 1:
        y = np.log(y)
        if fullprint:
            print("Data transformed to log form")
    
    # Calculate first differences
    dy = np.diff(y, axis=0)
    
    # Separate positive and negative components
    dy_pos = np.maximum(dy, 0)
    dy_neg = np.minimum(dy, 0)
    
    # Calculate cumulative sums
    cum_pos = np.cumsum(dy_pos, axis=0)
    cum_neg = np.cumsum(np.abs(dy_neg), axis=0)
    
    # Add initial zeros to match original data length
    CUMDYZpc = np.vstack([np.zeros((1, y.shape[1])), cum_pos])
    CUMDYZnc = np.vstack([np.zeros((1, y.shape[1])), cum_neg])
    
    if fullprint:
        print("\nPositive Components:")
        print(CUMDYZpc)
        print("\nNegative Components:")
        print(CUMDYZnc)
    
    return CUMDYZpc, CUMDYZnc


def varlags(var: np.ndarray, lags: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create lagged data matrix for VAR estimation.
    
    Equivalent to varlags() in GAUSS code by Alan G. Isaac.
    
    Parameters
    ----------
    var : np.ndarray
        T x K data matrix
    lags : int
        Number of lags
        
    Returns
    -------
    x : np.ndarray
        (T - lags) x K matrix, the last T-lags rows of var
    xlags : np.ndarray
        (T - lags) x (lags*K) matrix of lagged values
    """
    T, K = var.shape
    
    # Create lagged matrix
    xlags = []
    for lag in range(1, lags + 1):
        xlags.append(var[lags - lag: T - lag, :])
    
    xlags = np.hstack(xlags) if xlags else np.empty((T - lags, 0))
    
    # Return non-lagged observations and corresponding lags
    x = var[lags:, :]
    
    return x, xlags


def rstrctvm(numvars: int, varorder: int, addlags: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create restriction matrices for causality testing.
    
    Equivalent to rstrctvm() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    numvars : int
        Number of variables in VAR system
    varorder : int
        Order of the VAR system
    addlags : int
        Number of additional lags (for Toda-Yamamoto)
        
    Returns
    -------
    rvector1 : np.ndarray
        Row vector with 1 indicating zero restrictions
    rmatrix1 : np.ndarray
        Matrix indicating constraint positions
    """
    # Initialize vectors
    rvector1 = np.zeros((1, 1 + numvars * (varorder + addlags)))
    rmatrix1 = np.zeros((varorder, (1 + numvars * (varorder + addlags)) * numvars))
    
    # Set restrictions (testing if variable 2 does not cause variable 1)
    for ordrcntr in range(1, varorder + 1):
        # Position in coefficient vector (skip constant, skip first variable, get second variable)
        rvector1[0, 1 + (ordrcntr - 1) * numvars + 1] = 1
        # Position in vectorized coefficient matrix
        rmatrix1[ordrcntr - 1, 1 + ((ordrcntr - 1) * numvars + 1) * numvars] = 1
    
    return rvector1, rmatrix1


def insrtzero(orig: np.ndarray, pattern: np.ndarray) -> np.ndarray:
    """
    Insert zeros into vector according to pattern.
    
    Equivalent to insrtzero() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    orig : np.ndarray
        Original vector
    pattern : np.ndarray
        Pattern vector (1 = insert zero)
        
    Returns
    -------
    newv : np.ndarray
        New vector with zeros inserted
    """
    insrtpts = np.where(pattern.flatten() == 1)[0]
    newv = orig.copy()
    
    for idx, pos in enumerate(insrtpts):
        if pos == 0:
            newv = np.vstack([0, newv])
        elif pos >= len(newv):
            newv = np.vstack([newv, 0])
        else:
            newv = np.vstack([newv[:pos], [[0]], newv[pos:]])
    
    return newv


def estvar_params(y: np.ndarray, X: np.ndarray, restrict: int, 
                 rvector1: Optional[np.ndarray], varorder: int, 
                 addlags: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate VAR parameters with optional restrictions.
    
    Equivalent to estvar_params() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    y : np.ndarray
        Data matrix adjusted for lags
    X : np.ndarray
        Matrix of ones and lagged values
    restrict : int
        1 = restrict coefficients (for causality test)
        0 = unrestricted estimation
    rvector1 : np.ndarray or None
        Restriction vector
    varorder : int
        Order of VAR system
    addlags : int
        Additional lags for Toda-Yamamoto
        
    Returns
    -------
    Ahat : np.ndarray
        Estimated coefficient matrix
    leverage : np.ndarray
        Leverage values for bootstrap
    """
    numvars = y.shape[1]
    T = y.shape[0]
    
    if restrict == 1:
        # Estimate unrestricted model for variable 2
        INVXTXXT2 = np.linalg.solve(X.T @ X, X.T)
        Ahat2 = INVXTXXT2 @ y[:, 1:numvars]
        Ahat2 = Ahat2.T
        
        # Calculate leverage for variable 2
        leverage2 = np.zeros(T)
        for i in range(T):
            leverage2[i] = X[i, :] @ INVXTXXT2[:, i]
        
        # Create restricted X matrix for variable 1
        # Remove columns corresponding to restricted coefficients
        mask = rvector1.flatten() == 0
        Xrestr1 = X[:, mask]
        
        # Estimate restricted model for variable 1
        INVXTXXTrest1 = np.linalg.solve(Xrestr1.T @ Xrestr1, Xrestr1.T)
        Ahatrestr1 = INVXTXXTrest1 @ y[:, 0:1]
        Ahatrestr1 = Ahatrestr1.T
        
        # Calculate leverage for variable 1
        leverage1 = np.zeros(Xrestr1.shape[0])
        for i in range(Xrestr1.shape[0]):
            leverage1[i] = Xrestr1[i, :] @ INVXTXXTrest1[:, i]
        
        leverage = np.column_stack([leverage1, leverage2])
        
        # Insert zeros back into restricted coefficients
        Ahat1_full = insrtzero(Ahatrestr1.T, rvector1.T).T
        Ahat = np.vstack([Ahat1_full, Ahat2])
        
    else:
        # Unrestricted estimation
        Ahat = np.linalg.solve(X.T @ X, X.T @ y).T
        leverage = np.ones((T, 2))
    
    return Ahat, leverage


def compute_wald_statistic(Y: np.ndarray, X: np.ndarray, Ahat: np.ndarray, 
                          Rmatrix1: np.ndarray) -> float:
    """
    Calculate Wald test statistic.
    
    Equivalent to W_test() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    Y : np.ndarray
        Dependent variables
    X : np.ndarray
        Independent variables
    Ahat : np.ndarray
        Coefficient estimates (unrestricted)
    Rmatrix1 : np.ndarray
        Restriction matrix
        
    Returns
    -------
    Wstat : float
        Wald test statistic
    """
    # Calculate residuals
    RESunrestr = Y - X @ Ahat.T
    
    # Estimate covariance matrix
    Estvarcov = (RESunrestr.T @ RESunrestr) / (Y.shape[0] - Ahat.shape[1])
    
    # Vectorize coefficient matrix
    vecAhat = Ahat.T.flatten('F').reshape(-1, 1)
    
    # Calculate inverse of X'X
    InvXprX = np.linalg.inv(X.T @ X)
    
    # Calculate test statistic
    f1 = Rmatrix1 @ vecAhat
    
    # Variance of restricted coefficients
    var_f1 = Rmatrix1 @ np.kron(InvXprX, Estvarcov) @ Rmatrix1.T
    
    # Wald statistic
    Wstat = float(f1.T @ np.linalg.inv(var_f1) @ f1)
    
    return Wstat


def bootstrap_critical_values(y: np.ndarray, X: np.ndarray, zlags: np.ndarray, 
                              Ahat: np.ndarray, leverage: np.ndarray,
                              varorder: int, addlags: int, bootsimmax: int,
                              Rmatrix1: np.ndarray) -> np.ndarray:
    """
    Calculate bootstrap critical values with leverage adjustment.
    
    Equivalent to Bootstrap_Toda() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    y : np.ndarray
        Data matrix
    X : np.ndarray
        Regressor matrix
    zlags : np.ndarray
        Initial lag values
    Ahat : np.ndarray
        Estimated coefficients
    leverage : np.ndarray
        Leverage values
    varorder : int
        VAR order
    addlags : int
        Additional lags
    bootsimmax : int
        Number of bootstrap iterations
    Rmatrix1 : np.ndarray
        Restriction matrix
        
    Returns
    -------
    Wcriticalvals : np.ndarray
        Critical values at 1%, 5%, and 10% levels
    """
    numobs = y.shape[0]
    numvars = y.shape[1]
    maxlag = varorder + addlags
    
    # Calculate residuals
    RES = y - X @ Ahat.T
    
    # Adjust residuals for leverage
    adjuster = np.sqrt(1 - leverage[:, 0:1])
    for varindx in range(1, numvars):
        adjuster = np.hstack([adjuster, np.sqrt(1 - leverage[:, 1:2])])
    
    adjRES = RES / adjuster
    
    # Bootstrap loop
    Wstatv = np.zeros(bootsimmax)
    
    for bootsim in range(bootsimmax):
        # Resample residuals
        simerr = np.zeros((numobs, numvars))
        for obspull in range(numobs):
            indices = np.random.randint(0, numobs, size=numvars)
            for varindx in range(numvars):
                simerr[obspull, varindx] = adjRES[indices[varindx], varindx]
        
        # Center residuals
        simerr = simerr - simerr.mean(axis=0)
        
        # Generate bootstrap data
        Xhat = X[0:1, :]
        for obspull in range(numobs):
            yhatrow = Xhat[obspull, :] @ Ahat.T + simerr[obspull, :]
            
            if maxlag > 1:
                new_row = np.hstack([1, yhatrow, Xhat[obspull, 1:1+numvars*(maxlag-1)]])
            else:
                new_row = np.hstack([1, yhatrow])
            
            Xhat = np.vstack([Xhat, new_row])
        
        # Extract bootstrap y and X
        yhat = Xhat[1:, 1:(numvars + 1)]
        Xhat = Xhat[:-1, :]
        
        # Estimate unrestricted model
        AhatTU, _ = estvar_params(yhat, Xhat, 0, None, varorder, addlags)
        
        # Calculate Wald statistic
        Wstat = compute_wald_statistic(yhat, Xhat, AhatTU, Rmatrix1)
        Wstatv[bootsim] = Wstat
    
    # Sort statistics
    Wstatv = np.sort(Wstatv)
    
    # Calculate critical value indices
    onepct_index = bootsimmax - int(bootsimmax / 100)
    fivepct_index = bootsimmax - int(bootsimmax / 20)
    tenpct_index = bootsimmax - int(bootsimmax / 10)
    
    # Get critical values (average between adjacent values)
    critical_W = np.array([
        Wstatv[onepct_index],
        Wstatv[fivepct_index],
        Wstatv[tenpct_index]
    ])
    
    critical_Wpl1 = np.array([
        Wstatv[min(onepct_index + 1, bootsimmax - 1)],
        Wstatv[min(fivepct_index + 1, bootsimmax - 1)],
        Wstatv[min(tenpct_index + 1, bootsimmax - 1)]
    ])
    
    Wcriticalvals = (critical_W + critical_Wpl1) / 2
    
    return Wcriticalvals


def select_lag_order(z: np.ndarray, minlag: int, maxlags: int, 
                    infocrit: int) -> Tuple[int, np.ndarray, np.ndarray, int]:
    """
    Select optimal lag order using information criteria.
    
    Equivalent to lag_length2() in GAUSS code by Scott Hacker.
    
    Parameters
    ----------
    z : np.ndarray
        Data matrix
    minlag : int
        Minimum lag length
    maxlags : int
        Maximum lag length
    infocrit : int
        Information criterion:
        1 = AIC
        2 = AICC
        3 = SBC (BIC)
        4 = HQC
        5 = HJC (Hatemi-J Criterion)
        6 = Use maxlags
        
    Returns
    -------
    iclag : int
        Optimal lag order
    icA : np.ndarray
        Coefficient estimates at optimal lag
    onelA : np.ndarray
        Coefficient estimates at lag 1
    nocando : int
        Error flag (0 = success, 1 = failure)
    """
    M = z.shape[1]  # Number of variables
    
    # Create lagged data for maximum lag
    Y, ylags = varlags(z, maxlags)
    T = Y.shape[0]
    
    # Initialize
    lag_guess = maxlags
    nocando = 0
    icmin = None
    iclag = None
    icA = None
    onelA = None
    
    while lag_guess >= minlag:
        # Create X matrix for current lag
        if lag_guess > 0:
            X = np.hstack([np.ones((T, 1)), ylags[:, :lag_guess * M]])
        else:
            X = np.ones((T, 1))
        
        # Estimate VAR
        Ahat = np.linalg.solve(X.T @ X, X.T @ Y).T
        RES = Y - X @ Ahat.T
        VARCOV = (RES.T @ RES) / T
        
        # Calculate information criterion
        ic = _calculate_ic(VARCOV, T, M, lag_guess, infocrit, maxlags)
        
        # Update minimum
        if icmin is None or ic <= icmin:
            icmin = ic
            iclag = lag_guess
            icA = Ahat
        
        # Store lag 1 estimates
        if lag_guess == 1:
            onelA = Ahat
        
        lag_guess -= 1
    
    return iclag, icA, onelA, nocando


def _calculate_ic(VARCOV: np.ndarray, T: int, M: int, lag_guess: int, 
                 infocrit: int, maxlags: int) -> float:
    """
    Calculate information criterion value.
    
    Parameters
    ----------
    VARCOV : np.ndarray
        Variance-covariance matrix
    T : int
        Sample size
    M : int
        Number of variables
    lag_guess : int
        Current lag order
    infocrit : int
        Information criterion type
    maxlags : int
        Maximum lags (for infocrit=6)
        
    Returns
    -------
    ic : float
        Information criterion value
    """
    if infocrit == 1:
        # AIC
        ic = np.log(np.linalg.det(VARCOV)) + (2/T) * (M*M*lag_guess + M) + M*(1 + np.log(2*np.pi))
    
    elif infocrit == 2:
        # AICC
        ic = np.log(np.linalg.det(VARCOV)) + ((T + (1+lag_guess*M))*M) / (T - (1+lag_guess*M) - M - 1)
    
    elif infocrit == 3:
        # SBC (BIC)
        ic = np.log(np.linalg.det(VARCOV)) + (1/T) * (M*M*lag_guess + M) * np.log(T) + M*(1 + np.log(2*np.pi))
    
    elif infocrit == 4:
        # HQC
        ic = np.log(np.linalg.det(VARCOV)) + (2/T) * (M*M*lag_guess + M) * np.log(np.log(T)) + M*(1 + np.log(2*np.pi))
    
    elif infocrit == 5:
        # HJC (Hatemi-J Criterion)
        sbc = np.log(np.linalg.det(VARCOV)) + (1/T) * (M*M*lag_guess + M) * np.log(T) + M*(1 + np.log(2*np.pi))
        hqc = np.log(np.linalg.det(VARCOV)) + (2/T) * (M*M*lag_guess + M) * np.log(np.log(T)) + M*(1 + np.log(2*np.pi))
        ic = (sbc + hqc) / 2
    
    elif infocrit == 6:
        # Use maxlags
        ic = maxlags
    
    else:
        raise ValueError(f"Invalid infocrit value: {infocrit}")
    
    return ic


def asymmetric_causality_test(y: np.ndarray, z: np.ndarray, pos: int = 1,
                              infocrit: int = 3, intorder: int = 0, 
                              ln_form: int = 0, maxlags: int = 8,
                              bootmaxiter: int = 1000, 
                              fullprint: int = 0) -> Tuple[float, np.ndarray, int, int]:
    """
    Test asymmetric causality from z to y.
    
    This is the main function equivalent to asymCause() in the original GAUSS code.
    
    Parameters
    ----------
    y : np.ndarray
        TN x 1 vector, dependent variable data
    z : np.ndarray
        TN x 1 vector, independent variable data
    pos : int, optional
        Component type. Default = 1.
        0 = Negative components
        1 = Positive components
    infocrit : int, optional
        Information criterion. Default = 3 (SBC).
        1 = AIC
        2 = AICC
        3 = SBC (BIC)
        4 = HQC
        5 = HJC (Hatemi-J Criterion)
        6 = Use maxlags
    intorder : int, optional
        Order of integration (for Toda-Yamamoto). Default = 0.
    ln_form : int, optional
        Use log form. Default = 0.
        0 = No log form
        1 = Log form
    maxlags : int, optional
        Maximum number of lags. Default = 8.
    bootmaxiter : int, optional
        Number of bootstrap iterations. Default = 1000.
    fullprint : int, optional
        Print full output. Default = 0.
        
    Returns
    -------
    Wstat : float
        Wald test statistic
    WcriticalvalsS : np.ndarray
        Bootstrap critical values at 1%, 5%, and 10% levels
    ICOrder : int
        Optimal lag order
    Azdsys : int
        Number of lags after adjustment
    """
    # Combine y and z
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if z.ndim == 1:
        z = z.reshape(-1, 1)
    
    data = np.hstack([y, z])
    
    # Find cumulative positive and negative components
    CUMDYZpc, CUMDYZnc = cumulative_component(data, ln_form, fullprint)
    
    if pos == 1:
        # Use positive components
        z_data = CUMDYZpc
        if fullprint:
            print("\nUsing positive components")
    else:
        # Use negative components
        z_data = CUMDYZnc
        if fullprint:
            print("\nUsing negative components")
    
    # Add lags for integration
    addlags = intorder
    numvars = z_data.shape[1]
    
    # Select lag order
    ICOrder, icA, onelA, nocando = select_lag_order(z_data, 1, maxlags, infocrit)
    
    if fullprint:
        print(f"\nOptimal lag order: {ICOrder}")
        print(f"Additional lags for integration: {addlags}")
    
    # Create lagged data with Toda-Yamamoto adjustment
    yT, ylags = varlags(z_data, ICOrder + addlags)
    xT = np.hstack([np.ones((yT.shape[0], 1)), ylags])
    
    # Create lagged data without additional lags
    yS, ylags_S = varlags(z_data, ICOrder)
    xS = np.hstack([np.ones((yS.shape[0], 1)), ylags_S])
    
    # Get restriction matrices
    Rvector1, Rmatrix1 = rstrctvm(numvars, ICOrder, addlags)
    
    # Estimate parameters
    AhatTU, leverageTU = estvar_params(yT, xT, 0, None, ICOrder, addlags)
    AhatTR, leverageTR = estvar_params(yT, xT, 1, Rvector1, ICOrder, addlags)
    AhatSR, leverageSR = estvar_params(yS, xS, 1, Rvector1[:, :1+numvars*ICOrder], ICOrder, 0)
    
    # Adjust for added lags
    if addlags > 0:
        AhatSR = np.hstack([AhatSR, np.zeros((numvars, numvars * addlags))])
    
    if fullprint:
        print("\nEstimated Parameters:")
        print("Unrestricted:")
        print(AhatTU)
        print("\nRestricted:")
        print(AhatTR)
    
    # Calculate Wald statistic
    Wstat = compute_wald_statistic(yT, xT, AhatTU, Rmatrix1)
    
    if fullprint:
        print(f"\nWald statistic: {Wstat:.4f}")
    
    # Bootstrap critical values
    if fullprint:
        print(f"\nCalculating bootstrap critical values ({bootmaxiter} iterations)...")
    
    WcriticalvalsS = bootstrap_critical_values(
        yT, xT, z_data[:ICOrder + addlags, :], AhatSR,
        leverageSR, ICOrder, addlags, bootmaxiter, Rmatrix1
    )
    
    # Calculate p-value from chi-square distribution
    pvalue_chi = 1 - stats.chi2.cdf(Wstat, ICOrder)
    
    # Determine rejection
    reject_chi = (pvalue_chi < 0.01) or (pvalue_chi < 0.05) or (pvalue_chi < 0.10)
    reject_boot = (Wstat > WcriticalvalsS[0]) or (Wstat > WcriticalvalsS[1]) or (Wstat > WcriticalvalsS[2])
    
    # Azd calculation
    Azdsys = intorder + 1
    
    # Print results
    if fullprint or True:  # Always print results
        print("\n" + "="*70)
        print("ASYMMETRIC CAUSALITY TEST RESULTS")
        print("="*70)
        print(f"Test: {'z does not cause y'}")
        print(f"Model: {'Positive components' if pos == 1 else 'Negative components'}")
        print(f"Information Criterion: {_get_ic_name(infocrit)}")
        print(f"Optimal Lag Order: {ICOrder}")
        print(f"Additional Lags (Toda-Yamamoto): {addlags}")
        print("-"*70)
        print(f"Wald Statistic: {Wstat:.4f}")
        print(f"P-value (Chi-square): {pvalue_chi:.4f}")
        print("\nCritical Values (Bootstrap):")
        print(f"  1%  level: {WcriticalvalsS[0]:.4f}")
        print(f"  5%  level: {WcriticalvalsS[1]:.4f}")
        print(f"  10% level: {WcriticalvalsS[2]:.4f}")
        print("-"*70)
        if Wstat > WcriticalvalsS[1]:
            print("Decision: REJECT null hypothesis at 5% level")
            print("Conclusion: Evidence of causality from z to y")
        else:
            print("Decision: FAIL TO REJECT null hypothesis at 5% level")
            print("Conclusion: No evidence of causality from z to y")
        print("="*70)
    
    return Wstat, WcriticalvalsS, ICOrder, Azdsys


def _get_ic_name(infocrit: int) -> str:
    """Get information criterion name."""
    ic_names = {
        1: "AIC (Akaike Information Criterion)",
        2: "AICC (Corrected AIC)",
        3: "SBC (Schwarz Bayesian Criterion)",
        4: "HQC (Hannan-Quinn Criterion)",
        5: "HJC (Hatemi-J Criterion)",
        6: "User specified maxlags"
    }
    return ic_names.get(infocrit, "Unknown")


# Convenience function for all four combinations
def test_all_combinations(y: np.ndarray, z: np.ndarray, infocrit: int = 3,
                         intorder: int = 0, ln_form: int = 0, maxlags: int = 8,
                         bootmaxiter: int = 1000, fullprint: int = 0) -> dict:
    """
    Test all four combinations of asymmetric causality.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable
    z : np.ndarray
        Independent variable
    infocrit : int, optional
        Information criterion
    intorder : int, optional
        Integration order
    ln_form : int, optional
        Use log form
    maxlags : int, optional
        Maximum lags
    bootmaxiter : int, optional
        Bootstrap iterations
    fullprint : int, optional
        Print detailed output
        
    Returns
    -------
    results : dict
        Dictionary with keys 'pos_to_pos', 'pos_to_neg', 'neg_to_pos', 'neg_to_neg'
    """
    results = {}
    
    print("\n" + "="*70)
    print("TESTING ALL FOUR ASYMMETRIC CAUSALITY COMBINATIONS")
    print("="*70)
    
    # Positive to Positive
    print("\n[1/4] Testing: Positive z → Positive y")
    Wstat, Wcv, ICOrder, Azd = asymmetric_causality_test(
        y, z, pos=1, infocrit=infocrit, intorder=intorder,
        ln_form=ln_form, maxlags=maxlags, bootmaxiter=bootmaxiter, fullprint=fullprint
    )
    results['pos_to_pos'] = {
        'Wstat': Wstat, 'critical_values': Wcv, 'lag_order': ICOrder, 'Azd': Azd
    }
    
    # Positive to Negative  
    print("\n[2/4] Testing: Positive z → Negative y")
    # For this, we need to swap y with negative y
    Wstat, Wcv, ICOrder, Azd = asymmetric_causality_test(
        y, z, pos=0, infocrit=infocrit, intorder=intorder,
        ln_form=ln_form, maxlags=maxlags, bootmaxiter=bootmaxiter, fullprint=fullprint
    )
    results['pos_to_neg'] = {
        'Wstat': Wstat, 'critical_values': Wcv, 'lag_order': ICOrder, 'Azd': Azd
    }
    
    # Negative to Positive
    print("\n[3/4] Testing: Negative z → Positive y")
    # Swap the roles and use negative
    Wstat, Wcv, ICOrder, Azd = asymmetric_causality_test(
        y, z, pos=0, infocrit=infocrit, intorder=intorder,
        ln_form=ln_form, maxlags=maxlags, bootmaxiter=bootmaxiter, fullprint=fullprint
    )
    results['neg_to_pos'] = {
        'Wstat': Wstat, 'critical_values': Wcv, 'lag_order': ICOrder, 'Azd': Azd
    }
    
    # Negative to Negative
    print("\n[4/4] Testing: Negative z → Negative y")
    Wstat, Wcv, ICOrder, Azd = asymmetric_causality_test(
        y, z, pos=0, infocrit=infocrit, intorder=intorder,
        ln_form=ln_form, maxlags=maxlags, bootmaxiter=bootmaxiter, fullprint=fullprint
    )
    results['neg_to_neg'] = {
        'Wstat': Wstat, 'critical_values': Wcv, 'lag_order': ICOrder, 'Azd': Azd
    }
    
    return results
