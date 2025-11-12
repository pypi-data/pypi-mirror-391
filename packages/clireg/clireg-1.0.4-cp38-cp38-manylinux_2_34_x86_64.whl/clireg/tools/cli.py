# =============================================================================
# PhD Thesis: Clique-Based Optimization for Robust Perception and Interaction in Robotics:
#             Applications to SLAM and Social Assistance
# File:       cli.py
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

import typer


def version_callback(value: bool):
    if value:
        try:
            # Check that the python bindings are properly built and can be loaded at runtime
            from clireg.pybind import clireg_pybind
        except ImportError as e:
            print(f"[ERRROR] Python bindings not properly built!")
            print(f"[ERRROR] '{e}'")
            raise typer.Exit(1)

        import clireg

        print(f"[INFO] CliReg Version: {clireg.__version__}")
        raise typer.Exit(0)


app = typer.Typer(add_completion=False, rich_markup_mode="rich")

docstring = f"""
CliReg: Clique-based robust Point Cloud  Registration\n
\b
Examples:\n
# Register two point clouds using the default parameters
$ clireg register --source <path_to_source> --target <path_to_target> --output <path_to_output>\n
"""


@app.command(help=docstring)
def clireg_pipeline(
    source: str = typer.Option(..., "--source", "-s", help="Path to the source point cloud"),
    target: str = typer.Option(..., "--target", "-t", help="Path to the target point cloud"),
    output: str = typer.Option(..., "--output", "-o", help="Path to the output point cloud"),
    # Aditional Options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode"),
    version: bool = typer.Option(
        None, "--version", "-V", callback=version_callback, is_eager=True, help="Show version"
    ),
):
    try:
        # Check that the python bindings are properly built and can be loaded at runtime
        from clireg.pybind import clireg_pybind
    except ImportError as e:
        print(f"[ERRROR] Python bindings not properly built!")
        print(f"[ERRROR] '{e}'")
        raise typer.Exit(1)

    import clireg

    if verbose:
        print(f"[INFO] Source: {source}")
        print(f"[INFO] Target: {target}")
        print(f"[INFO] Output: {output}")
        print(f"[INFO] Verbose: {verbose}")

    clireg.register(source, target, output, verbose)


def main():
    app()
