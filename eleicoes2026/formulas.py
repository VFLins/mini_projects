import numpy as np
import pandas as pd


def a_metric(
    a: float,
    a_estimate: float,
) -> np.float64:
    """https://doi.org/10.1093/poq/nfi044

    > [...] measure of the predictive accuracy (A) of election polls that permits
    > examination of both accuracy and bias [...]
    > - Elizabeth A. Martin , Michael W. Traugott , Courtney Kennedy

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

    > [...] polling accuracy measure for multi-party elections based on a generalization
    > of Martin, Traugott, and Kennedy's two-party predictive accuracy index. [...]

    :param a_metrics: Estimated A metrics for each participant of a elecion poll.
    """
    k = len(a_metrics)
    return np.sum(np.absolute(a_metrics)) / k


def poll_data(
    n: int,
    name: str,
    vote_a: float,
    vote_b: float,
    reject_a: float,
    reject_b: float,
) -> pd.Series:
    """Build a poll dataset in long format with vote intentions and rejections.

    :param n: Poll sample size.
    :param name: Poll name, identifying it in the dataset.
    :param vote_a: Percentage of votes declared to candidate A.
    :param vote_b: Percentage of votes declared to candidate B.
    :param unsure_a: Percentage of voters declared unsure about voting on candidate A.
    :param unsure_b: Percentage of voters declared unsure about voting on candidate B.
    :paran reject_a: Percentage of voters declared not voting on candidate A.
    :paran reject_b: Percentage of voters declared not voting on candidate B.
    """
    n_va = round(n * vote_a)
    n_vb = round(n * vote_b)
    n_ra = round(n * reject_a)
    n_rb = round(n * reject_b)
    n_ua = n - n_va - n_ra
    n_ub = n - n_vb - n_rb
    unsure_a = n_ua / n
    unsure_b = n_ub / n

    colnames = [
        "n",
        "vote_a", "vote_b",
        "unsure_a", "unsure_b",
        "reject_a", "reject_b",
        "n_vote_a", "n_vote_b",
        "n_unsure_a", "n_unsure_b",
        "n_reject_a", "n_reject_b",
    ]

    return pd.Series(
        [
            n,
            vote_a, vote_b,
            unsure_a, unsure_b,
            reject_a, reject_b,
            n_va, n_vb,
            n_ua, n_ub,
            n_ra, n_rb,
        ],
        name=name,
        index=colnames
    )
