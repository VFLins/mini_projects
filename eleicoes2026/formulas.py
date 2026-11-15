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


def frechet_limits(va, vb, ra, rb, max_self_rejection=0.0):
    """Compute Fréchet bounds for the winnable voters of candidates A and B.

    Winnable voters of a candidate are the undecided voters who do not reject
    that candidate. The undecided share is derived as
    ``1 - va - vb``.

    For candidate A, with :math:`x = V_A \\cap R_A` bounded by
    ``max_self_rejection``:

    * upper bound: ``undecided - max(0, (ra - x) - vb)``
    * lower bound: ``undecided - min(undecided, ra)``

    The bounds for B are symmetric.

    :param va: Share of voters who intend to vote for A (0 to 1).
    :type va: float
    :param vb: Share of voters who intend to vote for B (0 to 1).
    :type vb: float
    :param ra: Share of voters who reject A (0 to 1).
    :type ra: float
    :param rb: Share of voters who reject B (0 to 1).
    :type rb: float
    :param max_self_rejection: Upper bound for the share of voters who vote for
        a candidate and also reject that candidate. With ``0.0``, voters of X
        are assumed not to reject X.
    :type max_self_rejection: float
    :returns: ``((hi_a, lo_a), (hi_b, lo_b))``, the upper and lower bounds of
        the winnable share for A and for B, as proportions of the electorate.
    :rtype: tuple[tuple[float, float], tuple[float, float]]
    :raises ValueError: If any share is outside [0, 1], if
        ``va + vb`` exceeds 1, or if a rejection share is larger than
        the part of the electorate that does not vote for that candidate.

    Example::

        >>> frechet_limits(0.40, 0.40, 0.30, 0.25)
        ((0.2, 0.0), (0.2, 0.0))
    """
    if min(va, vb, ra, rb) < 0 \
            or max(va, vb, ra, rb) > 1:
        raise ValueError("Shares must be in [0, 1]")

    undecided = 1 - va - vb
    if undecided < 0:
        raise ValueError(f"va + vb must not exceed 1, got {va + vb}")

    def _bounds(own_vote, other_vote, reject):
        x_max = min(max_self_rejection, own_vote, reject)
        if reject - x_max > 1 - own_vote:
            raise ValueError("Rejection is inconsistent with the vote composition")
        hi = undecided - max(0.0, (reject - x_max) - other_vote)
        lo = undecided - min(undecided, reject)
        return max(0.0, hi), max(0.0, lo)

    return (
        _bounds(va, vb, ra),  # winnable by A
        _bounds(vb, va, rb),  # winnable by B
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


class DirichletTransfer:
    """Ecological inference restricted to the undecided reservoir V_U.

    Assumes voters of A and B in Round 1 vote for the same candidate in Round 2
    (T_AA = T_BB = 1). The Round 2 counts of A and B are reduced by their Round 1
    counts, and only the residual is explained by transfers from the origins in V_U.

    ..reference::
      ROSEN, Ori et al. Bayesian and frequentist inference for ecological inference:
      The R× C case. Statistica neerlandica, v. 55, n. 2, p. 134-156, 2001.

    :param idx_a: Column of A in X (Round 1) and in Y (Round 2).
    :param idx_b: Column of B in X and in Y.
    :param u_cols: Columns of X that make up V_U, the pool of voters who may change
        destination (e.g. eliminated candidates, blank/null and abstention). Must be
        exactly the columns of X that are neither ``idx_a`` nor ``idx_b``.
    :param draws: Posterior samples per chain.
    :param max_stations: Maximum number of stations used in the fit. If more stations
        remain after removing those that violate the assumption, a random subsample of
        this size is drawn (seeded by ``seed``). Memory and sampling time grow roughly
        linearly with the number of stations, since the model has one set of transfer
        rates per station.
    :param seed: Random subsampling seed.
    """

    def __init__(
        self,
        idx_a,
        idx_b,
        u_cols,
        tune=1000,
        draws=1000,
        chains=4,
        max_depth=10,
        max_stations=30_000,
        seed=42
    ):
        self.idx_a, self.idx_b, self.u_cols = idx_a, idx_b, list(u_cols)
        self.tune, self.draws, self.chains = tune, draws, chains
        self.max_depth, self.max_stations, self.seed = max_depth, max_stations, seed

    def fit(self, X, Y):
        """
        :param X: Round 1 counts of eligible voters, shape (stations, K),
            including abstention.
        :param Y: Round 2 counts, shape (stations, M), same electorate.
        """
        X, Y = np.asarray(X, float), np.asarray(Y, float)

        res = np.column_stack([Y[:, self.idx_a] - X[:, self.idx_a],
                               Y[:, self.idx_b] - X[:, self.idx_b]])
        self.resid_ = pd.DataFrame(res, columns=["res_A", "res_B"])
        ok = (res >= 0).all(axis=1)
        self.share_violated_ = 1 - ok.mean()

        X, Y = X[ok], Y[ok].copy()
        Y[:, self.idx_a] -= X[:, self.idx_a]
        Y[:, self.idx_b] -= X[:, self.idx_b]
        Y = np.round(Y).astype(int)

        XU = X[:, self.u_cols]
        keep = (XU.sum(axis=1) > 0) & (Y.sum(axis=1) > 0)
        XU, Y = XU[keep], Y[keep]

        # Random subsample of stations to bound memory and sampling time
        if len(XU) > self.max_stations:
            idx = np.random.default_rng(self.seed).choice(
                len(XU), self.max_stations, replace=False)
            XU, Y = XU[idx], Y[idx]

        N, K = XU.shape
        M = Y.shape[1]
        X_prop = XU / XU.sum(axis=1, keepdims=True)
        w = XU / XU.sum(axis=0, keepdims=True)

        with pm.Model():
            alpha = pm.Gamma("alpha", 4.0, 2.0, shape=(K, M))
            beta_i = pm.Dirichlet("beta_i", a=alpha * np.ones((N, 1, 1)))
            theta = (X_prop[:, :, None] * beta_i).sum(axis=1)
            pm.Multinomial("y", n=Y.sum(axis=1), p=theta, observed=Y)
            pm.Deterministic("B", (w[:, :, None] * beta_i).sum(axis=0))
            pm.NUTS(max_treedepth=self.max_depth)
            self.trace = pm.sample(
                tune=self.tune,
                draws=self.draws,
                chains=self.chains,
                target_accept=0.95,
                nuts_sampler="numpyro",
                nuts={"chain_method": "vectorized"},
                idata_kwargs={"log_likelihood": False},
                var_names=["alpha", "B"],
                random_seed=self.seed
            )

        self.XU_ = XU
        self.mean_ = self.trace.posterior["B"].mean(dim=("chain", "draw")).values
        return self

    def flows(self):
        """Sampled (n<=1000) posterior means. Origin in rows and destination in
        columns.
        """
        return pd.DataFrame(self.XU_.sum(axis=0)[:, None] * self.mean_)

    def summary(self):
        """R-hat, ESS and HDI of the aggregate transition matrix."""
        return az.summary(self.trace, var_names=["B"])
