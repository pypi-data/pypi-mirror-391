# psd_covariance package

A Python package for estimating positive semi-definite (PSD) covariance matrices.
Includes methods for computing:

- Sample covariance matrix;
- Thresholding or correcting negative eigenvalues based on the work of Rousseeuw and Molenberghs (1993);
- Linear Shrinkage and QIS Shrinkage of Ledoit & Wolf (2004, 2022);
- The posterior mean (PM) and fixed-trace (FT) estimators from Boudt et al. (2025);
- Fast cross-validation for regularization parameter tuning for PM and FT.

### Installation
```python
pip install psd-covariance
```

### Quick Start
```python
import numpy as np
from psd_covariance import utils, posterior_mean

np.random.seed(0)
X = np.random.multivariate_normal(
    mean=np.zeros(5),
    cov=0.8 ** np.abs(np.subtract.outer(np.arange(5), np.arange(5))),
    size=50
)

S = utils.sample_cov(X)

pm = posterior_mean.PosteriorMeanEstimator(fixed_trace=False)
Sigma_pm, _ = pm.fit(S, sigma=0.5)

print(Sigma_pm)
```
