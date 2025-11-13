import numpy as np

# compute sample cov
def sample_cov(data):  # 2d array of observations and dimensions, each row is observation
    n_obs = data.shape[0]
    if n_obs < 2:
        raise ValueError("Only one observation is observed, at least two observations are required.")
    demean = data - np.mean(data, axis=0)
    cov = (demean.T @ demean) / (n_obs - 1)
    return cov