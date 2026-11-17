from __future__ import annotations
 
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az


@dataclass(frozen=True)
class Potential:
    """Winnable share of one candidate, as proportions of the electorate.

    Each field is a float, or an array with one entry per poll when the inputs
    of :func:`vote_potential` are arrays.

    :param hi: Upper (Fréchet) bound, valid for any ``beta``.
    :param est: Estimate for the ``beta`` used.
    :param lo: Lower (Fréchet) bound.
    """
    hi: float | np.ndarray
    est: float | np.ndarray
    lo: float | np.ndarray


@dataclass(frozen=True)
class VotePotential:
    """Result of :func:`vote_potential`.

    :param a: Potential of candidate A.
    :param b: Potential of candidate B.
    :param beta: Heterogeneity parameter used in the estimates.
    """
    a: Potential
    b: Potential
    beta: float


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


def vote_potential(va, vb, ra, rb, beta=1.0):
    """Estimate the winnable voters of candidates A and B from poll marginals.

    Winnable voters of a candidate are the undecided voters who do not reject
    that candidate, so the potential is a ceiling and not a forecast. The
    cross-tabulation between vote intention and rejection is not observed, so
    the rejection of A is split between B voters and undecided voters through
    a heterogeneity parameter.

    With ``vu = 1 - va - vb`` and ``beta = r_u / r_b``, where ``r_b`` and
    ``r_u`` are the rejection rates of A among B voters and among undecided
    voters, and assuming nobody votes for a candidate they reject::

        P_A = vu * (1 - beta * ra / (vb + beta * vu))

    The result is clipped to the Fréchet bounds, which hold without any
    assumption on ``beta``::

        hi = vu - max(0, ra - vb)
        lo = max(0, vu - ra)

    The estimate for B is symmetric (swap ``va``/``vb`` and ``ra``/``rb``).

    :param va: Share of voters who intend to vote for A (0 to 1).
    :param vb: Share of voters who intend to vote for B (0 to 1).
    :param ra: Share of voters who reject A (0 to 1).
    :param rb: Share of voters who reject B (0 to 1).
    :param beta: Ratio between the rejection rate of a candidate among
        undecided voters and among the rival's voters. ``1`` means homogeneous
        rejection; ``beta > 1`` puts more of the rejection among the
        undecided (lower potential); ``beta < 1`` puts more among the rival's
        voters (higher potential).
    :returns: A :class:`VotePotential` with ``a`` and ``b`` (each a
        :class:`Potential` with ``hi``, ``est`` and ``lo``) and the ``beta``
        used. Arguments may be scalars or arrays with one entry per poll.
    :raises ValueError: If shares are outside [0, 1], if ``va + vb`` exceeds 1,
        if ``beta`` is not positive, or if a rejection share is larger than the
        part of the electorate that does not vote for that candidate.

    Example::

        >>> p = vote_potential(0.40, 0.40, 0.30, 0.25)
        >>> round(float(p.a.hi), 3), round(float(p.a.est), 3), round(float(p.a.lo), 3)
        (0.2, 0.1, 0.0)
        >>> round(float(p.b.est), 3)
        0.117
    """
    va, vb, ra, rb = (np.asarray(x, float) for x in (va, vb, ra, rb))
    if any((x < 0).any() or (x > 1).any() for x in (va, vb, ra, rb)):
        raise ValueError("Shares must be in [0, 1]")
    if beta <= 0:
        raise ValueError("beta must be positive")
    vu = 1 - va - vb
    if (vu < 0).any():
        raise ValueError("va + vb must not exceed 1")

    def _potential(v_other, r):
        if (r > v_other + vu).any():
            raise ValueError(
              "Rejection exceeds the electorate that does not "
              "vote for the candidate"
            )
        hi = vu - np.maximum(0.0, r - v_other)
        lo = np.maximum(0.0, vu - r)
        denom = v_other + beta * vu
        est = vu * (1 - beta * r / np.where(denom > 0, denom, np.nan))
        est = np.clip(np.nan_to_num(est, nan=0.0), lo, hi)
        # unwrap 0-d arrays so scalar inputs give plain floats
        hi, est, lo = (x.item() if x.ndim == 0 else x for x in (hi, est, lo))
        return Potential(hi=hi, est=est, lo=lo)

    return VotePotential(a=_potential(vb, ra), b=_potential(va, rb), beta=beta)


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
        seed=42
    ):
        self.idx_a, self.idx_b, self.u_cols = idx_a, idx_b, list(u_cols)
        self.tune, self.draws, self.chains = tune, draws, chains
        self.max_depth, self.seed = max_depth, seed

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
