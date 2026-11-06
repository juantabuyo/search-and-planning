"""Run the logical palace agent with a reproducible generated layout."""
import argparse
import random

from .agents import run_bfs_agent, run_manual_agent
from .config import N_GRIDS
from .palace import Palace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--mode', choices=['auto', 'manual'], default='auto')
    parser.add_argument('--show-map', action='store_true', help='Reveal the layout for debugging')
    parser.add_argument('--quiet', action='store_true', help='Show only the automated outcome')
    args = parser.parse_args()
    random.seed(args.seed)
    palace = Palace(N_GRIDS)
    if args.show_map:
        print('Full layout (debugging):')
        print(palace)
    if args.mode == 'manual':
        run_manual_agent(palace, show=True)
    else:
        success, path = run_bfs_agent(palace, show=not args.quiet)
        print(f'Seed: {args.seed}; success: {success}; recorded actions: {len(path)}')


if __name__ == '__main__':
    main()
