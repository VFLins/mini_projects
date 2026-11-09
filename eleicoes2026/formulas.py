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


class DirichletTransferring:
    def __init__(
        """
        Bayesian Ecological Inference Model for Vote Transfer Estimation.

        This implementation estimates transition matrices between two election rounds
        using micro-data aggregated by polling stations. The methodology is based on
        the multinomial-Dirichlet hierarchical framework for ecological inference, 
        extending the foundational work on ecological inference by Gary King.

        .. reference::
           King, G. (1997). *A Solution to the Ecological Inference Problem: 
           Reconstructing Individual Behavior from Aggregate Data*. Princeton 
           University Press.

        :param colunas_origem: Names of the origin candidates/options from Round 1.
        :type colunas_origem: list of str, optional
        :param colunas_destino: Names of the destination candidates/options from Round 2.
        :type colunas_destino: list of str, optional
        :param draws: The number of samples to draw from the posterior distribution per chain.
        :type draws: int, default=2000
        :param tune: Number of iterations to tune (warm-up) the MCMC sampler.
        :type tune: int, default=1000
        :param chains: Number of Markov chains to run in parallel.
        :type chains: int, default=2
        :param random_seed: Seed for the random number generator to ensure reproducibility.
        :type random_seed: int, default=42
        """
        self, 
        colunas_origem=None, 
        colunas_destino=None, 
        draws=2000, 
        tune=1000, 
        chains=2, 
        random_seed=42
    ):
        self.colunas_origem = colunas_origem
        self.colunas_destino = colunas_destino
        self.draws = draws
        self.tune = tune
        self.chains = chains
        self.random_seed = random_seed

        # Attributes stored after invoking fit()
        self.is_fitted = False
        self.model = None
        self.trace = None
        self.mean_transition_matrix = None
        self.hdi_low_transition_matrix = None
        self.hdi_high_transition_matrix = None
        self.df_transition_matrix = None

    def _prepare_data(self, X, Y):
        """
        Validates input data, extracts column names if provided as DataFrames, 
        and normalizes row counts into proportions (row sum equals 1.0).

        :param X: Matrix or DataFrame containing raw votes or proportions for Round 1.
        :type X: numpy.ndarray or pandas.DataFrame
        :param Y: Matrix or DataFrame containing raw votes or proportions for Round 2.
        :type Y: numpy.ndarray or pandas.DataFrame
        :return: Normalized proportion matrices (X_prop, Y_prop).
        :rtype: tuple of (numpy.ndarray, numpy.ndarray)
        """
        if isinstance(X, pd.DataFrame):
            if self.colunas_origem is None:
                self.colunas_origem = list(X.columns)
            X = X.values
        if isinstance(Y, pd.DataFrame):
            if self.colunas_destino is None:
                self.colunas_destino = list(Y.columns)
            Y = Y.values

        # Normalize rows to proportions (sum across candidates per precinct = 1.0)
        X_prop = X / X.sum(axis=1, keepdims=True)
        Y_prop = Y / Y.sum(axis=1, keepdims=True)

        return X_prop, Y_prop

    def fit(self, X, Y):
        """
        Fits the Bayesian Multinomial-Dirichlet model to the provided Round 1 (X) 
        and Round 2 (Y) voting data using PyMC MCMC sampling.

        :param X: Voting data for Round 1 per polling station.
        :type X: numpy.ndarray or pandas.DataFrame
        :param Y: Voting data for Round 2 per polling station.
        :type Y: numpy.ndarray or pandas.DataFrame
        :return: Returns self with updated posterior parameters.
        :rtype: BayesianVoteTransfer
        """
        X_prop, Y_prop = self._prepare_data(X, Y)

        num_precincts, K = X_prop.shape  # K candidates in Round 1
        _, M = Y_prop.shape              # M options in Round 2

        if self.colunas_origem is None:
            self.colunas_origem = [f"Origin_{i+1}" for i in range(K)]
        if self.colunas_destino is None:
            self.colunas_destino = [f"Destination_{j+1}" for j in range(M)]

        # 1. PyMC Model Definition
        with pm.Model() as model:
            # Dirichlet priors for each of the K Round 1 candidates
            beta = pm.Dirichlet('beta', a=np.ones(M), shape=(K, M))
            # Expected proportion per precinct
            mu = pm.math.dot(X_prop, beta)
            # Stochastic variance across precincts
            sigma = pm.HalfNormal('sigma', sigma=1.0)
            # Likelihood definition
            likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=Y_prop)
            # MCMC Sampling
            self.trace = pm.sample(
                draws=self.draws,
                tune=self.tune,
                chains=self.chains,
                random_seed=self.random_seed,
                return_inferencedata=True,
                progressbar=True
            )

        self.model = model

        # 2. Extract Posterior Estimates
        beta_samples = self.trace.posterior['beta'].values  # Shape: (chains, draws, K, M)
        beta_flat = beta_samples.reshape(-1, K, M)          # Shape: (total_samples, K, M)

        # Posterior mean of transition probabilities
        self.mean_transition_matrix = beta_flat.mean(axis=0)

        # Highest Density Interval (HDI 94%)
        hdi = az.hdi(self.trace.posterior)['beta'].values  # Shape: (K, M, 2)
        self.hdi_low_transition_matrix = hdi[:, :, 0]
        self.hdi_high_transition_matrix = hdi[:, :, 1]

        # Formatted DataFrame for transition matrix
        self.df_transition_matrix = pd.DataFrame(
            self.mean_transition_matrix,
            index=self.colunas_origem,
            columns=self.colunas_destino
        )

        self.is_fitted = True
        return self

    def summary(self):
        """
        Returns the formatted transition matrix containing mean transfer estimates.

        :return: DataFrame containing mean transfer proportions between rounds.
        :rtype: pandas.DataFrame
        :raises ValueError: If called before running ``.fit()``.
        """
        if not self.is_fitted:
            raise ValueError("The model is not fitted yet. Call '.fit(X, Y)' first.")
        return self.df_transition_matrix

    def get_plot_data(self, long=False):
        """
        Extracts posterior mean transfer proportions and error bounds structured 
        as a single pandas DataFrame for plotting.

        **Returned DataFrame Columns when** ``long=False`` **(Wide Format):**

        - Index: Name of the Round 1 origin candidate/option.
        - Destination Columns (e.g., ``Finalist_1_R2``, ``Finalist_2_R2``): 
          Mean transition proportions for each Round 2 destination option.
        - Error Columns (e.g., ``Finalist_1_R2_err_low``, ``Finalist_1_R2_err_high``): 
          Absolute asymmetric error bounds calculated relative to the posterior mean 
          for plotting with Matplotlib (suitable for ``yerr`` parameters).

        **Returned DataFrame Columns when** ``long=True`` **(Long/Melted Format):**

        - ``Origin`` (str): Name of the origin candidate/option from Round 1.
        - ``Destination`` (str): Name of the destination candidate/option from Round 2.
        - ``Weight`` (float): Mean estimated vote transfer proportion.
        - ``HDI_Low`` (float): Lower bound of the 94% Highest Density Interval (HDI).
        - ``HDI_High`` (float): Upper bound of the 94% Highest Density Interval (HDI).
        - ``Err_Low`` (float): Lower absolute error bound (``Weight - HDI_Low``).
        - ``Err_High`` (float): Upper absolute error bound (``HDI_High - Weight``).

        :param long: If True, returns a single long-format DataFrame (edge-list format) 
                     optimized for Sankey/Ribbon diagrams. If False, returns a single 
                     wide-format DataFrame with mean values and error columns.
        :type long: bool, default=False
        :return: A single DataFrame formatted based on the ``long`` parameter.
        :rtype: pandas.DataFrame
        :raises ValueError: If called before running ``.fit()``.
        """
        if not self.is_fitted:
            raise ValueError("The model is not fitted yet. Call '.fit(X, Y)' first.")

        means_df = pd.DataFrame(
            self.mean_transition_matrix, 
            index=self.colunas_origem, 
            columns=self.colunas_destino
        )
        hdi_low_df = pd.DataFrame(
            self.hdi_low_transition_matrix, 
            index=self.colunas_origem, 
            columns=self.colunas_destino
        )
        hdi_high_df = pd.DataFrame(
            self.hdi_high_transition_matrix, 
            index=self.colunas_origem, 
            columns=self.colunas_destino
        )

        if long:
            # Flatten matrices into an edge list (Origin -> Destination -> Metrics)
            means_long = means_df.reset_index().melt(
                id_vars='index', var_name='Destination', value_name='Weight'
            ).rename(columns={'index': 'Origin'})
            low_long = hdi_low_df.reset_index().melt(
                id_vars='index', var_name='Destination', value_name='HDI_Low'
            ).rename(columns={'index': 'Origin'})
            high_long = hdi_high_df.reset_index().melt(
                id_vars='index', var_name='Destination', value_name='HDI_High'
            ).rename(columns={'index': 'Origin'})

            df = means_long.merge(low_long, on=['Origin', 'Destination'])
            df = df.merge(high_long, on=['Origin', 'Destination'])

            df['Err_Low'] = np.abs(df['Weight'] - df['HDI_Low'])
            df['Err_High'] = np.abs(df['HDI_High'] - df['Weight'])
        else:
            # Create a single wide-format DataFrame with mean values and error columns
            err_lower = np.abs(self.mean_transition_matrix - self.hdi_low_transition_matrix)
            err_upper = np.abs(self.hdi_high_transition_matrix - self.mean_transition_matrix)

            df = means_df.copy()

            for i, col in enumerate(self.colunas_destino):
                df[f"{col}_err_low"] = err_lower[:, i]
                df[f"{col}_err_high"] = err_upper[:, i]

        return df
