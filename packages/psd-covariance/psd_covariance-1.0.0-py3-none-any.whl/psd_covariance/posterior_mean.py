import numpy as np
from scipy.special import log_ndtr
from joblib import Parallel, delayed
from sklearn.model_selection import KFold
from psd_covariance.utils import sample_cov

class PosteriorMeanEstimator:
    def __init__(self, fixed_trace=False):
        self.fixed_trace = fixed_trace
        self.sigma = None
        self.Sigma_ = None
        self.Sigma_inv_ = None

    def fit(self, Sigma_tilde, sigma):
        E_tilde, Q = np.linalg.eigh(Sigma_tilde)
        x = E_tilde / sigma

        # for numerical precision.
        log_phi = -0.5 * x ** 2 - 0.5 * np.log(2 * np.pi)
        log_Phi = log_ndtr(x)
        log_ratio = log_phi - log_Phi
        ratio = np.exp(log_ratio)
        E_hat_values = E_tilde + sigma * ratio

        if self.fixed_trace:
            old_trace = np.sum(E_tilde)
            new_trace = np.sum(E_hat_values)
            if new_trace > 0:
                E_hat_values *= old_trace / new_trace

        self.Sigma_ = Q @ np.diag(E_hat_values) @ Q.T
        E_hat_inv = np.divide(1.0, E_hat_values, out=np.zeros_like(E_hat_values), where=E_hat_values > 1e-12)
        self.Sigma_inv_ = Q @ np.diag(E_hat_inv) @ Q.T
        self.sigma = sigma

        return self.Sigma_, self.Sigma_inv_

    def cross_validate_sigma(self, X, sigma_range, n_splits=10, n_jobs=-1, random_state=42):
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        def evaluate_fold(X_train, X_test, sigma):
            try:
                cov_sample = sample_cov(X_train)
                Sigma, Sigma_inv = self.fit(cov_sample, sigma)

                eigvals = np.linalg.eigvalsh(Sigma)
                log_det = np.sum(np.log(np.clip(eigvals, 1e-12, None)))

                d = X.shape[1]
                ll = [
                    -0.5 * (x @ Sigma_inv @ x + log_det + d * np.log(2 * np.pi))
                    for x in X_test
                ]
                return np.sum(ll)
            except np.linalg.LinAlgError:
                return -np.inf

        scores = []
        for sigma in sigma_range:
            fold_scores = Parallel(n_jobs=n_jobs)(
                delayed(evaluate_fold)(X[train], X[test], sigma)
                for train, test in kf.split(X)
            )
            scores.append(np.mean(fold_scores))

        best_sigma = sigma_range[np.argmax(scores)]
        self.sigma = best_sigma
        return best_sigma