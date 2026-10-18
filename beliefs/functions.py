import random

def print_heatmap(probability_positions, n, message):
    """Print a numerical belief map or risk score with its supplied label."""
    print(f'\n{message}')
    print('=' * 60)
    for i in range(n):
        row = []
        for j in range(n):
            val = probability_positions[i, j]
            row.append(f'{val:.3f}')
        print(' '.join(row))
    print()

def print_all_heatmaps(bayesian):
    """Show the trap risk score and separate soldier and exit marginals."""
    n = bayesian.n
    trap_risk_score = bayesian.prob_F + bayesian.prob_P + bayesian.prob_D
    print('=' * 70)
    print('APPROXIMATE MARGINAL BELIEFS AND RISK SCORE')
    print('=' * 70)
    print_heatmap(trap_risk_score, n, 'Trap risk score (sum of three marginal maps; not a union probability)')
    print_heatmap(bayesian.prob_M, n, 'Soldier marginal probability')
    print_heatmap(bayesian.prob_S, n, 'Exit marginal probability')

def random_position(n):
    """Draw a one-based grid position."""
    return (random.randint(1, n), random.randint(1, n))
