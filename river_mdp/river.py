import random
import numpy as np
from .config import *

class River:

    def __init__(self, rows=ROWS, cols=COLS, num_islands=NUM_ISLANDS, seed=None):
        if rows < 3 or cols < 3:
            raise ValueError('The river needs at least three rows and columns')
        if not 0 <= num_islands <= (rows - 2) * (cols - 2):
            raise ValueError('The number of islands exceeds the available interior cells')
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.rows = rows
        self.cols = cols
        self.exit_col = cols - 1
        self.num_islands = num_islands
        self.initial_state = (random.randint(0, rows - 1), START_COL)
        self.islands = self.generate_islands()
        self.river_strength = self.generate_river_strength()
        self.terminal_states = set()
        for i in range(rows):
            self.terminal_states.add((i, self.exit_col))
        self.terminal_states.update(self.islands)

    def generate_islands(self):
        """Draw interior island positions.

        Random draws are made with a finite retry limit, exactly as submitted, so a
        seed that used to produce a layout still produces the same one. If the limit
        is reached first (more than 100 islands, or a nearly full river), the missing
        islands are drawn without replacement from the free interior cells, so every
        count accepted by the constructor can be placed.
        """
        islands = set()
        attempts = 0
        max_attempts = 100
        while len(islands) < self.num_islands and attempts < max_attempts:
            i = random.randint(1, self.rows - 2)
            j = random.randint(1, self.cols - 2)
            islands.add((i, j))
            attempts += 1
        missing = self.num_islands - len(islands)
        if missing:
            free = [(i, j) for i in range(1, self.rows - 1) for j in range(1, self.cols - 1)
                    if (i, j) not in islands]
            islands.update(random.sample(free, missing))
        return islands

    def generate_river_strength(self):
        """Draw current strengths for interior columns; banks have no current."""
        river_strength = np.zeros(self.cols)
        for j in range(self.cols):
            if j == 0 or j == self.cols - 1:
                river_strength[j] = 0.0
            else:
                river_strength[j] = round(random.uniform(MIN_CURRENT, MAX_CURRENT), 2)
        return river_strength

    def get_states(self):
        """Enumerate the finite state space."""
        states = []
        for i in range(self.rows):
            for j in range(self.cols):
                states.append((i, j))
        return states

    def get_next_state(self, state, action):
        """Return the intended destination before current or boundary checks."""
        i, j = state
        if action == 'up':
            return (i - 1, j)
        elif action == 'down':
            return (i + 1, j)
        elif action == 'left':
            return (i, j - 1)
        elif action == 'right':
            return (i, j + 1)
        elif action == 'stay':
            return state
        else:
            return state

    def valid_state(self, state):
        """Check whether a state lies inside the grid."""
        i, j = state
        return 0 <= i < self.rows and 0 <= j < self.cols

    def transition_probabilities(self, state, action, next_state):
        """Return P(next_state | state, action) for the submitted river model.

        A blocked voluntary move stays in place. A downward move is deterministic.
        Other valid moves split between the intended cell and a downward push.
        A push into an island is terminal, unlike an attempted voluntary entry.
        """
        if state in self.terminal_states:
            return 1.0 if next_state == state else 0.0
        i, j = state
        wanted_state = self.get_next_state(state, action)
        if not self.valid_state(wanted_state) or wanted_state in self.islands:
            return 1.0 if next_state == state else 0.0
        pushed_state = (i + 1, j) if i + 1 < self.rows else state
        if not self.valid_state(pushed_state):
            pushed_state = state
        if action == 'down':
            if next_state == wanted_state:
                return 1.0
            else:
                return 0.0
        else:
            pdir = 1 - self.river_strength[j]
            pdown = self.river_strength[j]
            if wanted_state == pushed_state:
                return 1.0 if next_state == wanted_state else 0.0
            if next_state == wanted_state:
                return pdir
            elif next_state == pushed_state:
                return pdown
            else:
                return 0.0

    def get_reward(self, state, action, next_state):
        """Return R(state, action, next_state), paid on the transition into the cell."""
        _, j_n = next_state
        if j_n == self.exit_col:
            return REWARD_EXIT
        if next_state in self.islands:
            return REWARD_ISLAND
        return REWARD_STEP

    def get_actions(self, state):
        """Return the action set; terminal states have no actions."""
        if state in self.terminal_states:
            return []
        return ACTIONS.copy()

    def __str__(self):
        """Return a text representation of the grid."""
        grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                pos = (i, j)
                if pos == self.initial_state:
                    box = SYMBOLS['captain']
                elif j == self.exit_col and pos not in self.islands:
                    box = SYMBOLS['exit']
                elif pos in self.islands:
                    box = SYMBOLS['island']
                elif j == 0 or j == self.cols - 1:
                    box = ' '
                else:
                    box = SYMBOLS['river']
                row.append(f'|{box:^5}|')
            grid.append(''.join(row))
        return '\n'.join(grid)

    def print_info(self):
        """Print the generated river layout and current strengths."""
        print('=' * 70)
        print('RIVER INFORMATION')
        print('=' * 70)
        print(f'Dimensions: {self.rows} rows x {self.cols} columns')
        print(f'Initial state: {self.initial_state}')
        print(f'Exit (last column): column {self.exit_col}')
        print(f'Islands (hazards): {self.islands}')
        print(f'\nCurrent strength by column:')
        for j, strength in enumerate(self.river_strength):
            column_type = 'Bank' if strength == 0.0 else 'Interior'
            print(f'Column {j} ({column_type}): {strength:.2f}')
        print('\n')
        print(str(self))
