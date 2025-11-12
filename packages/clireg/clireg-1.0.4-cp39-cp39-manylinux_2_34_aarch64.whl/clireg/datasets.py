# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       dataset.py
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


def generate_synthetic_pair(n_points=100, noise=0.01, transform=None):
    """
    Generates a synthetic source-target pair of point clouds for registration testing.

    Parameters
    ----------
    n_points : int
        Number of points to generate.
    noise : float
        Standard deviation of Gaussian noise to apply to target.
    transform : np.ndarray, optional
        4x4 transformation to apply to source.

    Returns
    -------
    source : np.ndarray
        Original point cloud.
    target : np.ndarray
        Transformed and noisy point cloud.
    gt_transform : np.ndarray
        Ground truth transformation applied.
    """
    source = np.random.rand(n_points, 3).astype(np.float32)

    if transform is None:
        angle = np.pi / 12
        R = np.array(
            [[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]]
        )
        t = np.array([0.05, -0.03, 0.02])
        transform = np.eye(4, dtype=np.float32)
        transform[:3, :3] = R
        transform[:3, 3] = t

    ones = np.ones((n_points, 1), dtype=np.float32)
    homogeneous = np.hstack((source, ones))
    target = (homogeneous @ transform.T)[:, :3]
    target += np.random.normal(scale=noise, size=target.shape).astype(np.float32)

    return source, target, transform
