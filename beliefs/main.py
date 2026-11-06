"""Run a manual belief-guided palace agent, or display its initial belief update."""
import argparse
import random

from .agents import run_bayesian_agent
from .bayesian import Bayesian
from .config import N_GRIDS, MAX_RISK
from .functions import print_all_heatmaps
from .palace import Palace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--demo', action='store_true', help='Display the initial update without requesting input')
    parser.add_argument('--show-map', action='store_true', help='Reveal hidden objects for debugging')
    args = parser.parse_args()
    random.seed(args.seed)
    palace = Palace(N_GRIDS)
    if args.show_map:
        print('Full layout (debugging):')
        print(palace.__str__(hidden=False))
    if args.demo:
        beliefs = Bayesian(N_GRIDS)
        beliefs.update(palace.captain, palace.get_percepts())
        print_all_heatmaps(beliefs)
        print(f'Seed: {args.seed}; initial position: {palace.captain}')
        print(f'Unvisited neighbours with score <= {MAX_RISK}: '
              f'{beliefs.get_low_risk_neighbours(palace.captain)}')
    else:
        success = run_bayesian_agent(palace)
        print(f'Mission completed: {success}')


if __name__ == '__main__':
    main()
