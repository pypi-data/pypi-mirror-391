# pytest tests for credibility tools

import pytest
from ratemaking import (
    # Classical credibility
    classical_full_credibility_frequency,
    classical_full_credibility_severity,
    classical_full_credibility_pure_premium,
    classical_partial_credibility,
    
    # Bühlmann credibility
    BuhlmannInputs,
    BuhlmannStraubInputs,
    buhlmann,
    buhlmann_straub,
    
    # Bayesian credibility
    bayes_poisson_gamma,
    bayes_beta_binomial,
    bayes_normal_known_var,
)


# -----------------------------
# Classical (limited fluctuation)
# -----------------------------
def test_classical_full_credibility_frequency():
    """Test the classical full credibility for frequency (Poisson)."""
    p = 0.95  # confidence level
    k = 0.05  # tolerance
    n_full = classical_full_credibility_frequency(p, k)
    
    # For 95% confidence and 5% tolerance, should be around 1537
    assert isinstance(n_full, float)
    assert n_full > 1500
    assert n_full < 1600


def test_classical_partial_credibility():
    """Test partial credibility calculation."""
    n = 1000  # actual exposure
    n_full = 1600  # full credibility standard
    z = classical_partial_credibility(n, n_full)
    
    # Z should be sqrt(1000/1600) = sqrt(0.625) ≈ 0.791
    expected_z = (1000 / 1600) ** 0.5
    assert abs(z - expected_z) < 0.001


def test_classical_full_credibility_pure_premium():
    """Test pure premium credibility with severity variation."""
    cv_sev = 0.3  # coefficient of variation for severity
    p = 0.95
    k = 0.05
    n_full = classical_full_credibility_pure_premium(cv_sev, p, k)
    
    # Should be higher than frequency-only due to severity variation
    n_full_freq = classical_full_credibility_frequency(p, k)
    assert n_full > n_full_freq


# ---------
# Bühlmann
# ---------
def test_buhlmann_basic():
    """Test basic Bühlmann credibility estimation."""
    data = {
        "risk_1": [100, 120, 110],
        "risk_2": [200, 180, 190],
        "risk_3": [150, 160, 140]
    }
    
    inputs = BuhlmannInputs(data=data)
    result = buhlmann(inputs)
    
    # Check that result has expected structure
    assert hasattr(result, 'mu')
    assert hasattr(result, 'EPV')
    assert hasattr(result, 'VHM')
    assert hasattr(result, 'K')
    assert hasattr(result, 'Z_by_risk')
    assert hasattr(result, 'estimate_by_risk')
    
    # Check that all risks have credibility weights
    assert 'risk_1' in result.Z_by_risk
    assert 'risk_2' in result.Z_by_risk
    assert 'risk_3' in result.Z_by_risk
    
    # Credibility weights should be between 0 and 1
    for z in result.Z_by_risk.values():
        assert 0 <= z <= 1


# -----------------------------
# Bayesian (Poisson–Gamma)
# -----------------------------
def test_bayes_poisson_gamma():
    """Test Poisson-Gamma conjugate updating."""
    prior_alpha = 2.0
    prior_beta = 100.0
    total_counts = 15
    total_exposure = 120
    
    result = bayes_poisson_gamma(prior_alpha, prior_beta, total_counts, total_exposure)
    
    # Check structure
    assert hasattr(result, 'alpha')
    assert hasattr(result, 'beta')
    assert hasattr(result, 'mean')
    assert hasattr(result, 'credibility_Z')
    
    # Check posterior parameters
    expected_alpha = prior_alpha + total_counts  # 2 + 15 = 17
    expected_beta = prior_beta + total_exposure  # 100 + 120 = 220
    
    assert abs(result.alpha - expected_alpha) < 0.001
    assert abs(result.beta - expected_beta) < 0.001
    
    # Check posterior mean
    expected_mean = expected_alpha / expected_beta  # 17/220
    assert abs(result.mean - expected_mean) < 0.001


def test_bayes_beta_binomial():
    """Test Beta-Binomial conjugate updating."""
    prior_a = 1.0
    prior_b = 1.0
    successes = 8
    trials = 20
    
    result = bayes_beta_binomial(prior_a, prior_b, successes, trials)
    
    # Check posterior parameters
    expected_a = prior_a + successes  # 1 + 8 = 9
    expected_b = prior_b + (trials - successes)  # 1 + 12 = 13
    
    assert abs(result.a - expected_a) < 0.001
    assert abs(result.b - expected_b) < 0.001
    
    # Check posterior mean
    expected_mean = expected_a / (expected_a + expected_b)  # 9/22
    assert abs(result.mean - expected_mean) < 0.001


def test_input_validation():
    """Test that functions properly validate inputs."""
    # Classical credibility
    with pytest.raises(ValueError):
        classical_full_credibility_frequency(p=1.5, k=0.05)  # p > 1
    
    with pytest.raises(ValueError):
        classical_partial_credibility(n=-1, n_full=100)  # negative n
    
    # Bayesian
    with pytest.raises(ValueError):
        bayes_poisson_gamma(prior_alpha=-1, prior_beta=1, total_counts=5, total_exposure=10)  # negative alpha


if __name__ == "__main__":
    pytest.main([__file__])
