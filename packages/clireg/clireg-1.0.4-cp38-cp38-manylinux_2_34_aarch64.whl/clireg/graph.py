# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       graph.py
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

from clireg.pybind.clireg_pybind import GraphParameters, SimpleGraphGenerator


class GraphConfig:
    """
    High-level wrapper for configuring graph construction parameters.
    """

    def __init__(self):
        self.params = GraphParameters()

    def set_defaults(self, use_features=True, use_keypoints=True):
        self.params.use_features = use_features
        self.params.use_keypoints = use_keypoints
        return self

    def get(self):
        return self.params


class GraphGenerator:
    """
    Wrapper around SimpleGraphGenerator with predefined interface.
    """

    def __init__(self):
        self._generator = SimpleGraphGenerator()

    def generate(self, src_kpts, tgt_kpts, src_feat, tgt_feat, vertices):
        return self._generator.generate(src_kpts, tgt_kpts, src_feat, tgt_feat, vertices)
