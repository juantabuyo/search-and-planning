import numpy as np
from .config import MAX_RISK, START

class Bayesian:

    def __init__(self, n):
        """Initialise uniform approximate marginal maps."""
        self.n = n
        self.total = n * n
        self.prob_F = None
        self.prob_P = None
        self.prob_D = None
        self.prob_M = None
        self.prob_S = None
        self.visited = set()
        self.soldier_alive = True
        self.start_priors()

    def start_priors(self):
        """Give every non-start cell prior mass 1 / (n*n - 1) for each object."""
        prior = 1 / (self.total - 1)
        self.prob_F = np.full((self.n, self.n), prior)
        self.prob_P = np.full((self.n, self.n), prior)
        self.prob_D = np.full((self.n, self.n), prior)
        self.prob_M = np.full((self.n, self.n), prior)
        self.prob_S = np.full((self.n, self.n), prior)
        x, y = START
        self.prob_F[x - 1, y - 1] = 0
        self.prob_P[x - 1, y - 1] = 0
        self.prob_D[x - 1, y - 1] = 0
        self.prob_M[x - 1, y - 1] = 0
        self.prob_S[x - 1, y - 1] = 0
        self.normalise()

    def normalise(self):
        """Normalise each non-empty marginal map; a dead soldier remains all zero."""
        for probability_grid in [self.prob_F, self.prob_P, self.prob_D, self.prob_M, self.prob_S]:
            total_sum = probability_grid.sum()
            if total_sum > 0:
                probability_grid /= total_sum

    def get_neighbours(self, pos):
        """Return orthogonal neighbours and the current cell for perception masks."""
        x, y = pos
        adj = [pos]
        for x_add, y_add in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x_new, y_new = (x + x_add, y + y_add)
            if 1 <= x_new <= self.n and 1 <= y_new <= self.n:
                adj.append((x_new, y_new))
        return adj

    def update(self, pos, percepts):
        """Apply binary perception masks and renormalise the separate marginal maps.

        Survival rules out a trap or soldier in the current cell. The model does
        not represent the joint constraints between object locations.
        """
        x, y = pos
        eF, eP, eD, eM, eS = percepts[:5]
        self.visited.add(pos)
        n_x, n_y = (x - 1, y - 1)
        self.prob_F[n_x, n_y] = 0
        self.prob_P[n_x, n_y] = 0
        self.prob_D[n_x, n_y] = 0
        self.prob_M[n_x, n_y] = 0
        boxes = self.get_neighbours(pos)
        self.update_box(self.prob_F, eF, boxes)
        self.update_box(self.prob_P, eP, boxes)
        self.update_box(self.prob_D, eD, boxes)
        if self.soldier_alive:
            self.update_box(self.prob_M, eM, boxes)
        else:
            self.prob_M.fill(0)
        self.update_box(self.prob_S, eS, boxes)
        self.normalise()

    def update_box(self, probability_grid, percept, boxes):
        """Multiply a map by a binary compatibility mask.

        Starting with a uniform prior, repeated 0/1 masks leave a uniform map
        over the remaining compatible cells, not gradually weighted evidence.
        """
        likelihood = np.zeros((self.n, self.n))
        for box in boxes:
            x, y = box
            likelihood[x - 1, y - 1] = 1
        if percept:
            probability_grid *= likelihood
        else:
            probability_grid *= 1 - likelihood

    def soldier_dead(self):
        """Remove the soldier hazard after the grenade perception confirms its death."""
        self.soldier_alive = False
        self.prob_M.fill(0)

    def get_risk_score(self, pos):
        """Sum approximate trap and living-soldier marginal masses at a cell.

        This risk score can exceed one. Traps may overlap, and the separate maps
        do not model a joint distribution, so it is not P(any danger).
        """
        x, y = pos
        n_x, n_y = (x - 1, y - 1)
        trap_risk_score = self.prob_F[n_x, n_y] + self.prob_P[n_x, n_y] + self.prob_D[n_x, n_y]
        soldier_probability = self.prob_M[n_x, n_y] if self.soldier_alive else 0
        return trap_risk_score + soldier_probability

    def get_low_risk_neighbours(self, pos, max_risk=MAX_RISK):
        """Return unvisited neighbours whose risk score is at most max_risk.

        A score below the threshold is not a guarantee that a cell is safe.
        """
        neighbours = self.get_neighbours(pos)
        neighbours = [n for n in neighbours if n != pos]
        safe = []
        for neighbour in neighbours:
            if neighbour not in self.visited:
                danger = self.get_risk_score(neighbour)
                if danger <= max_risk:
                    safe.append(neighbour)
        return safe
