from .functions import kb_neighbours

class KnowledgeBase:

    def __init__(self, n):
        """Initialise the logical facts and disjunctions."""
        self.n = n
        self.soldier_alive = True
        self.visited = set()
        self.no_cliff = set()
        self.no_soldier = set()
        self.no_exit = set()
        self.cliff_clauses = []
        self.soldier_clauses = []
        self.exit_clauses = []
        self.cliff_certain = set()
        self.soldier_certain = set()
        self.exit_certain = set()

    def all_pos(self):
        """Return all one-based grid positions."""
        return {(x, y) for x in range(1, self.n + 1) for y in range(1, self.n + 1)}

    def analyse_clauses(self, clauses):
        """Remove duplicate disjunctions without changing their meaning."""
        seen = set()
        out = []
        for clause in clauses:
            key = tuple(sorted(clause))
            if key not in seen:
                seen.add(key)
                out.append(clause)
        return out

    def reduce_clauses(self):
        """Remove cells ruled out by negative facts from each disjunction."""
        new_cliff = []
        for clause in self.cliff_clauses:
            clause_2 = {c for c in clause if c not in self.no_cliff}
            if clause_2:
                new_cliff.append(clause_2)
        self.cliff_clauses = self.analyse_clauses(new_cliff)
        if self.soldier_alive:
            new_soldier = []
            for clause in self.soldier_clauses:
                clause_2 = {c for c in clause if c not in self.no_soldier}
                if clause_2:
                    new_soldier.append(clause_2)
            self.soldier_clauses = self.analyse_clauses(new_soldier)
        else:
            self.soldier_clauses = []
            self.soldier_certain = set()
        new_exit = []
        for clause in self.exit_clauses:
            clause_2 = {c for c in clause if c not in self.no_exit}
            if clause_2:
                new_exit.append(clause_2)
        self.exit_clauses = self.analyse_clauses(new_exit)

    def inference(self):
        """Propagate singleton clauses and negative facts until no fact count changes.

        A singleton identifies its object. There is only one soldier, so identifying
        its cell rules out every other cell. This is limited rule propagation, not
        a complete propositional satisfiability solver.
        """
        changed = True
        while changed:
            changed = False
            before = (len(self.cliff_clauses), len(self.soldier_clauses), len(self.exit_clauses), len(self.cliff_certain), len(self.soldier_certain), len(self.exit_certain), len(self.no_cliff), len(self.no_soldier), len(self.no_exit))
            self.reduce_clauses()
            for clause in self.cliff_clauses:
                if len(clause) == 1:
                    cliff = next(iter(clause))
                    if cliff not in self.cliff_certain:
                        self.cliff_certain.add(cliff)
                        changed = True
            if self.soldier_alive:
                for clause in self.soldier_clauses:
                    if len(clause) == 1:
                        soldier = next(iter(clause))
                        if soldier not in self.soldier_certain:
                            self.soldier_certain.add(soldier)
                            changed = True
                if len(self.soldier_certain) == 1:
                    soldier = next(iter(self.soldier_certain))
                    all_pos = self.all_pos()
                    before_no_soldier = len(self.no_soldier)
                    self.no_soldier.update(all_pos - {soldier})
                    if len(self.no_soldier) != before_no_soldier:
                        changed = True
            for clause in self.exit_clauses:
                if len(clause) == 1:
                    exit_pos = next(iter(clause))
                    if exit_pos not in self.exit_certain:
                        self.exit_certain.add(exit_pos)
                        changed = True
            after = (len(self.cliff_clauses), len(self.soldier_clauses), len(self.exit_clauses), len(self.cliff_certain), len(self.soldier_certain), len(self.exit_certain), len(self.no_cliff), len(self.no_soldier), len(self.no_exit))
            if before == after:
                break

    def watch(self, pos, percepts):
        """Record perceptions at a surviving position, then propagate the clauses."""
        breeze, snoring, glow, _, _, _, _, scream = percepts
        adj = kb_neighbours(pos, self.n)
        self.visited.add(pos)
        self.no_cliff.add(pos)
        self.no_soldier.add(pos)
        if breeze == 0:
            self.no_cliff.update(adj)
        else:
            self.cliff_clauses.append(set(adj))
        if scream == 1:
            self.soldier_alive = False
            self.soldier_certain = set()
            self.soldier_clauses = []
            self.no_soldier.update(self.all_pos())
        elif not self.soldier_alive or snoring == 0:
            self.no_soldier.update(adj)
        else:
            self.soldier_clauses.append(set(adj))
        if glow == 0:
            self.no_exit.add(pos)
            self.no_exit.update(adj)
        else:
            self.exit_clauses.append(set([pos] + adj))
        self.inference()

    def safe_positions(self):
        """Intersect cells known to contain no cliff with cells containing no soldier."""
        return self.no_cliff & self.no_soldier

    def possible_cliffs(self):
        """Return unresolved cliff candidates appearing in the clauses."""
        possible = set()
        for clause in self.cliff_clauses:
            possible.update(clause)
        possible -= self.no_cliff
        possible -= self.cliff_certain
        return possible

    def possible_soldier(self):
        """Return unresolved soldier candidates, or an empty set after its death."""
        if not self.soldier_alive:
            return set()
        possible = set()
        for clause in self.soldier_clauses:
            possible.update(clause)
        possible -= self.no_soldier
        possible -= self.soldier_certain
        return possible

    def possible_exit(self):
        """Return unresolved exit candidates appearing in the clauses."""
        possible = set()
        for clause in self.exit_clauses:
            possible.update(clause)
        possible -= self.no_exit
        possible -= self.exit_certain
        return possible

    def safe_neighbours(self, pos):
        """Return adjacent cells that the knowledge base can certify as safe."""
        safe = self.safe_positions()
        return [x for x in kb_neighbours(pos, self.n) if x in safe]
