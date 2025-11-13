# Obtained from Michael Wolfs website @ https://github.com/pald22/covShrinkage/blob/main/QIS.py

import numpy as np
import pandas as pd

class ShrinkageMethods:
    @staticmethod
    def linear_shrinkage(Y):

        # de-mean returns if required
        N, p = Y.shape  # sample size and matrix dimension
        mean = Y.mean(axis=0)
        Y = Y.sub(mean, axis=1)
        # vars
        n = N - 1  # adjust effective sample size

        # Cov df: sample covariance matrix
        sample = pd.DataFrame(np.matmul(Y.T.to_numpy(), Y.to_numpy())) / n

        # compute shrinkage target
        target = pd.DataFrame(np.diag(np.diag(sample.to_numpy())))

        # estimate the parameter that we call pi in Ledoit and Wolf (2003, JEF)
        Y2 = pd.DataFrame(np.multiply(Y.to_numpy(), Y.to_numpy()))
        sample2 = pd.DataFrame(np.matmul(Y2.T.to_numpy(), Y2.to_numpy())) / n  # sample matrix of squared returns
        piMat = pd.DataFrame(sample2.to_numpy() - np.multiply(sample.to_numpy(), sample.to_numpy()))
        pihat = sum(piMat.sum())

        # Estimate gamma
        gammahat = np.linalg.norm(sample.to_numpy() - target, ord='fro') ** 2

        # diagonal part of the parameter that we call rho
        rho_diag = np.sum(np.diag(piMat))

        # off-diagonal part of the parameter that we call rho
        rho_off = 0

        # compute shrinkage intensity
        rhohat = rho_diag + rho_off
        kappahat = (pihat - rhohat) / gammahat
        shrinkage = max(0, min(1, kappahat / n))

        # compute shrinkage estimator
        sigmahat = shrinkage * target + (1 - shrinkage) * sample;
        sigmahat_inv = np.linalg.inv(sigmahat)

        return sigmahat, sigmahat_inv, shrinkage

    @staticmethod
    def quadratic_inverse_shrinkage(Y):
        # Pre-Conditions: Y is a valid pd.dataframe and optional arg- k which can be
        #    None, np.nan or int
        # Post-Condition: Sigmahat dataframe is returned

        # Set df dimensions
        N = Y.shape[0]  # num of columns
        p = Y.shape[1]  # num of rows
        mean = Y.mean(axis=0)
        Y = Y.sub(mean, axis=1)

        # vars
        n = N - 1  # adjust effective sample size
        c = p / n  # concentration ratio

        # Cov df: sample covariance matrix
        sample = pd.DataFrame(np.matmul(Y.T.to_numpy(), Y.to_numpy())) / n
        sample = (sample + sample.T) / 2  # make symmetrical

        # Spectral decomp
        lambda1, u = np.linalg.eigh(sample)  # use LAPACK routines
        lambda1 = lambda1.real  # clip imaginary part due to rounding error
        u = u.real  # clip imaginary part for eigenvectors

        lambda1 = lambda1.real.clip(min=0)  # reset negative values to 0
        dfu = pd.DataFrame(u, columns=lambda1)  # create df with column names lambda
        #                                        and values u
        dfu.sort_index(axis=1, inplace=True)  # sort df by column index
        lambda1 = dfu.columns  # recapture sorted lambda

        # COMPUTE Quadratic-Inverse Shrinkage estimator of the covariance matrix
        h = (min(c ** 2, 1 / c ** 2) ** 0.35) / p ** 0.35  # smoothing parameter
        invlambda = 1 / lambda1[max(1, p - n + 1) - 1:p]  # inverse of (non-null) eigenvalues
        dfl = pd.DataFrame()
        dfl['lambda'] = invlambda
        Lj = dfl[np.repeat(dfl.columns.values, min(p, n))]  # like  1/lambda_j
        Lj = pd.DataFrame(Lj.to_numpy())  # Reset column names
        Lj_i = Lj.subtract(Lj.T)  # like (1/lambda_j)-(1/lambda_i)

        theta = Lj.multiply(Lj_i).div(Lj_i.multiply(Lj_i).add(
            Lj.multiply(Lj) * h ** 2)).mean(axis=0)  # smoothed Stein shrinker
        Htheta = Lj.multiply(Lj * h).div(Lj_i.multiply(Lj_i).add(
            Lj.multiply(Lj) * h ** 2)).mean(axis=0)  # its conjugate
        Atheta2 = theta ** 2 + Htheta ** 2  # its squared amplitude

        if p <= n:  # case where sample covariance matrix is not singular
            delta = 1 / ((1 - c) ** 2 * invlambda + 2 * c * (1 - c) * invlambda * theta
                         + c ** 2 * invlambda * Atheta2)  # optimally shrunk eigenvalues
            delta = delta.to_numpy()
        else:
            delta0 = 1 / ((c - 1) * np.mean(invlambda.to_numpy()))  # shrinkage of null
            #                                                 eigenvalues
            delta = np.repeat(delta0, p - n)
            delta = np.concatenate((delta, 1 / (invlambda * Atheta2)), axis=None)

        deltaQIS = delta * (sum(lambda1) / sum(delta))  # preserve trace

        temp1 = dfu.to_numpy()
        temp2 = np.diag(deltaQIS)
        temp3 = dfu.T.to_numpy().conjugate()
        # reconstruct covariance matrix
        sigmahat = np.matmul(np.matmul(temp1, temp2), temp3)
        sigmahat_inv = np.linalg.inv(sigmahat)

        # sigmahat = pd.DataFrame(sigmahat)
        # sigmahat_inv = pd.DataFrame(sigmahat_inv)

        return sigmahat, sigmahat_inv
