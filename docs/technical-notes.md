# Inference and planning notes

The [README](../README.md) introduces the three examples and their outputs.

## Palace agents

The safe-cell rule intersects the no-cliff and no-soldier sets. Clause propagation
is not a complete SAT solver; the fallback movement heuristic can take fatal
risks. The default palace is six by six. Sizes below three by three raise
`ValueError`.

Beliefs are separate marginals filtered by binary masks. Uniform priors remain
uniform over compatible positions. Summed trap and soldier scores can exceed one
and are not joint hazard probabilities. Traps and some other objects may overlap.
Sampling candidates are sorted before seeded placement, so the seed refers to
this implementation's placement order.

For manual play:

```bash
python -m logic_search.main --seed 42 --mode manual
python -m beliefs.main --seed 42
```

Use `moveU/D/L/R` to move and `grenadeU/D/L/R` to throw a grenade. Commands ignore
case. `exit` works at the exit after the rescue; Ctrl+C stops a session.
`--show-map` reveals the hidden layout for debugging. The belief demo's candidate
moves do not amount to an automatic rescue policy.

## River model

The default river contains 35 states. Rewards are +100 for entering the exit,
−100 for entering an island and −1 for other transitions. Terminal values remain
zero. Bellman updates are synchronous, with fixed action order and greedy
tie-breaking. The default settings are `gamma=1`, tolerance 0.01 and at most
1,000 updates. Layout and simulation seeds are independent.

Observed stopping and a small Bellman residual on a particular layout do not
establish convergence or an error bound for arbitrary undiscounted environments.
Saved simulations record actual transition counts and outcomes; successful
samples are not guarantees for every trajectory.

Island placement first uses rejection sampling, with a limit of 100 draws.
If islands are still missing, it samples without replacement from free interior
cells. Requested counts must fit within the river's interior capacity.

## Saved results and visualisation

`results/` contains four river layouts, the logical seed-42 example and the
belief demo. Each stored river result uses simulation seed 2026, 20 episodes and
a limit of 100 transitions per episode.

| Layout seed | Bellman iterations | Exits | Mean transitions | Mean reward |
|---|---:|---:|---:|---:|
| 5121111 | 91 | 20/20 | 16.05 | 84.95 |
| 1500 | 73 | 20/20 | 17.80 | 83.20 |
| 37 | 67 | 20/20 | 14.30 | 86.70 |
| 51211 | 27 | 20/20 | 6.40 | 94.60 |

The figure displays layout 37. To redraw it from the stored policy:

```bash
python -m pip install -r requirements-visualisation.txt
python preview.py
```

This replaces `docs/images/river-policy.png` without rerunning value iteration.
