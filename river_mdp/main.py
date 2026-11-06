"""Solve the river MDP and simulate its greedy policy locally."""
import argparse
import json
import random
from pathlib import Path

from .config import GAMMA, THETA, MAX_ITERATIONS
from .river import River
from .value_iteration import ValueIteration


def run_test(river, policy, max_steps=100, show=True, rng=None):
    """Simulate at most max_steps transitions, including success on the last one.

    A terminal initial state uses zero transitions. Missing actions stop the
    episode and report the actual count, rather than the whole step allowance.
    """
    if max_steps < 0:
        raise ValueError('max_steps must be non-negative')
    rng = rng if rng is not None else random
    state = river.initial_state
    total_reward = 0
    steps = 0
    if show:
        print(f'Initial state: {state}')
    while state not in river.terminal_states and steps < max_steps:
        action = policy.get(state)
        if action is None:
            break
        destinations = []
        probabilities = []
        for next_state in river.get_states():
            probability = river.transition_probabilities(state, action, next_state)
            if probability > 0:
                destinations.append(next_state)
                probabilities.append(probability)
        next_state = rng.choices(destinations, weights=probabilities)[0]
        reward = river.get_reward(state, action, next_state)
        total_reward += reward
        steps += 1
        if show:
            print(f'Step {steps}: {state} --{action}--> {next_state} (reward={reward:g})')
        state = next_state

    success = (state in river.terminal_states and state[1] == river.exit_col
               and state not in river.islands)
    if show:
        outcome = 'exit reached' if success else 'island reached' if state in river.islands else 'stopped without reaching the exit'
        print(f'Outcome: {outcome}; steps: {steps}; total reward: {total_reward:g}')
    return success, total_reward, steps


def run_multiple_tests(river, policy, n_tests=20, max_steps=100, rng=None):
    """Return simulated outcomes; finite samples do not prove a success probability."""
    if n_tests < 1:
        raise ValueError('n_tests must be positive')
    return [run_test(river, policy, max_steps, show=False, rng=rng)
            for _ in range(n_tests)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=5121111, help='Layout seed (submission default)')
    parser.add_argument('--simulation-seed', type=int, default=2026)
    parser.add_argument('--episodes', type=int, default=20)
    parser.add_argument('--max-steps', type=int, default=100)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--json', type=Path, help='Write current results to this local file')
    args = parser.parse_args()
    if args.episodes < 1 or args.max_steps < 0:
        parser.error('episodes must be positive and max-steps non-negative')
    river = River(seed=args.seed)
    solver = ValueIteration(river)
    values, policy = solver.execute(show=not args.quiet)
    episodes = run_multiple_tests(river, policy, args.episodes, args.max_steps,
                                  random.Random(args.simulation_seed))
    summary = {
        'layout_seed': args.seed,
        'simulation_seed': args.simulation_seed,
        'episodes': args.episodes,
        'max_steps': args.max_steps,
        'initial_state': list(river.initial_state),
        'islands': [list(s) for s in sorted(river.islands)],
        'current_by_column': river.river_strength.tolist(),
        'gamma': GAMMA,
        'tolerance': THETA,
        'iteration_cap': MAX_ITERATIONS,
        'iterations': solver.iterations,
        'update_tolerance_reached': solver.converged,
        'maximum_last_update': solver.max_update,
        'initial_state_value': values[river.initial_state],
        'successes': sum(result[0] for result in episodes),
        'mean_reward': sum(result[1] for result in episodes) / args.episodes,
        'mean_steps': sum(result[2] for result in episodes) / args.episodes,
        'episode_results': [{'success': success, 'reward': reward, 'steps': steps}
                            for success, reward, steps in episodes],
        'values': [[values[(i, j)] for j in range(river.cols)] for i in range(river.rows)],
        'policy': [[policy[(i, j)] for j in range(river.cols)] for i in range(river.rows)],
    }
    if not args.quiet:
        river.print_info()
        solver.print_values()
        solver.print_policy()
    print(f'Seed {args.seed}: {summary["successes"]}/{args.episodes} simulated exits; '
          f'mean reward {summary["mean_reward"]:.2f}; mean steps {summary["mean_steps"]:.2f}')
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
