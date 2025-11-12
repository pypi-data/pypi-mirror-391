# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       __init__.py
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


__version__ = "1.0.4"

from clireg.core import Registration
from clireg.datasets import generate_synthetic_pair
from clireg.features import FeatureExtractor, KeypointExtractor
from clireg.graph import GraphConfig, GraphGenerator
from clireg.io import load_ply, save_ply
from clireg.pybind.clireg_pybind import GraphParameters, RegistrationResult
from clireg.types import (
    CorrespondenceVector,
    FeatureCloud,
    NormalCloud,
    PointCloud,
    Transformation,
)
from clireg.utils import apply_transformation, compute_rmse
from clireg.vis import visualize_point_clouds

__all__ = [
    "Registration",
    "GraphConfig",
    "GraphGenerator",
    "KeypointExtractor",
    "FeatureExtractor",
    "load_ply",
    "save_ply",
    "visualize_point_clouds",
    "apply_transformation",
    "compute_rmse",
    "generate_synthetic_pair",
    "GraphParameters",
    "RegistrationResult",
    "PointCloud",
    "NormalCloud",
    "FeatureCloud",
    "Transformation",
    "CorrespondenceVector",
]
