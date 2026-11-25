"""Logistic regression written with NumPy only (Newton Raphson).

Used to show the maths behind the probability of default model.
"""

import numpy as np


def sigmoid(z):
    """Numerically safe logistic function."""
    z = np.clip(z, -35, 35)
    return 1.0 / (1.0 + np.exp(-z))


def fit_logistic(features, target, l2=0.0, max_iter=50, tol=1e-9):
    """Fit coefficients by Newton Raphson.

    features: array of shape (n, k), without an intercept column.
    l2: ridge penalty on the slopes. The intercept is not penalised.
    Returns the intercept, the slopes and the number of iterations used.
    """
    features = np.asarray(features, dtype=float)
    target = np.asarray(target, dtype=float)
    n_rows, n_cols = features.shape
    design = np.column_stack([np.ones(n_rows), features])
    beta = np.zeros(n_cols + 1)
    penalty = np.eye(n_cols + 1) * l2
    penalty[0, 0] = 0.0

    iterations = 0
    for iterations in range(1, max_iter + 1):
        probability = sigmoid(design @ beta)
        gradient = design.T @ (target - probability) - penalty @ beta
        weights = probability * (1 - probability)
        hessian = design.T @ (design * weights[:, None]) + penalty
        step = np.linalg.solve(hessian, gradient)
        beta = beta + step
        if np.max(np.abs(step)) < tol:
            break
    return {"intercept": float(beta[0]), "slopes": beta[1:].copy(), "iterations": iterations}


def predict_proba(features, intercept, slopes):
    """Probability of the bad class."""
    features = np.asarray(features, dtype=float)
    return sigmoid(intercept + features @ np.asarray(slopes))


def standard_errors(features, intercept, slopes):
    """Large sample standard errors from the inverse information matrix."""
    features = np.asarray(features, dtype=float)
    design = np.column_stack([np.ones(len(features)), features])
    probability = predict_proba(features, intercept, slopes)
    weights = probability * (1 - probability)
    information = design.T @ (design * weights[:, None])
    return np.sqrt(np.diag(np.linalg.inv(information)))
