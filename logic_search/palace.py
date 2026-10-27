from .functions import random_position
from .config import N_GRIDS, N_CLIFFS, N_SOLDIERS, N_COLONELS, START

class Palace:

    def __init__(self, n=N_GRIDS) -> None:
        """Create a randomly generated palace with the original placement rules."""
        required = 1 + N_CLIFFS + N_SOLDIERS + N_COLONELS + 1   # start, hazards and the exit
        if n * n < required:
            raise ValueError(f'A {n}x{n} palace has {n * n} cells; {required} are needed to place all elements.')
        self.n = n
        self.captain = START
        self.cliffs = set()
        self.soldiers = set()
        self.colonels = set()
        self.exit = None
        self.with_colonel = False
        self.grenade = True
        self.last_scream = False
        occupied = {self.captain}
        while len(self.cliffs) < N_CLIFFS:
            pos = random_position(self.n)
            if pos not in occupied:
                self.cliffs.add(pos)
                occupied.add(pos)
        while len(self.soldiers) < N_SOLDIERS:
            pos = random_position(self.n)
            if pos not in occupied:
                self.soldiers.add(pos)
                occupied.add(pos)
        while len(self.colonels) < N_COLONELS:
            pos = random_position(self.n)
            if pos not in occupied:
                self.colonels.add(pos)
                occupied.add(pos)
        while self.exit is None:
            pos = random_position(self.n)
            if pos not in occupied:
                self.exit = pos
                occupied.add(pos)

    def __str__(self):
        """Return a text representation of the grid."""
        grid = []
        for x in range(1, self.n + 1):
            row = []
            for y in range(1, self.n + 1):
                pos = (x, y)
                box = '.'
                if pos == self.exit:
                    box = 'E'
                if pos in self.cliffs:
                    box = 'P'
                if pos in self.soldiers:
                    box = 'S'
                if pos in self.colonels:
                    box = 'CK'
                if pos == self.captain:
                    box = 'CW'
                row.append(f'{box:^2}')
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

    def breeze(self, adj=None):
        """Detect a cliff in an adjacent cell."""
        if adj is None:
            adj = self.adjacent()
        for a in adj:
            if a in self.cliffs:
                return True
        return False

    def snoring(self, adj=None):
        """Detect a soldier in an adjacent cell."""
        if adj is None:
            adj = self.adjacent()
        for a in adj:
            if a in self.soldiers:
                return True
        return False

    def glow(self, adj=None):
        """Detect the exit in the current or an adjacent cell."""
        if self.captain == self.exit:
            return True
        if adj is None:
            adj = self.adjacent()
        for a in adj:
            if a == self.exit:
                return True
        return False

    def found_colonel(self):
        """Return whether the captain has rescued the colonel."""
        return self.with_colonel

    def get_percepts(self):
        """Return [breeze, snoring, glow, four walls, scream]."""
        x, y = self.captain
        wall_up = x == 1
        wall_down = x == self.n
        wall_left = y == 1
        wall_right = y == self.n
        adj = self.adjacent()
        return [int(self.breeze(adj)), int(self.snoring(adj)), int(self.glow(adj)), int(wall_up), int(wall_down), int(wall_left), int(wall_right), int(self.last_scream)]

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
            if new_pos in self.cliffs:
                raise Exception('Death: the captain entered a cliff.')
            if new_pos in self.soldiers:
                raise Exception("Death: the captain entered the soldier's cell.")
            if new_pos in self.colonels:
                self.with_colonel = True
                self.colonels.remove(new_pos)
            self.captain = new_pos
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
            if target in self.soldiers:
                self.soldiers.remove(target)
                self.last_scream = True
            return
        if action == 'exit':
            if self.captain == self.exit and self.with_colonel:
                return 'EXITED'
            return
        return
