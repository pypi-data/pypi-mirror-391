import argparse
from .simulate import GBMSimulator

def main():
    parser = argparse.ArgumentParser(description="This script allows us to use the simulator from Command line")

    #adding input of variables
    parser.add_argument("--y0", type=float, required=True,help="Initial value Y(0)")
    parser.add_argument("--mu", type=float, required=True,help="Drift Coefficient")
    parser.add_argument("--sigma", type=float, required=True,help="Diffusion coefficient")
    parser.add_argument("--T", type=float, required=True, help="Total time for simulation")
    parser.add_argument("--N", type=int, required=True, help="Number of time steps")
    parser.add_argument("--output", type=str, help="Output file for the plot")

    args = parser.parse_args()

    simulator = GBMSimulator(args.y0,args.mu, args.sigma)
    y, t = simulator.simulate_path(args.T, args.N)
    simulator.plot_path(t,y)

if __name__ == "__main__":
    main()

