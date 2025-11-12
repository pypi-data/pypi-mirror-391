# Ratemaking

A comprehensive Python library for Property & Casualty actuarial ratemaking, providing tools for credibility analysis, trending, exposure calculations, and data processing.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Currently Available
- **Credibility Analysis**: Classical, Bühlmann, and Bayesian credibility methods
- **Complement Calculations**: First-Dollar methods from Werner & Modlin Chapter 12
- **Comprehensive Testing**: Test suite with actuarial validation

## Installation

```bash
pip install ratemaking
```

## Quick Start

### Classical Credibility

```python
from ratemaking import (
    classical_full_credibility_frequency,
    classical_partial_credibility
)

# Calculate full credibility standard
n_full = classical_full_credibility_frequency(p=0.95, k=0.05)

# Calculate credibility factor  
z = classical_partial_credibility(n=observed_claims, n_full=n_full)

# Apply credibility blend
estimate = z * observed_rate + (1 - z) * complement_rate
```

### Bühlmann Credibility

```python
from ratemaking import BuhlmannInputs, buhlmann

data = {"risk_1": [1.2, 1.5], "risk_2": [2.1, 1.9]}
result = buhlmann(BuhlmannInputs(data=data))
print(f"Credibility weights: {result.Z_by_risk}")
```

### Bayesian Credibility

```python
from ratemaking import bayes_poisson_gamma

# Poisson-Gamma conjugate updating
posterior = bayes_poisson_gamma(
    prior_alpha=2.0, prior_beta=100.0,
    total_counts=15, total_exposure=120
)
print(f"Posterior mean: {posterior.mean}")
print(f"Credibility weight: {posterior.credibility_Z}")
```

### Complement Calculations

```python
from ratemaking.complements import (
    trended_present_rates_loss_cost,
    trended_present_rates_rate_change_factor,
    larger_group_applied_rate_change_to_present_rate,
    HarwayneInputs,
    harwayne_complement,
)

# Trended present rates method
complement = trended_present_rates_loss_cost(
    present_rate=100.0,
    prior_indicated_factor=1.10,  # 10% indicated
    prior_implemented_factor=1.06,  # 6% implemented 
    loss_trend_annual=0.05,  # 5% annual loss trend
    trend_years=2.0
)

# Harwayne's method for multi-state complements
inputs = HarwayneInputs(
    target_class_exposures=target_exposures,
    target_avg_pure_premium=120.0,
    related_state_class_pp=related_pp_data,
    related_state_class_exposures=related_exposure_data,
    class_of_interest='ClassA'
)
complement = harwayne_complement(inputs)
```

## Package Structure

```
ratemaking/
├── credibility/           # Credibility analysis tools
│   ├── classical.py      # Classical (Limited Fluctuation) credibility
│   ├── buhlmann.py       # Bühlmann & Bühlmann-Straub credibility
│   └── bayesian.py       # Bayesian credibility with conjugate priors
├── complements/          # Complement calculation methods
│   └── first_dollar.py   # First-Dollar methods (Werner & Modlin Ch.12)
├── trending/             # Trending analysis tools (coming soon)
├── exposure/             # Exposure calculation tools (coming soon)
└── utils/                # Data processing utilities (coming soon)
```

## Modular Usage

For organized imports, use the submodules:

```python
# Organized by functionality
from ratemaking.credibility import classical, buhlmann, bayesian
from ratemaking.complements import first_dollar

# Use specific functions
n_full = classical.classical_full_credibility_frequency(p=0.95, k=0.05)
complement = first_dollar.trended_present_rates_loss_cost(...)
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Development

### Setting up for development:

```bash
git clone https://github.com/little-croissant/ratemaking.git
cd ratemaking
pip install -e .
pip install -e ".[test]"
```

## License

MIT License 
