from .config import GAMMA, THETA, MAX_ITERATIONS

class ValueIteration:

    def __init__(self, river):
        self.river = river
        self.states = river.get_states()
        self.value_iteration = {state: 0 for state in self.states}
        self.policy = {}
        self.iterations = 0
        self.converged = False
        self.max_update = float('inf')

    def execute(self, show=True):
        """Apply synchronous Bellman updates until the update tolerance or iteration cap.

        With gamma=1 this stopping check is empirical for this finite environment;
        it is not a general contraction guarantee or a bound on policy error.
        """
        if show:
            print('\nRUNNING VALUE ITERATION')
        for k in range(MAX_ITERATIONS):
            v_k = {}
            for state in self.states:
                if state in self.river.terminal_states:
                    v_k[state] = 0.0
                    continue
                max_value = float('-inf')
                for action in self.river.get_actions(state):
                    value = 0.0
                    for next_state in self.states:
                        prob = self.river.transition_probabilities(state, action, next_state)
                        if prob > 0:
                            reward = self.river.get_reward(state, action, next_state)
                            value += prob * (reward + GAMMA * self.value_iteration[next_state])
                    max_value = max(max_value, value)
                v_k[state] = max_value
            self.max_update = max(abs(v_k[state] - self.value_iteration[state]) for state in self.states)
            check = self.max_update < THETA
            self.value_iteration = v_k
            self.iterations = k + 1
            if check:
                self.converged = True
                if show:
                    print(f'\nUpdate tolerance reached after {self.iterations} iterations')
                break
        if show and not self.converged:
            print(f'Update tolerance was not reached within {MAX_ITERATIONS} iterations')
        self.optimal_policy()
        return (self.value_iteration, self.policy)

    def optimal_policy(self):
        """Extract a greedy policy from the current value estimates."""
        for state in self.states:
            if state in self.river.terminal_states:
                self.policy[state] = None
                continue
            best_policy = None
            best_value = float('-inf')
            for action in self.river.get_actions(state):
                value = 0
                for next_state in self.states:
                    prob = self.river.transition_probabilities(state, action, next_state)
                    if prob > 0:
                        reward = self.river.get_reward(state, action, next_state)
                        value += prob * (reward + GAMMA * self.value_iteration[next_state])
                if value > best_value:
                    best_value = value
                    best_policy = action
            self.policy[state] = best_policy

    def print_values(self):
        """Print estimated state values, with terminal values fixed at zero."""
        print('\n')
        print('=' * 70)
        print('ESTIMATED STATE VALUES V(s)')
        print('=' * 70)
        for i in range(self.river.rows):
            row = []
            for j in range(self.river.cols):
                state = (i, j)
                value = self.value_iteration[state]
                if state in self.river.islands:
                    row.append(' ISLAND ')
                elif state in self.river.terminal_states:
                    row.append('EXIT')
                else:
                    row.append(f'{value:6.2f}')
            print(' | '.join(row))

    def print_policy(self):
        """Print the greedy policy for the current value estimates."""
        print('\n')
        print('=' * 70)
        print('GREEDY POLICY FOR THE CURRENT VALUES')
        print('=' * 70)
        action_symbols = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→', 'stay': 'o', None: '·'}
        for i in range(self.river.rows):
            row = []
            for j in range(self.river.cols):
                state = (i, j)
                action = self.policy.get(state)
                if state in self.river.islands:
                    row.append('  I ')
                elif state in self.river.terminal_states:
                    row.append('  E ')
                elif state == self.river.initial_state:
                    symbol = action_symbols.get(action, '·')
                    row.append(f' {symbol}S ')
                else:
                    symbol = action_symbols.get(action, '·')
                    row.append(f'  {symbol} ')
            print(' | '.join(row))
        print('\nLegend: ↑=up, ↓=down, ←=left, →=right, o=stay, S=start, E=exit, I=island')
