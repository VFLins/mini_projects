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

    def __init__(self, idx_a, idx_b, u_cols, draws=1000, max_stations=30_000, seed=42):
        self.idx_a, self.idx_b, self.u_cols = idx_a, idx_b, list(u_cols)
        self.draws, self.max_stations, self.seed = draws, max_stations, seed

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
            self.trace = pm.sample(
                tune=2000,
                draws=self.draws,
                chains=4,
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
        """Posterior mean voters: origin in V_U (rows) -> destination (columns)."""
        return pd.DataFrame(self.XU_.sum(axis=0)[:, None] * self.mean_)

    def summary(self):
        """R-hat, ESS and HDI of the aggregate transition matrix."""
        return az.summary(self.trace, var_names=["B"])



def build_matrices(df, cargo, a_num, b_num, electorate_total):
    """Build the X (Round 1) and Y (Round 2) matrices of the ecological model.

    Abstention is the difference in total votes between rounds in the same
    station: the round with fewer votes receives the difference as abstention
    and the other receives zero. The electorate of a station is therefore the
    larger of the two vote totals, and every row of X and Y sums to it.

    :param df: VOTACAO_SECAO already loaded as a DataFrame (both rounds). It
        must contain ``CD_MUNICIPIO``, ``NR_ZONA``, ``NR_SECAO``,
        ``CD_CARGO``, ``NR_TURNO``, ``NR_VOTAVEL`` and ``QT_VOTOS``.
    :param cargo: ``CD_CARGO`` of the race (e.g. 1 = President, 3 = Governor).
    :param a_num: ``NR_VOTAVEL`` of candidate A (Round 2 finalist).
    :param b_num: ``NR_VOTAVEL`` of candidate B (Round 2 finalist).
    :param electorate_total: Total eligible voters.
    :returns: ``(X, Y, report)``. X columns are ``[A, B, OUT, BN, ABS]`` and
        Y columns are ``[A, B, BN, ABS]``; with the VUTransfer class use
        ``idx_a=0, idx_b=1, u_cols=[2, 3, 4]``.
    """
    KEY = ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    BLANK_NULL = {95, 96, 97}

    v = df.loc[
        df["CD_CARGO"] == cargo, KEY + ["NR_TURNO", "NR_VOTAVEL", "QT_VOTOS"]
    ]
    grp = np.select(
        [
            v["NR_VOTAVEL"] == a_num, v["NR_VOTAVEL"] == b_num,
            v["NR_VOTAVEL"].isin(BLANK_NULL)
        ],
        ["A", "B", "BN"],
        default="OUT"
    )
    table = (
        v.assign(grp=grp)
        .groupby(KEY + ["NR_TURNO", "grp"])["QT_VOTOS"].sum()
        .unstack("grp", fill_value=0)
        .reindex(columns=["A", "B", "OUT", "BN"], fill_value=0)
    )

    r1 = table.xs(1, level="NR_TURNO")
    r2 = table.xs(2, level="NR_TURNO")
    both = r1.join(r2, how="inner", lsuffix="_1", rsuffix="_2")

    t1 = both[["A_1", "B_1", "OUT_1", "BN_1"]].sum(axis=1)
    t2 = both[["A_2", "B_2", "OUT_2", "BN_2"]].sum(axis=1)
    base = np.maximum(t1, t2)

    both["ABS_1"] = base - t1
    both["ABS_2"] = base - t2
    keep = base > 0
    both, base = both[keep], base[keep]
    extra = electorate_total - base.sum()
    if extra < 0:
        raise ValueError(
            f"Votes in kept stations ({base.sum():,}) exceed "
            f"electorate_total ({electorate_total:,}); check the territory."
        )
    common = np.round(extra * base / base.sum()).astype(int)
    both["ABS_1"] += common
    both["ABS_2"] += common

    report = {
        "stations_round1": len(r1),
        "stations_round2": len(r2),
        "stations_kept": len(both),
        "net_abstention_part": int(base.sum() - t1[keep].sum()),
        "common_abstention_added": int(common.sum()),
        "abstention_rate_round1": float(both["ABS_1"].sum() / electorate_total),
        "abstention_rate_round2": float(both["ABS_2"].sum() / electorate_total),
    }

    X = both[["A_1", "B_1", "OUT_1", "BN_1", "ABS_1"]]
    X.columns = ["A", "B", "OUT", "BN", "ABS"]
    Y = both[["A_2", "B_2", "BN_2", "ABS_2"]]
    Y.columns = ["A", "B", "BN", "ABS"]
    return X, Y, report
