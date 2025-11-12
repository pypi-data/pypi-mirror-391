# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       core.py
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

from clireg.pybind.clireg_pybind import (
    CliqueParameters,
    GraphParameters,
    RegistrationResult,
    createSolver,
)


class Registration:
    """
    Main class for robust point cloud registration using clique graphs.

    Parameters
    ----------
    graph_params : GraphParameters, optional
        Parameters for the graph generator.
    clique_params : CliqueParameters, optional
        Parameters for the clique search algorithm.
    """

    def __init__(
        self,
        graph_params: GraphParameters = GraphParameters(),
        clique_params: CliqueParameters = CliqueParameters(),
    ):
        self._solver = createSolver("default", graph_params, clique_params)

    def set_input(
        self,
        source,
        target,
        *,
        source_normals=None,
        target_normals=None,
        source_keypoints=None,
        target_keypoints=None,
        source_features=None,
        target_features=None,
    ):
        """
        Sets the input clouds and optional data for registration.

        Parameters
        ----------
        source : np.ndarray
            Source point cloud (Nx3).
        target : np.ndarray
            Target point cloud (Nx3).
        source_normals, target_normals : np.ndarray, optional
            Normals for each point.
        source_keypoints, target_keypoints : np.ndarray, optional
            Keypoints of each cloud.
        source_features, target_features : np.ndarray, optional
            Descriptors per point.
        """
        self._solver.setSourceCloud(source)
        self._solver.setTargetCloud(target)
        if source_normals is not None:
            self._solver.setSourceNormals(source_normals)
        if target_normals is not None:
            self._solver.setTargetNormals(target_normals)
        if source_keypoints is not None:
            self._solver.setSourceKeypoints(source_keypoints)
        if target_keypoints is not None:
            self._solver.setTargetKeypoints(target_keypoints)
        if source_features is not None:
            self._solver.setSourceFeatures(source_features)
        if target_features is not None:
            self._solver.setTargetFeatures(target_features)

    def compute(self) -> RegistrationResult:
        """
        Executes the registration algorithm.

        Returns
        -------
        RegistrationResult
            Object containing the transformation, RMSE, fitness, and inliers.
        """
        return self._solver.compute()

    def get_result(self) -> RegistrationResult:
        """
        Returns the result of the registration.

        Returns
        -------
        RegistrationResult
            Result of the last compute() execution.
        """
        return self._solver.getRegistrationResult()
