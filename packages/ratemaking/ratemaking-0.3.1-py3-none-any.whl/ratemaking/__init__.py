"""
Ratemaking Tools: A comprehensive Python library for P&C actuarial ratemaking

This package provides tools for:
- Credibility analysis (classical, Bühlmann, Bayesian)
- Complement calculations (First-Dollar methods)
- Trending analysis (coming soon)
- Exposure calculations (coming soon)
- Data processing utilities (coming soon)

For backward compatibility, all credibility functions are available at the top level.
For organized access, use the submodules: credibility, complements, trending, exposure, utils.
"""

# Import all credibility tools for backward compatibility
from .credibility import (
    # Classical credibility functions
    classical_full_credibility_frequency,
    classical_full_credibility_severity, 
    classical_full_credibility_pure_premium,
    classical_partial_credibility,
    
    # Bühlmann credibility types and functions
    BuhlmannInputs, 
    BuhlmannStraubInputs, 
    BuhlmannResult,
    buhlmann, 
    buhlmann_straub,
    
    # Bayesian credibility types and functions
    PoissonGammaPosterior, 
    BetaBinomialPosterior, 
    NormalNormalPosterior,
    bayes_poisson_gamma, 
    bayes_beta_binomial, 
    bayes_normal_known_var,
)

# Submodule imports (recommended for new code)
from . import credibility
from . import complements
from . import trending
from . import exposure
from . import utils

__version__ = "0.3.0"

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
    
    # Submodules
    'credibility',
    'complements',
    'trending', 
    'exposure',
    'utils',
]
