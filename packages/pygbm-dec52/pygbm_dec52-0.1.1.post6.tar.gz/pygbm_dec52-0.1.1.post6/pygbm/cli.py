"""
Command-line interface (CLI) tool for simulating and plotting Geometric Brownian Motion (GBM) paths.

This script provides a simple command-line interface to the GBM simulator implemented
in the `pygbm` package. It allows users to specify model parameters such as drift, 
volatility, time horizon, and output file path, and generates a plot of the simulated 
GBM path saved to disk.

Example
-------
Run the following command from a terminal to simulate and save a GBM path:

    python gbm_cli.py simulate --y0 1.0 --mu 0.05 --sigma 0.2 --T 2.0 --N 300 --output gbm_plot.png

Requirements
------------
- pygbm (module containing GBMSimulator)
- matplotlib
- numpy
"""

import argparse
import pygbm
import matplotlib.pyplot as plt


def plot_and_save(y0: float, mu: float, sigma: float, T: float, N: int, output_path: str) -> None:
    """
    Simulates a Geometric Brownian Motion (GBM) path and saves the resulting plot to a file.

    This function creates a GBMSimulator instance, generates a sample path using the provided
    parameters, and plots the resulting process. The plot is then saved as an image file
    (e.g., PNG or PDF) at the specified output path.

    Parameters
    ----------
    y0 : float
        Initial value of the GBM process (Y₀).
    mu : float
        Drift parameter (expected rate of return).
    sigma : float
        Volatility (diffusion coefficient) of the process.
    T : float
        Total time horizon (end time) for the simulation.
    N : int
        Number of discrete steps to simulate between 0 and T.
    output_path : str
        File path where the generated plot will be saved.

    Returns
    -------
    None
        The function does not return any value; it saves a plot file to disk.

    Example
    -------
    >>> plot_and_save(1.0, 0.05, 0.2, 2.0, 300, "gbm_plot.png")
    # Saves a PNG file with a simulated GBM path.
    """
    simulator = pygbm.gbm_simulator.GBMSimulator(y0, mu, sigma)
    t, y = simulator.simulate_path(T, N)

    plt.plot(t, y, label="GBM Path")
    plt.xlabel("Time")
    plt.ylabel("Y(t)")
    plt.title("Simulated Geometric Brownian Motion Path")
    plt.legend()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    """
    Entry point for the GBM command-line interface (CLI).

    Parses command-line arguments and executes the selected subcommand.
    The main subcommand supported is "simulate", which runs a GBM simulation
    and saves the plot to a user-specified output file.

    Command-line Arguments
    ----------------------
    --y0 : float, optional
        Initial value of the process (default: 1.0)
    --mu : float, optional
        Drift parameter (default: 0.05)
    --sigma : float, optional
        Volatility parameter (default: 0.2)
    --T : float, optional
        End time for simulation (default: 1.0)
    --N : int, optional
        Number of simulation steps (default: 100)
    --output : str, optional
        Output file path for the generated plot (default: "plot.png")

    Usage
    -----
    Example terminal command:
        python gbm_cli.py simulate --y0 1.0 --mu 0.05 --sigma 0.2 --T 2.0 --N 300 --output gbm_plot.png

    Returns
    -------
    None
        Executes the selected command and saves the output.
    """
    parser = argparse.ArgumentParser(description="Geometric Brownian Motion (GBM) CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    parser_sim = subparsers.add_parser(
        "simulate",
        help="Simulate a geometric Brownian motion process and save the resulting plot."
    )
    parser_sim.add_argument("--y0", type=float, default=1.0, help="Starting value (default: 1.0)")
    parser_sim.add_argument("--mu", type=float, default=0.05, help="Drift term (default: 0.05)")
    parser_sim.add_argument("--sigma", type=float, default=0.2, help="Diffusion term (default: 0.2)")
    parser_sim.add_argument("--T", type=float, default=1.0, help="End time (default: 1.0)")
    parser_sim.add_argument("--N", type=int, default=100, help="Number of steps (default: 100)")
    parser_sim.add_argument("--output", type=str, default="plot.png", help="Output path (default: plot.png)")

    args = parser.parse_args()

    if args.command == "simulate":
        plot_and_save(args.y0, args.mu, args.sigma, args.T, args.N, args.output)


if __name__ == "__main__":
    main()
