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


def frechet_limits(a_vote, b_vote, a_reject, b_reject, max_self_rejection=0.0):
    """Compute Fréchet bounds for the winnable voters of candidates A and B.

    Winnable voters of a candidate are the undecided voters who do not reject
    that candidate. The undecided share is derived as
    ``1 - a_vote - b_vote``.

    For candidate A, with :math:`x = V_A \\cap R_A` bounded by
    ``max_self_rejection``:

    * upper bound: ``undecided - max(0, (a_reject - x) - b_vote)``
    * lower bound: ``undecided - min(undecided, a_reject)``

    The bounds for B are symmetric.

    :param a_vote: Share of voters who intend to vote for A (0 to 1).
    :type a_vote: float
    :param b_vote: Share of voters who intend to vote for B (0 to 1).
    :type b_vote: float
    :param a_reject: Share of voters who reject A (0 to 1).
    :type a_reject: float
    :param b_reject: Share of voters who reject B (0 to 1).
    :type b_reject: float
    :param max_self_rejection: Upper bound for the share of voters who vote for
        a candidate and also reject that candidate. With ``0.0``, voters of X
        are assumed not to reject X.
    :type max_self_rejection: float
    :returns: ``((hi_a, lo_a), (hi_b, lo_b))``, the upper and lower bounds of
        the winnable share for A and for B, as proportions of the electorate.
    :rtype: tuple[tuple[float, float], tuple[float, float]]
    :raises ValueError: If any share is outside [0, 1], if
        ``a_vote + b_vote`` exceeds 1, or if a rejection share is larger than
        the part of the electorate that does not vote for that candidate.

    Example::

        >>> frechet_limits(0.40, 0.40, 0.30, 0.25)
        ((0.2, 0.0), (0.2, 0.0))
    """
    if min(a_vote, b_vote, a_reject, b_reject) < 0 \
            or max(a_vote, b_vote, a_reject, b_reject) > 1:
        raise ValueError("Shares must be in [0, 1]")

    undecided = 1 - a_vote - b_vote
    if undecided < 0:
        raise ValueError(f"a_vote + b_vote must not exceed 1, got {a_vote + b_vote}")

    def _bounds(own_vote, other_vote, reject):
        x_max = min(max_self_rejection, own_vote, reject)
        if reject - x_max > 1 - own_vote:
            raise ValueError("Rejection is inconsistent with the vote composition")
        hi = undecided - max(0.0, (reject - x_max) - other_vote)
        lo = undecided - min(undecided, reject)
        return max(0.0, hi), max(0.0, lo)

    return (
        _bounds(a_vote, b_vote, a_reject),  # winnable by A
        _bounds(b_vote, a_vote, b_reject),  # winnable by B
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
 
