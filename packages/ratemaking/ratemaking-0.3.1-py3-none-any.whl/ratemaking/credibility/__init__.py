"""
Actuarial credibility calculation tools

This subpackage provides comprehensive credibility methods including:
- Classical (Limited Fluctuation) credibility
- Bühlmann and Bühlmann-Straub credibility  
- Bayesian credibility with conjugate priors
"""

from .classical import (
    classical_full_credibility_frequency,
    classical_full_credibility_severity, 
    classical_full_credibility_pure_premium,
    classical_partial_credibility,
)

from .buhlmann import (
    BuhlmannInputs, 
    BuhlmannStraubInputs, 
    BuhlmannResult,
    buhlmann, 
    buhlmann_straub,
)

from .bayesian import (
    PoissonGammaPosterior, 
    BetaBinomialPosterior, 
    NormalNormalPosterior,
    bayes_poisson_gamma, 
    bayes_beta_binomial, 
    bayes_normal_known_var,
)

__all__ = [
    # Classical credibility functions
    'classical_full_credibility_frequency',
    'classical_full_credibility_severity', 
    'classical_full_credibility_pure_premium',
    'classical_partial_credibility',
    
    # Bühlmann credibility types and functions
    'BuhlmannInputs', 
    'BuhlmannStraubInputs', 
    'BuhlmannResult',
    'buhlmann', 
    'buhlmann_straub',
    
    # Bayesian credibility types and functions
    'PoissonGammaPosterior', 
    'BetaBinomialPosterior', 
    'NormalNormalPosterior',
    'bayes_poisson_gamma', 
    'bayes_beta_binomial', 
    'bayes_normal_known_var',
]
