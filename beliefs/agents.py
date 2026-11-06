from .functions import print_all_heatmaps
from .config import MAX_RISK, MAX_STEPS
from .bayesian import Bayesian

def run_bayesian_agent(palace, show=True):
    """Let the user choose actions after displaying approximate marginal beliefs.

    The neighbouring-cell threshold uses a sum of hazard marginals, not the
    probability of their union. This is a manual agent, not autonomous planning.
    """
    bayesian = Bayesian(palace.n)
    print('\nUSER-GUIDED MARGINAL-BELIEF AGENT')
    print('=' * 70)
    print('Commands: moveU, moveD, moveL, moveR, grenadeU, grenadeD, grenadeL, grenadeR, exit')
    print('=' * 70)
    actions = {'moveu': 'moveU', 'moved': 'moveD', 'movel': 'moveL', 'mover': 'moveR', 'grenadeu': 'grenadeU', 'grenaded': 'grenadeD', 'grenadel': 'grenadeL', 'grenader': 'grenadeR', 'exit': 'exit'}
    steps = 0
    while True:
        steps += 1
        if steps > MAX_STEPS:
            print('=' * 70)
            print(f'END: exceeded MAX_STEPS ({MAX_STEPS}).')
            print('=' * 70)
            return False
        percepts = palace.get_percepts()
        bayesian.update(palace.captain, percepts)
        if show:
            print('\n')
            print('=' * 70)
            print(f'STEP {steps}')
            print('=' * 70)
            print(f'\nVisited map (hidden objects are not shown):')
            print(palace)
            print_all_heatmaps(bayesian)
            print(f'\nPosition: {palace.captain}')
            print(f"Colonel rescued: {('✅' if palace.with_colonel else '❌')}")
            print(f"Grenade available: {('✅' if palace.grenade else '❌')}")
            eF, eP, eD, eM, eS = percepts[:5]
            print('\nPercepts')
            if eF:
                print(' - Kerosene smell (fire nearby)')
            if eP:
                print(' - Creaking floor (spikes nearby)')
            if eD:
                print(' - Visible wires (darts nearby)')
            if eM:
                print(' - Snoring (soldier nearby)')
            if eS:
                print(' - Glow (exit nearby)')
            low_risk_neighbours = bayesian.get_low_risk_neighbours(palace.captain, MAX_RISK)
            if low_risk_neighbours:
                print(f'\nNeighbours below the risk-score threshold (<= {MAX_RISK}): {low_risk_neighbours}')
            else:
                print(f'No unvisited neighbours below risk-score threshold {MAX_RISK}')
        print()
        print('=' * 70)
        inp = input('Action: ').strip().lower()
        if inp not in actions:
            print('Invalid action')
            continue
        action = actions[inp]
        try:
            result = palace.apply_action(action)
            if 'grenade' in action:
                new_percepts = palace.get_percepts()
                if new_percepts[9]:
                    bayesian.soldier_dead()
            if result == 'EXITED':
                print('=' * 70)
                print(f'MISSION COMPLETED IN {steps} STEPS')
                print('=' * 70)
                return True
        except Exception as e:
            print('=' * 70)
            print(f'GAME OVER, step {steps} ☠️')
            print('=' * 70)
            print(f'Cause: {e}')
            return False
