# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       pipeline.py
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


class CliRegPipeline:
    def __init__(self):
        pass

    def _logToConsole(self):
        import rich
        from rich.console import Console

        console = Console()
        console.print(1 == 1, ":thumbs_up:")
        console.print(1 == 2, ":thumbs_down:")
        try:
            1 / 0
        except Exception:
            console.print_exception()

    def _logToFile(self, message):
        import logging

        logging.basicConfig(filename="pipeline.log", level=logging.DEBUG)
        logging.debug(message)
