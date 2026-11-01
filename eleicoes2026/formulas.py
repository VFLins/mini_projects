import numpy as np

def a_metric(
    a: float,
    b: float,
    a_estimate: float,
    b_estimate: float,
) -> np.float64:
    """https://doi.org/10.1093/poq/nfi044

    > [...] measure of the predictive accuracy (A) of election polls that permits
    > examination of both accuracy and bias [...]
    > - Elizabeth A. Martin , Michael W. Traugott , Courtney Kennedy

    :param a: Percentage of valid votes presidential candidate A.
    :param b: Percentage of valid votes presidential candidate B.
    :param a_estimate: Percentage of valid votes predicted to candidate A.
    :param b_estimate: Percentage of valid votes predicted to candidate B.
    """
    estimated_balance = a_estimate / b_estimate
    observed_balance = a / b
    return np.log(estimated_balance / observed_balance)


def a_std_error(n: float, m: float) -> np.float64:



