from __future__ import annotations
 
import warnings

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az


def a_metric(
    a: float,
    a_estimate: float,
) -> np.float64:
    """https://doi.org/10.1093/poq/nfi044

    .. reference::
      [...] measure of the predictive accuracy (A) of election polls that permits
      examination of both accuracy and bias [...]
      - Elizabeth A. Martin , Michael W. Traugott , Courtney Kennedy

    :param a: Percentage of valid votes presidential candidate A.
    :param a_estimate: Percentage of valid votes predicted to candidate A.
    """
    estimated_balance = a_estimate / (1 - a_estimate)
    observed_balance = a / (1 - a)
    return np.log(estimated_balance / observed_balance)


def a_std_error(n: float, a_estimate) -> np.float64:
    """https://doi.org/10.1093/poq/nfi044

    Measures the standard error of the A metric, based on delta-Approx method.

    :param n: Poll sample size.
    :param a_estimate: Percentage of valid votes predicted to candidate A.
    """
    return np.sqrt(
        1 / ( n * a_estimate * (1 - a_estimate) )
    )


def b_metric(*a_metrics: np.float64):
    """https://dx.doi.org/10.1093/pan/mpt012

    .. reference::
      [...] polling accuracy measure for multi-party elections based on a generalization
      of Martin, Traugott, and Kennedy's two-party predictive accuracy index. [...]

    :param a_metrics: Estimated A metrics for each participant of a elecion poll.
    """
    k = len(a_metrics)
    return np.sum(np.absolute(a_metrics)) / k


class DirichletTransferring:
    """
    Hierarchical Multinomial-Dirichlet ecological inference model
    (Rosen, Jiang, King & Tanner, 2001), for vote transfer between two rounds.
 
    For each polling station i and each Round 1 option k::
 
        alpha_km  ~ Gamma(lambda1, lambda2)            # shared hyperparameters
        beta_ik   ~ Dirichlet(alpha_k)                 # station-level transfers
        theta_i    = sum_k X_prop[i, k] * beta_ik
        Y_i       ~ Multinomial(n_i, theta_i)
 
    The estimated transition matrix is the aggregate
    ``B_km = sum_i X[i,k] * beta_ikm / sum_i X[i,k]``.
 
    :param draws: Posterior samples per chain.
    :param tune: Tuning iterations.
    :param chains: Number of chains.
    :param random_seed: Random seed.
    :param lambda1: Shape of the Gamma hyperprior on alpha.
    :param lambda2: Rate of the Gamma hyperprior on alpha.
    :param target_accept: NUTS target acceptance (high values help with divergences).
    :param hdi_prob: Probability mass of the HDI.
    """
 
    def __init__(
        self,
        draws=1000,
        tune=1000,
        chains=2,
        random_seed=42,
        lambda1=4.0,
        lambda2=2.0,
        target_accept=0.95,
        hdi_prob=0.94,
    ):
        self.draws = draws
        self.tune = tune
        self.chains = chains
        self.random_seed = random_seed
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.target_accept = target_accept
        self.hdi_prob = hdi_prob

        self.model = None
        self.trace = None
        self.mean_ = None
        self.hdi_low_ = None
        self.hdi_high_ = None
 
    def fit(self, X, Y):
        """
        :param X: Round 1 vote counts, shape (stations, K).
        :param Y: Round 2 vote counts (integers), shape (stations, M).
        """
        X = np.asarray(X, dtype=float)
        Y = np.asarray(Y, dtype=float)

        # Drop stations with no votes in either round
        keep = (X.sum(axis=1) > 0) & (Y.sum(axis=1) > 0)
        X, Y = X[keep], np.round(Y[keep]).astype(int)
        N, K = X.shape
        M = Y.shape[1]

        X_prop = X / X.sum(axis=1, keepdims=True)  # (N, K)
        w = X / X.sum(axis=0, keepdims=True)       # (N, K) weights per origin
        n_votes = Y.sum(axis=1)                    # (N,)

        with pm.Model() as model:
            alpha = pm.Gamma("alpha", alpha=self.lambda1, beta=self.lambda2, shape=(K, M))
            beta_i = pm.Dirichlet("beta_i", a=alpha * np.ones((N, 1, 1)))  # (N, K, M)
            theta = (X_prop[:, :, None] * beta_i).sum(axis=1)              # (N, M)
            pm.Multinomial("y", n=n_votes, p=theta, observed=Y)
            pm.Deterministic("B", (w[:, :, None] * beta_i).sum(axis=0))    # (K, M)

            self.trace = pm.sample(
                draws=self.draws,
                tune=self.tune,
                chains=self.chains,
                random_seed=self.random_seed,
                target_accept=self.target_accept,
                progressbar=True,
            )
        self.model = model

        self.mean_ = self.trace.posterior["B"].mean(dim=("chain", "draw")).values
        hdi = az.hdi(self.trace, var_names=["B"], hdi_prob=self.hdi_prob)["B"]
        self.hdi_low_ = hdi.sel(hdi="lower").values
        self.hdi_high_ = hdi.sel(hdi="higher").values
        return self

    def summary(self):
        """Posterior mean transition matrix (origin x destination) as a DataFrame."""
        if self.mean_ is None:
            raise ValueError("Call .fit(X, Y) first.")
        return pd.DataFrame(self.mean_)
 
