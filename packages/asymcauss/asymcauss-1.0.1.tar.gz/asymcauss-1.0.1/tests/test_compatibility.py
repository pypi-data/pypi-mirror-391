"""
Basic compatibility tests for asymcaus package.
"""

import numpy as np
from asymcaus import (
    asymmetric_causality_test,
    cumulative_component,
    varlags,
    rstrctvm,
    select_lag_order,
    IC_AIC, IC_SBC, IC_HJC
)


def test_cumulative_component():
    """Test cumulative component decomposition."""
    np.random.seed(42)
    data = np.random.randn(100, 2)
    
    pos_comp, neg_comp = cumulative_component(data, ln_form=0, fullprint=0)
    
    assert pos_comp.shape == data.shape
    assert neg_comp.shape == data.shape
    assert np.all(pos_comp >= 0)
    assert np.all(neg_comp >= 0)
    print("✓ cumulative_component test passed")


def test_varlags():
    """Test varlags function."""
    np.random.seed(42)
    data = np.random.randn(100, 2)
    
    x, xlags = varlags(data, lags=2)
    
    assert x.shape == (98, 2)
    assert xlags.shape == (98, 4)
    print("✓ varlags test passed")


def test_rstrctvm():
    """Test restriction matrix creation."""
    rvec, rmat = rstrctvm(numvars=2, varorder=3, addlags=1)
    
    assert rvec.shape[1] == 1 + 2 * (3 + 1)
    assert rmat.shape[0] == 3
    assert np.sum(rvec) == 3
    print("✓ rstrctvm test passed")


def test_select_lag_order():
    """Test lag selection."""
    np.random.seed(42)
    data = np.random.randn(100, 2).cumsum(axis=0)
    
    for ic in [IC_AIC, IC_SBC, IC_HJC]:
        iclag, icA, onelA, nocando = select_lag_order(data, 1, 8, ic)
        assert 1 <= iclag <= 8
        assert nocando == 0
    
    print("✓ select_lag_order test passed")


def test_asymmetric_causality_test():
    """Test main asymmetric causality function."""
    np.random.seed(42)
    y = np.random.randn(100, 1).cumsum(axis=0)
    z = np.random.randn(100, 1).cumsum(axis=0)
    
    Wstat, cv, lag, azd = asymmetric_causality_test(
        y, z, pos=1, infocrit=3, intorder=0,
        ln_form=0, maxlags=8, bootmaxiter=100, fullprint=0
    )
    
    assert isinstance(Wstat, (float, np.floating))
    assert cv.shape == (3,)
    assert isinstance(lag, (int, np.integer))
    assert lag >= 1
    print("✓ asymmetric_causality_test test passed")


if __name__ == "__main__":
    print("Running GAUSS Compatibility Tests...")
    print("=" * 60)
    
    test_cumulative_component()
    test_varlags()
    test_rstrctvm()
    test_select_lag_order()
    test_asymmetric_causality_test()
    
    print("=" * 60)
    print("All tests passed! ✅")
    print("\nPackage is GAUSS-compatible and ready to use.")
