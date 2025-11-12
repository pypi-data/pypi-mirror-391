# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       utils.py
# Project:    CliReg - Clique-based robust Point Cloud Registration
# Author:     Javier Laserna Moratalla
# Date:       2025-04-08
#
# Description:
# This file is part of the codebase supporting the CliReg algorithm, a clique-based
# method for robust rigid point cloud registration in the presence of outliers.
# The work is developed as part of the PhD thesis:
# "Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#  Applications to SLAM and Social Assistance".
#
# CliReg formulates the registration problem as a maximal clique search on a correspondence graph
# and combines branch-and-bound techniques with consensus evaluation for high robustness and accuracy.
#
# This code is licensed for academic and research purposes only.
# For more information, contact: j.laserna@upm.es
# =============================================================================

import numpy as np


def apply_transformation(points: np.ndarray, transformation: np.ndarray) -> np.ndarray:
    """
    Applies a 4x4 transformation matrix to a Nx3 point cloud.

    Parameters
    ----------
    points : np.ndarray
        Input point cloud (Nx3).
    transformation : np.ndarray
        Transformation matrix (4x4).

    Returns
    -------
    np.ndarray
        Transformed point cloud (Nx3).
    """
    ones = np.ones((points.shape[0], 1), dtype=np.float32)
    homogeneous = np.hstack((points, ones))  # Nx4
    transformed = homogeneous @ transformation.T  # Nx4
    return transformed[:, :3]


def compute_rmse(a: np.ndarray, b: np.ndarray) -> float:
    """
    Computes Root Mean Square Error (RMSE) between two point sets.

    Parameters
    ----------
    a, b : np.ndarray
        Point clouds (Nx3) to compare.

    Returns
    -------
    float
        RMSE value.
    """
    assert a.shape == b.shape, "Point clouds must have the same shape"
    return np.sqrt(np.mean(np.linalg.norm(a - b, axis=1) ** 2))
