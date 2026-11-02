import numpy as np


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

