import argparse
import matplotlib
# Use a non-interactive backend so saving works in headless environments
matplotlib.use("Agg")
from .gbm_simulator import GBMSimulator


def _run_simulation(y0, mu, sigma, T, N, output):
    simulator = GBMSimulator(y0, mu, sigma)
    t_values, y_values = simulator.simulate_path(T, N)
    simulator.plot_path(t_values, y_values, output=output)


def main():
    # Support two modes for backward compatibility:
    # 1) Old style: `pygbm --y0 ... --mu ...` (no subcommand)
    # 2) New style: `pygbm simulate_path --y0 ...` (subcommand)
    parser = argparse.ArgumentParser(description="Simulate Geometric Brownian Motion")

    subparsers = parser.add_subparsers(dest="command")

    # simulate_path subcommand
    sim_parser = subparsers.add_parser("simulate_path", help="Simulate a GBM path and optionally save a plot")
    sim_parser.add_argument("--y0", type=float, required=True, help="Initial value Y(0)")
    sim_parser.add_argument("--mu", type=float, required=True, help="Drift coefficient")
    sim_parser.add_argument("--sigma", type=float, required=True, help="Diffusion coefficient")
    sim_parser.add_argument("--T", type=float, required=True, help="Total time for simulation")
    sim_parser.add_argument("--N", type=int, required=True, help="Number of time steps")
    sim_parser.add_argument("--output", type=str, help="Output file for the plot")

    # Also accept the old no-subcommand flags for compatibility
    parser.add_argument("--y0", type=float, help="Initial value Y(0)")
    parser.add_argument("--mu", type=float, help="Drift coefficient")
    parser.add_argument("--sigma", type=float, help="Diffusion coefficient")
    parser.add_argument("--T", type=float, help="Total time for simulation")
    parser.add_argument("--N", type=int, help="Number of time steps")
    parser.add_argument("--output", type=str, help="Output file for the plot")

    args = parser.parse_args()

    if args.command == "simulate_path":
        _run_simulation(args.y0, args.mu, args.sigma, args.T, args.N, args.output)
    else:
        # assume direct flags were used (old behavior)
        if None in (args.y0, args.mu, args.sigma, args.T, args.N):
            parser.error("Either provide the 'simulate_path' subcommand or pass all required flags directly")
        _run_simulation(args.y0, args.mu, args.sigma, args.T, args.N, args.output)


if __name__ == "__main__":
    main()