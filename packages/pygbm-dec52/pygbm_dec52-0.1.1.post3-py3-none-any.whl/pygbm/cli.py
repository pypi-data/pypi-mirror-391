import argparse
import pygbm
import matplotlib.pyplot as plt

def plot_and_save(y0, mu, sigma, T, N, output_path):
    """
    Simulates a GBM process and saves it to a file
    """
    simulator = pygbm.gbm_simulator.GBMSimulator(y0, mu, sigma)
    t, y = simulator.simulate_path(T, N)

    plt.plot(t, y, label="GBM Path")
    plt.xlabel("Time")
    plt.ylabel("Y(t)")
    plt.title("Simulated Geometric Brownian Motion Path")
    plt.legend()
    plt.savefig(output_path)

def main():
    parser = argparse.ArgumentParser(description="GBM CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    parser_sim = subparsers.add_parser("simulate", help="Simulate geometric Brownian motion process")
    parser_sim.add_argument("--y0", type=float, default=1.0, help="Starting value")
    parser_sim.add_argument("--mu", type=float, default=0.05, help="Drift term")
    parser_sim.add_argument("--sigma", type=float, default=0.2, help="Diffusion term")
    parser_sim.add_argument("--T", type=float, default=1.0, help="End time")
    parser_sim.add_argument("--N", type=int, default=100, help="Number of steps")
    parser_sim.add_argument("--output", type=str, default="plot.png", help="Output path")

    args = parser.parse_args()
    if args.command == "simulate":
        plot_and_save(args.y0, args.mu, args.sigma, args.T, args.N, args.output)

if __name__ == "__main__":
    main()