# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       io.py
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


def load_ply(path: str) -> np.ndarray:
    """
    Loads a PLY file (ASCII format) containing only xyz.

    Parameters
    ----------
    path : str
        Path to the .ply file.

    Returns
    -------
    np.ndarray
        Nx3 array of point coordinates.
    """
    with open(path, "r") as f:
        lines = f.readlines()

    # Find header end
    i = 0
    while not lines[i].strip().startswith("end_header"):
        i += 1
    data = lines[i + 1 :]

    points = []
    for line in data:
        tokens = line.strip().split()
        if len(tokens) < 3:
            continue
        points.append([float(tokens[0]), float(tokens[1]), float(tokens[2])])
    return np.array(points, dtype=np.float32)


def save_ply(points: np.ndarray, path: str):
    """
    Saves a Nx3 numpy array to a PLY ASCII file.

    Parameters
    ----------
    points : np.ndarray
        Nx3 array of point coordinates.
    path : str
        Output .ply file path.
    """
    with open(path, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")
        for p in points:
            f.write(f"{p[0]} {p[1]} {p[2]}\n")
