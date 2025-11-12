# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       vis.py
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
import open3d as o3d


def visualize_point_clouds(source: np.ndarray, target: np.ndarray, transformation=None):
    """
    Visualize source and target point clouds using Open3D.

    Parameters
    ----------
    source : np.ndarray
        Nx3 array of source points.
    target : np.ndarray
        Nx3 array of target points.
    transformation : np.ndarray, optional
        4x4 transformation matrix to apply to source.
    """
    pcd_src = o3d.geometry.PointCloud()
    pcd_src.points = o3d.utility.Vector3dVector(source)

    pcd_tgt = o3d.geometry.PointCloud()
    pcd_tgt.points = o3d.utility.Vector3dVector(target)

    pcd_src.paint_uniform_color([1, 0.706, 0])  # orange
    pcd_tgt.paint_uniform_color([0, 0.651, 0.929])  # blue

    if transformation is not None:
        pcd_src.transform(transformation)

    o3d.visualization.draw_geometries([pcd_src, pcd_tgt])
