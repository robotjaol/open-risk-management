"""Small sanity checks that notebooks call so wrong numbers fail loudly."""

import numpy as np


def assert_close(actual, expected, tolerance=1e-8, label=""):
    """Raise when two numbers differ by more than the tolerance."""
    if not np.isclose(actual, expected, atol=tolerance, rtol=tolerance):
        raise AssertionError(f"{label} expected {expected}, got {actual}")
    return True


def assert_probability(values, label=""):
    """All values must be between 0 and 1."""
    values = np.asarray(values, dtype=float)
    if np.any(values < 0) or np.any(values > 1) or np.any(np.isnan(values)):
        raise AssertionError(f"{label} has values outside [0, 1]")
    return True
