# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       clireg.py
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

from clireg.pybind.clireg_pybind import CorrespondenceVector

PointCloud = np.ndarray  # Nx3
NormalCloud = np.ndarray  # Nx3
FeatureCloud = np.ndarray  # NxF
Transformation = np.ndarray  # 4x4

__all__ = [
    "PointCloud",
    "NormalCloud",
    "FeatureCloud",
    "Transformation",
    "CorrespondenceVector",
]
