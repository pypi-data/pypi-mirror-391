# A Package for Posterior Mean Covariance Estimation (psd\_covariance)

### Introduction

We address the problem of obtaining accurate and well-conditioned covariance
estimates by developing a regularization scheme grounded in the principle of
positive semi-definiteness (PSD). The method is designed for two practical
scenarios:

1. **Improving unreliable covariance estimates.**  
   When a preliminary estimator produces noisy or non-positive eigenvalues,
   the regularization corrects them, ensuring positive semi-definiteness and improving conditioning and predictive performance.

2. **Stabilizing truly ill-conditioned covariance structures.**  
   Even when the underlying covariance matrix is highly ill-conditioned, the
   method better-behaved estimate that performs well in
   out-of-sample settings such as mean-variance portfolio optimization.



### Authors
This package is based on the paper 'Well-Conditioned Covariance Estimation via Bayesian
Eigenvalue Regularization', by Kris Boudt, Jesper Cremers, Kirill Dragun & Steven Vanduffel. The psd_covariance package is developed and maintained by Jesper Cremers.

### Contents

The package provides the following functionality:

- **Posterior Mean (PM) and Fixed-Trace (PM-FT) covariance estimators**  
  Implements the Bayesian eigenvalue-regularization approach of Boudt et al. (2025), producing PSD and well-conditioned covariance matrices for any input.

- **Fast likelihood-based cross-validation for tuning the regularization parameter**  
  Efficient K-fold predictive likelihood selection for the PM and FT estimators.

- **Eigenvalue cleaning methods**  
  Ad hoc procedures for correcting non-positive eigenvalues, following Rousseeuw & Molenberghs (1993).

- **Shrinkage estimators**  
  Implements Ledoit–Wolf linear shrinkage (2004) and quadratic inverse shrinkage (QIS, 2022).  
  Includes adapted code from Michael Wolf’s reference implementation:  
  https://github.com/pald22/covShrinkage.

### Installation
```python
pip install psd-covariance
```
### Imports
```python
import pandas as pd
import numpy as np
from numpy.linalg import norm, cond
import matplotlib.pyplot as plt
```

## Quick Start
### Example 1: Transforming non-PSD matrices
We construct a non-PSD estimated covariance matrix with d=10, such that the smallest two eigenvalues are negative.
```python
d = 10
A = np.random.randn(d, d)
Q, _ = np.linalg.qr(A)
eigvals = np.random.uniform(0.5, 2.0, size = d)
eigvals[:2] *= -0.5
Sigma_tilde = Q @ np.diag(eigvals) @ Q.T
eigvals = np.sort(eigvals)
print(eigvals)
# [-0.67406598 -0.38745988  0.62513365  0.71727164  1.03341911  1.23208442, 1.62299543  1.64798788  1.85557961  1.91064792]
```
To transform the non-PSD matrix to a PSD matrix to obtain improved estimates, we compute the available estimators.
```python
cleaned_thresh, _ = EigenvalueCleaning.threshold_negative(Sigma_tilde)
eigvals_thresh = np.linalg.eigvalsh(cleaned_thresh)

# consider PD matrix
cleaned_replace, _ = EigenvalueCleaning.replace_negative(Sigma_tilde, 
                                                            epsilon=1e-1, PD=True)
eigvals_replace = np.linalg.eigvalsh(cleaned_replace)

# consider PD matrix
cleaned_abs, _ = EigenvalueCleaning.absolute_negative(Sigma_tilde, PD=True)
eigvals_abs = np.linalg.eigvalsh(cleaned_abs)

pm = PosteriorMeanEstimator(fixed_trace=False)
pm.fit(Sigma_tilde, sigma=0.5) # arbitrary choice
eigvals_pm = np.linalg.eigvalsh(pm.Sigma_)

ft = PosteriorMeanEstimator(fixed_trace=True)
ft.fit(Sigma_tilde, sigma=0.5) # arbitrary choice
eigvals_ft = np.linalg.eigvalsh(ft.Sigma_)
```

``` python
print("\nEigenvalues of cleaned matrices:")
print("Threshold Negative      :", np.round(eigvals_thresh, decimals=12))
print("Replace Negative        :", eigvals_replace)
print("Absolute Value          :", eigvals_abs)
print("PM Estimator            :", eigvals_pme)
print("PM Estimator (Fixed Tr.):", eigvals_pme_ft)
# Eigenvalues of cleaned matrices:
# Threshold Negative      : [0.          0.          0.58816645  0.60256691  0.82920843  0.84350457, 0.86596268  1.08551965  1.25500039  1.62205361]
# Replace Negative        : [0.1        0.1        0.58816645 0.60256691 0.82920843 0.84350457, 0.86596268 1.08551965 1.25500039 1.62205361]
# Absolute Value          : [0.55457948 0.58816645 0.60256691 0.74002933 0.82920843 0.84350457, 0.86596268 1.08551965 1.25500039 1.62205361]
# PM Estimator            : [0.22083797 0.25204088 0.7016114  0.71148757 0.88221069 0.89388246, 0.91241481 1.10470297 1.26359962 1.62308834]
# PM Estimator (Fixed Tr.): [0.16493152 0.18823523 0.52399428 0.53137025 0.65887379 0.66759078, 0.68143155 0.82504082 0.94371183 1.21219384]
```

## Example 2: PM and PM-FT Estimation using Cross-Validation
We generate a covariance matrix with a Toeplitz structure with d=10 and we draw n=20 observations from a Normal distribution with mean 0.
``` python
# Generate data
np.random.seed(0)
d = 10
n = 20
rho = 0.8
cov_matrix = np.fromfunction(lambda i, j: rho ** np.abs(i - j), (d, d))
X = np.random.multivariate_normal(np.zeros(d), cov_matrix, size=n)
> S = sample_cov(X)

> X = X.to_numpy()
> sigma_range = np.linspace(0.01, 2.0, 150)

# PM cross validation
> pm = PosteriorMeanEstimator(fixed_trace=False)
> sigma_pm = pm.cross_validate_sigma(X, sigma_range)
> print(sigma_pm)
# 0.2504026845637584
> Sigma_pm, Sigma_pm_inv = pm.fit(S, sigma_pm)

# FT cross validation
> ft = PosteriorMeanEstimator(fixed_trace=True)
> sigma_ft = ft.cross_validate_sigma(X, sigma_range)
> print(sigma_ft)
# 0.2771140939597316
> Sigma_ft, Sigma_ft_inv = ft.fit(S, sigma_ft)
```

## References
- Boudt, K., J. Cremers, K. Dragun, and S. Vanduffel (2025). Well-conditioned covariance estimation via bayesian eigenvalue regularization. Working paper.
- Ledoit, O. and M. Wolf (2004). Honey, I shrunk the sample covariance matrix. The Journal of Portfolio Management 30 (4), 110-119.
- Ledoit, O. and M. Wolf (2022). Quadratic shrinkage for large covariance matrices. Bernoulli 28 (3), 1519-1547.
- Rousseeuw, P. J. and G. Molenberghs (1993). Transformation of non positive semidefinite correlation matrices. Communications in Statistics–Theory and Methods 22 (4), 965-984.


