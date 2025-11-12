"""
Statistics required for RCMIP analysis
"""
import numpy as np
import pandas as pd
import scipy.optimize
from scipy.stats import multivariate_normal, norm


def _diff_exp_sigma(sigma, ratio, conflevel):

    low = (1 - conflevel) / 2
    upp = 1 - low
    qno = norm.ppf(upp)
    ratio_sigma = (np.exp(qno * sigma) - 1) / (1 - np.exp(-qno * sigma))

    diff = ratio_sigma - ratio

    return diff**2


def _get_skewed_normal_width(ratio, conflevel):
    ratio_in = ratio if ratio >= 1 else 1 / ratio
    if not 0 <= conflevel <= 1:
        raise ValueError(f"Confidence level must be in [0, 1]. Received: {conflevel}")

    opt_res = scipy.optimize.minimize(
        _diff_exp_sigma,
        (0.1,),
        args=(ratio_in, conflevel),
        bounds=((10**-7, 10),),
        options={"maxiter": 10**6},
    )

    if not opt_res.success:
        raise ValueError(
            "Optimisation failed for ratio {} and conflevel {}".format(ratio, conflevel)
        )

    skewed_normal_width = float(opt_res.x.squeeze())

    return skewed_normal_width


def get_skewed_normal(median, lower, upper, conf, input_data):
    """
    Get skewed normal distribution matching the inputs

    Parameters
    ----------
    median : float
        Median of the output distribution

    lower : float
        Lower bound of the confidence interval

    upper : float
        Upper bound of the confidence interval

    conf : float
        Confidence associated with the interval [lower, upper] e.g. 0.66
        would mean that [lower, upper] defines the 66% confidence range

    input_data : :obj:`np.ndarray`
        Points from the derived distribution to return. For each point, Y, in
        ``input_data``, we determine the value at which a cumulative
        probability of Y is achieved. As a result, all values in
        ``input_data`` must be in the range [0, 1]. Hence if you want a random
        sample from the derived skewed normal, simply make ``input_data``
        equal to a random sample of the uniform distribution [0, 1]

    Returns
    -------
    :obj:`np.ndarray`
        Points sampled from the derived skewed normal distribution based on
        ``input_data``
    """
    ratio = (upper - median) / (median - lower)
    ratio_gte_one = ratio >= 1

    skewed_normal_width = _get_skewed_normal_width(ratio, conf)

    factor_denominator = np.exp(skewed_normal_width * norm.ppf(0.5 * (1 + conf))) - 1

    if ratio_gte_one:
        factor = (upper - median) / factor_denominator
    else:
        factor = (lower - median) / factor_denominator

    shift = median - factor

    input_data = np.array(input_data)
    if ratio_gte_one:
        res_inp = input_data
    else:
        res_inp = 1 - input_data

    res = np.exp(norm.ppf(res_inp) * skewed_normal_width) * factor + shift

    return res


def sample_multivariate_skewed_normal(configuration, size, cor=None):
    r"""
    Sample multi-variate skewed normal distribution

    Following [Meinshausen et al. (2009)](https://doi.org/10.1038/nature08017),
    a skewed normal is defined as follows:
    "A distribution X, is skewed normal, if :math:`\\log(X + C)`, where
    :math:`C` is a constant, is a normal distribution with variance
    :math:`\\sigma^2` and mean :math:`\\mu`". The skewed normal allows us to
    create distributions which match arbitrary median and likely ranges (with
    associated confidence as a percentage), as is often used by the IPCC. A
    multivariate skewed normal is constructed such that each marginal
    distribution is a skewed normal and the overall distribution
    can have a non-identity correlation matrix.

    Parameters
    ----------
    configuration : :obj:`pd.DataFrame`
        Configuration for the sampling. Each column must represent a dimension to
        be sampled. The rows must be
        ``["median", "upper", "lower", "conf"]``. The rows represent the
        characteristics of each marginal distribution. The median is the median
        of each marginal distribution. ``"conf"`` represents the confidence
        associated with each of the intervals defined by ``"lower"`` and
        ``"upper"`` (e.g. 0.66 would mean that [lower, upper] defines the 66%
        confidence range).

    size : int
        Number of points to sample from the multivariate skewed normal

    cor : array[float]
        Correlation matrix between different dimensions in `configuration`.
        `cor` must be a square, symmetric matrix with size n x n, where n is
        the number of columns in ``configuration``. The element in row i and
        column j represents the correlation between the dimension in column i of
        ``configuration`` and the dimension in column j of ``configuration``. The
        correlations must be normalised i.e. the maximum value of each element
        is 1 and the minimum value is -1. As a result of the normalisation, the
        diagonals of ``cor`` must all be equal to 1.

    Returns
    -------
    :obj:`pd.DataFrame`
        Points sampled from the derived multivariate skewed normal
        distribution. Each row is a sampled point (so there will be ``size``
        row in the output). The columns match the columns in ``configuration``.

    Raises
    ------
    ValueError
        ``configuration`` contains any nans, distribution ranges are
        incorrectly specified (e.g. medians > upper ends of the
        intervals) or the correlation matrix is incorrectly normalised.

    KeyError
        ``configuration`` is missing one of the rows:
        ``["median", "upper", "lower", "conf"]``
    """
    if configuration.isnull().any().any():
        raise ValueError(
            f"`configuration` must not contain nan, received: {configuration}"
        )

    res_array = _sample_multivariate_skewed_normal_from_arrays(
        configuration.loc["median", :],
        configuration.loc["lower", :],
        configuration.loc["upper", :],
        configuration.loc["conf", :],
        size,
        cor,
    )

    res = pd.DataFrame(res_array, columns=configuration.columns)

    return res


def _check_input_ordering(a, b, a_name, b_name):
    a_gt_b = a > b
    if not np.all(a_gt_b):
        raise ValueError(
            f"{a_name} must be greater than {b_name}. "
            f"Received {a_name}: {a} and {b_name}: {b}. "
            f"Entries where {a_name} are greater than {b_name}: {a_gt_b}"
        )


def _check_correlation_matrix(cor):
    if not np.allclose(np.diag(cor), 1):
        raise ValueError(
            "The correlation matrix must be normalised i.e. all "
            "diagonal elements should be equal to 1. "
            f"Received: {cor}"
        )

    if not np.all(np.abs(cor) <= 1):
        raise ValueError(
            "The correlation matrix must be normalised i.e. all "
            "off-diagonal elements should have magnitude <=1. "
            f"Received: {cor}"
        )


def _sample_multivariate_skewed_normal_from_arrays(
    medians, lowers, uppers, confs, size, cor
):
    medians = np.atleast_1d(np.asarray(medians))
    lowers = np.atleast_1d(np.asarray(lowers))
    uppers = np.atleast_1d(np.asarray(uppers))
    confs = np.atleast_1d(np.asarray(confs))

    _check_input_ordering(uppers, medians, "uppers", "medians")
    _check_input_ordering(medians, lowers, "medians", "lowers")

    if cor is None:
        cor = np.eye(medians.shape[0])
    else:
        cor = np.asarray(cor)
        _check_correlation_matrix(cor)

    ratios = (uppers - medians) / (medians - lowers)
    ratios_gte_one = ratios >= 1

    skewed_normal_widths = np.asarray(
        [_get_skewed_normal_width(r, c) for r, c in zip(ratios, confs)]
    )

    factors_denominator = np.exp(skewed_normal_widths * norm.ppf(0.5 * (1 + confs))) - 1

    factors = (lowers - medians) / factors_denominator
    factors[ratios_gte_one] = ((uppers - medians) / factors_denominator)[ratios_gte_one]

    shifts = medians - factors

    inp = multivariate_normal(np.zeros_like(medians), cor).rvs(size)
    if len(inp.shape) == 1:
        inp = inp[:, np.newaxis]

    inp[:, np.where(~ratios_gte_one)] *= -1

    # Each marginal distribution has a distribution X, such that
    # log(X + C) is a normal distribution with mean mu and variance sigma^2
    # This can be seen by re-arranging the below to
    # inp * skewed_normal_widths + factors = log(res - shifts)
    # and noting that inp is a normal distribution along each marginal axis
    res = np.exp(inp * skewed_normal_widths) * factors + shifts

    return res
