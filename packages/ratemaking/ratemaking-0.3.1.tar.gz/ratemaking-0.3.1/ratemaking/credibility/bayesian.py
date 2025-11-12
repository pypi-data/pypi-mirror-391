"""
Bayesian credibility calculation tools with conjugate priors

This module provides functions for Bayesian credibility using conjugate
prior-likelihood pairs for common actuarial distributions.
"""

from dataclasses import dataclass


@dataclass
class PoissonGammaPosterior:
    alpha: float
    beta: float
    mean: float           # posterior mean of λ
    credibility_Z: float  # weight on sample rate vs prior mean (n / (n + beta))
    prior_mean: float
    sample_rate: float


def bayes_poisson_gamma(prior_alpha: float, prior_beta: float,
                        total_counts: float, total_exposure: float) -> PoissonGammaPosterior:
    """
    Conjugate update for Poisson rate λ with Gamma(α, β) prior (shape α, rate β).
    Observations: total_counts over total_exposure (so sample rate = counts/exposure).
    Posterior: α' = α + counts, β' = β + exposure.
    """
    if prior_alpha <= 0 or prior_beta <= 0:
        raise ValueError("Gamma prior α, β must be > 0.")
    if total_counts < 0 or total_exposure <= 0:
        raise ValueError("Counts ≥ 0 and exposure > 0 required.")

    alpha_p = prior_alpha + total_counts
    beta_p = prior_beta + total_exposure
    prior_mean = prior_alpha / prior_beta
    sample_rate = total_counts / total_exposure
    posterior_mean = alpha_p / beta_p

    # Credibility form: posterior_mean = Z * sample_rate + (1-Z) * prior_mean
    # For Gamma–Poisson, Z = total_exposure / (total_exposure + prior_beta)
    Z = total_exposure / (total_exposure + prior_beta)

    return PoissonGammaPosterior(alpha=alpha_p, beta=beta_p, mean=posterior_mean,
                                 credibility_Z=Z, prior_mean=prior_mean,
                                 sample_rate=sample_rate)


@dataclass
class BetaBinomialPosterior:
    a: float
    b: float
    mean: float
    credibility_Z: float  # n / (n + a + b)
    prior_mean: float
    sample_rate: float


def bayes_beta_binomial(prior_a: float, prior_b: float,
                        successes: int, trials: int) -> BetaBinomialPosterior:
    """
    Conjugate update for Bernoulli probability p with Beta(a,b) prior.
    Posterior: a' = a + s, b' = b + (n - s).
    Credibility form has weight n / (n + (a + b)).
    """
    if prior_a <= 0 or prior_b <= 0:
        raise ValueError("Beta prior a, b must be > 0.")
    if not (0 <= successes <= trials):
        raise ValueError("0 ≤ successes ≤ trials required.")
    a_p = prior_a + successes
    b_p = prior_b + (trials - successes)
    prior_mean = prior_a / (prior_a + prior_b)
    sample_rate = successes / trials if trials > 0 else 0.0
    mean = a_p / (a_p + b_p)
    Z = trials / (trials + prior_a + prior_b)
    return BetaBinomialPosterior(a=a_p, b=b_p, mean=mean, credibility_Z=Z,
                                 prior_mean=prior_mean, sample_rate=sample_rate)


@dataclass
class NormalNormalPosterior:
    mu: float
    tau2: float  # posterior variance of the mean
    credibility_Z: float  # weight on sample mean vs prior mean
    prior_mean: float
    sample_mean: float


def bayes_normal_known_var(prior_mean: float, prior_var: float,
                           sample_mean: float, known_var: float, n: int) -> NormalNormalPosterior:
    """
    Conjugate Normal–Normal with known variance σ^2 (per observation).
    Prior: θ ~ Normal(m0, v0). Data: x̄ with variance σ^2/n.
    Posterior mean is a credibility blend with weight Z = v0 / (v0 + σ^2/n) on sample mean.
    """
    if prior_var <= 0 or known_var <= 0 or n <= 0:
        raise ValueError("prior_var, known_var > 0 and n > 0 required.")
    v_data = known_var / n
    Z = prior_var / (prior_var + v_data)  # NOTE: This is the weight on the SAMPLE mean
    mu_post = Z * sample_mean + (1.0 - Z) * prior_mean
    tau2_post = 1.0 / (1.0 / prior_var + n / known_var)
    return NormalNormalPosterior(mu=mu_post, tau2=tau2_post, credibility_Z=Z,
                                 prior_mean=prior_mean, sample_mean=sample_mean)


__all__ = [
    'PoissonGammaPosterior', 
    'BetaBinomialPosterior', 
    'NormalNormalPosterior',
    'bayes_poisson_gamma', 
    'bayes_beta_binomial', 
    'bayes_normal_known_var'
]
