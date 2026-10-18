# Inference and planning conventions

The [README](../README.md) contains the entry points, controls and saved outcomes.

## Palace tasks

The safe-cell rule intersects the no-cliff and no-soldier sets. Clause propagation
is not a complete SAT solver, and the fallback movement heuristic can take fatal
risks. Small constructed maps and scripted input exercise particular behaviours;
they do not establish success across all maps or interactive sessions.

Beliefs are separate marginals filtered by binary masks. Uniform priors remain
uniform over compatible positions. Summed trap/soldier scores can exceed one
and are not joint hazard probabilities. Traps and some other objects may overlap.
Sorted sampling candidates make seeded placement reproducible, but can change
layouts relative to historical runs with the same seed.

## River model

Bellman updates are synchronous, with fixed action order and greedy tie-breaking.
Rewards are paid on entering a terminal state; terminal values stay zero.
Defaults are `gamma=1`, tolerance 0.01 and at most 1,000 updates. Observed stopping
and the checked default residual do not prove convergence or an error bound for
arbitrary undiscounted environments. Layout and simulation seeds are independent.
The saved finite simulations include actual transition counts and outcomes;
successful samples are not guarantees for every trajectory.
