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
Islands are first drawn by rejection with the original limit of 100 draws, so seeds
that already gave a layout still give the same one. When that limit is reached, which
always happens above 100 islands, the missing islands are drawn without replacement
from the free interior cells; before this, such rivers failed for every seed.
The saved finite simulations include actual transition counts and outcomes;
successful samples are not guarantees for every trajectory.

## Earlier corrections

This version includes post-submission fixes to transition-limit success/counting,
exit columns and the iteration cap. Seeded placement and simulation are controlled
separately; historical layouts and averages need not match older versions.

## Corrections of 27 October 2026

Palace sizes that cannot hold every element are rejected with `ValueError`; beliefs
palaces of two by two are rejected for every seed, although some seeds could build
one. Valid sizes consume the same random numbers as before: the seed-42 layouts are
unchanged. River island placement now succeeds for every count within the interior
capacity (see above).
