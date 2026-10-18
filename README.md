# Search and planning in small gridworlds

My Artificial Intelligence coursework explores logical inference, approximate
beliefs and planning under uncertainty. In the palace task, an agent must rescue
Colonel Kurtz and reach an exit while avoiding hazards. In the river task, it must
reach the opposite bank despite a random downward current.

## Run

Python 3.12; tested with 3.12.14. From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m logic_search.main --seed 42 --quiet
python -m beliefs.main --seed 42 --demo
python -m river_mdp.main --seed 5121111 --simulation-seed 2026 --episodes 20 --json results/river_5121111.json
```

On Windows, activate with `.venv\Scripts\activate`. No external dataset, account
or service is required. These commands run the logical heuristic, show an initial
belief update and solve/simulate the river model. Existing JSON outputs are
replaced. For an interactive palace session:

```bash
python -m logic_search.main --seed 42 --mode manual
python -m beliefs.main --seed 42
```

Use `moveU/D/L/R` to move and `grenadeU/D/L/R` to throw a grenade. `exit` succeeds
only at the exit after the rescue. Commands ignore case; Ctrl+C stops the session.
The belief interface's `--show-map` option reveals the hidden map for debugging.

## Three approaches

- **Logical search:** clauses describe adjacent hazards, and BFS searches known
  safe cells. Without a safe route, a heuristic penalises revisits and possible
  hazards. It can fail and is not a complete SAT solver.
- **Marginal beliefs:** separate uniform maps are filtered by deterministic
  perceptions. They remain uniform over compatible positions. Summed risk scores
  can exceed one; they are not joint hazard probabilities. The user chooses
  actions, and `--demo` does not complete a mission.
- **River MDP:** synchronous Bellman updates choose among up, down, left, right
  and stay. Rewards are +100 for reaching the exit, −100 for entering an island
  and −1 otherwise, counted on transition. The default grid has 35 states.

## Saved results

Runs on 17 October 2026 used simulation seed 2026, 20 episodes per layout and a
limit of 100 transitions per episode. Layout and simulation seeds are separate.

| Layout seed | Bellman iterations | Exits | Mean transitions | Mean reward |
|---|---:|---:|---:|---:|
| 5121111 | 91 | 20/20 | 16.05 | 84.95 |
| 1500 | 73 | 20/20 | 17.80 | 83.20 |
| 37 | 67 | 20/20 | 14.30 | 86.70 |
| 51211 | 27 | 20/20 | 6.40 | 94.60 |

[Results](results/) include policies, values and individual outcomes. Twenty
successful simulations do not establish guaranteed success. With seed 42, the
logical heuristic failed after three actions; the belief demo only updated its
initial maps. Historical simulation averages are not reproduced by these runs.

The MDP uses `gamma=1`, tolerance 0.01 and a 1,000-update cap. Its observed stopping
condition is not a general convergence guarantee; the discounted contraction
argument does not apply.

## Tests and version notes

```bash
python -m unittest discover -s tests -v
```

Fourteen tests cover safe shortest paths, clause propagation, compatible belief
support, scores above one, grenade perceptions, scripted rescue, transition
limits/counts, normalised transitions across four layouts, another grid width
and Bellman/policy consistency. Scripted cases are not a complete interactive
study or a success-rate guarantee.

[Technical notes](docs/technical-notes.md) explain model conventions. This version
includes post-submission fixes to transition-limit success/counting, exit columns
and the iteration cap. Seeded placement and simulation are controlled separately;
historical layouts and averages need not match.

## Academic context and credit

An individual submission for *Foundations of Artificial Intelligence*, iMAT,
ICAI, Universidad Pontificia Comillas. The logical inference,
belief updates and Bellman iteration are implemented in the project; NumPy
supports the numerical calculations. Teaching materials are not included.
