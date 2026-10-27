import random
from .config import N_GRIDS, TRAP_TYPES, TRAP_NAMES, START
from .functions import random_position

class Palace:

    def __init__(self, n=N_GRIDS) -> None:
        """Create a randomly generated palace with the original placement rules."""
        required = 1 + len(TRAP_TYPES) + 1   # start, distinct traps in the worst case, one free cell
        if n * n < required:
            raise ValueError(f'A {n}x{n} palace has {n * n} cells; at least {required} are needed to place all elements.')
        self.n = n
        self.captain = START
        self.visited = {START}
        self.traps = {'F': None, 'P': None, 'D': None}
        self.soldier = None
        self.colonel = None
        self.exit = None
        self.with_colonel = False
        self.grenade = True
        self.last_scream = False
        self.create_palace()

    def create_palace(self):
        """Place traps independently, allowing trap overlap.

        The soldier, colonel and exit avoid traps and the start, but may overlap
        one another, as in the submitted implementation.
        """
        for trap in TRAP_TYPES:
            pos = random_position(self.n)
            while pos == self.captain:
                pos = random_position(self.n)
            self.traps[trap] = pos
        trap_positions = set(self.traps.values())
        available_positions = set()
        for x in range(1, self.n + 1):
            for y in range(1, self.n + 1):
                pos = (x, y)
                if pos not in trap_positions and pos != self.captain:
                    available_positions.add(pos)
        # Sort before sampling so a seed does not depend on set iteration order.
        available = sorted(available_positions)
        self.soldier = random.choice(available)
        self.colonel = random.choice(available)
        self.exit = random.choice(available)

    def __str__(self, hidden=True):
        """Return a text representation of the grid."""
        grid = []
        for x in range(1, self.n + 1):
            row = []
            for y in range(1, self.n + 1):
                pos = (x, y)
                elements = []
                if pos == self.captain:
                    elements.append('CW')
                if pos in self.visited and pos != self.captain:
                    elements.append('✓')
                if not hidden:
                    for trap in TRAP_TYPES:
                        if self.traps[trap] == pos:
                            elements.append(trap)
                    if pos == self.soldier:
                        elements.append('M')
                    if pos == self.exit:
                        elements.append('S')
                    if pos == self.colonel:
                        elements.append('CK')
                if not elements:
                    cell_print = '.'
                else:
                    cell_print = ','.join(elements)
                row.append(f'{cell_print:^6}')
            grid.append(' '.join(row))
        return '\n'.join(grid)

    def adjacent(self):
        """Return the captain's orthogonal neighbours."""
        x, y = self.captain
        adj = []
        for x_add, y_add in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x_new, y_new = (x + x_add, y + y_add)
            if 1 <= x_new <= self.n and 1 <= y_new <= self.n:
                adj.append((x_new, y_new))
        return adj

    def get_percepts(self):
        """Return [fire, spikes, darts, soldier, exit, four walls, scream] perceptions."""
        adj = self.adjacent()
        x, y = self.captain
        eF = int(self.traps['F'] in adj)
        eP = int(self.traps['P'] in adj)
        eD = int(self.traps['D'] in adj)
        eM = int(self.soldier is not None and self.soldier in adj)
        eS = int(self.exit in adj or self.exit == self.captain)
        wall_up = int(x == 1)
        wall_down = int(x == self.n)
        wall_left = int(y == 1)
        wall_right = int(y == self.n)
        scream = int(self.last_scream)
        return [eF, eP, eD, eM, eS, wall_up, wall_down, wall_left, wall_right, scream]

    def found_colonel(self):
        """Return whether the captain has rescued the colonel."""
        return self.with_colonel

    def apply_action(self, action):
        """Apply a movement, grenade or exit action.

        A wall blocks movement. Entering a hazard raises an exception. A grenade
        is consumed only when aimed inside the grid. Exit requires the colonel.
        """
        x, y = self.captain
        self.last_scream = False
        actions = {'moveU': (-1, 0), 'moveD': (1, 0), 'moveL': (0, -1), 'moveR': (0, 1)}
        if action in actions:
            x_add, y_add = actions[action]
            x_new, y_new = (x + x_add, y + y_add)
            if not (1 <= x_new <= self.n and 1 <= y_new <= self.n):
                return
            new_pos = (x_new, y_new)
            for trap in TRAP_TYPES:
                if new_pos == self.traps[trap]:
                    raise Exception(f'Death: entered a trap of type {TRAP_NAMES[trap]}')
            if self.soldier is not None and new_pos == self.soldier:
                raise Exception("Death: the captain entered the soldier's cell.")
            if new_pos == self.colonel:
                self.with_colonel = True
            self.captain = new_pos
            self.visited.add(new_pos)
            return
        grenade_actions = {'grenadeU', 'grenadeD', 'grenadeL', 'grenadeR'}
        if action in grenade_actions:
            if not self.grenade:
                return
            direction_map = {'grenadeU': (-1, 0), 'grenadeD': (1, 0), 'grenadeL': (0, -1), 'grenadeR': (0, 1)}
            x_add, y_add = direction_map[action]
            x, y = self.captain
            target = (x + x_add, y + y_add)
            target_x, target_y = target
            if not (1 <= target_x <= self.n and 1 <= target_y <= self.n):
                return
            self.grenade = False
            if target == self.soldier:
                self.soldier = None
                self.last_scream = True
            return
        if action == 'exit':
            if self.captain == self.exit and self.with_colonel:
                return 'EXITED'
            return
        return
