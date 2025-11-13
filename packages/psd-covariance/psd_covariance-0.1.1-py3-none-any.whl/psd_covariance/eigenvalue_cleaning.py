import numpy as np

class EigenvalueCleaning:
    @staticmethod
    def threshold_negative(cov, fixed_trace=False):
        eigvals, eigvecs = np.linalg.eigh(cov)
        eigvals_new = np.maximum(eigvals, 0.0)

        if fixed_trace:
            eigvals_new *= np.sum(eigvals) / max(np.sum(eigvals_new), 1e-12)

        new_cov = eigvecs @ np.diag(eigvals_new) @ eigvecs.T
        inv_diag = np.divide(1.0, eigvals_new, out=np.zeros_like(eigvals_new), where=eigvals_new > 1e-12)
        new_cov_inv = eigvecs @ np.diag(inv_diag) @ eigvecs.T

        return new_cov, new_cov_inv

    @staticmethod
    def replace_negative(cov, epsilon=1e-4, fixed_trace=False, PD=False):
        eigvals, eigvecs = np.linalg.eigh(cov)
        if PD:
            eigvals_new = np.where(eigvals <= 1e-10, epsilon, eigvals)
        else:
            eigvals_new = np.where(eigvals < 0, epsilon, eigvals)

        if fixed_trace:
            eigvals_new *= np.sum(eigvals) / max(np.sum(eigvals_new), 1e-12)

        new_cov = eigvecs @ np.diag(eigvals_new) @ eigvecs.T
        inv_diag = np.divide(1.0, eigvals_new, out=np.zeros_like(eigvals_new), where=eigvals_new > 1e-12)
        new_cov_inv = eigvecs @ np.diag(inv_diag) @ eigvecs.T

        return new_cov, new_cov_inv

    @staticmethod
    def absolute_negative(cov, fixed_trace=False, PD=False):
        eigvals, eigvecs = np.linalg.eigh(cov)
        eigvals_new = np.abs(eigvals)
        min_value = np.min(eigvals_new)
        if PD:
            eigvals_new = np.where(eigvals_new == 0, min_value, eigvals_new)

        if fixed_trace:
            eigvals_new *= np.sum(eigvals) / max(np.sum(eigvals_new), 1e-12)

        new_cov = eigvecs @ np.diag(eigvals_new) @ eigvecs.T
        inv_diag = np.divide(1.0, eigvals_new, out=np.zeros_like(eigvals_new), where=eigvals_new > 1e-12)
        new_cov_inv = eigvecs @ np.diag(inv_diag) @ eigvecs.T

        return new_cov, new_cov_inv
