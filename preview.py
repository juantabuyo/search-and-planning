"""Draw the policy and state values stored for river layout 37."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def main():
    root = Path(__file__).parent
    result = json.loads((root / "results/river_37.json").read_text(encoding="utf-8"))
    values = np.array(result["values"])
    rows, columns = values.shape
    islands = {tuple(position) for position in result["islands"]}
    start = tuple(result["initial_state"])
    moves = {"up": (0, -0.28), "down": (0, 0.28),
             "left": (-0.28, 0), "right": (0.28, 0), "stay": (0, 0)}
    shown = np.ma.array(values, mask=np.zeros(values.shape, dtype=bool))
    shown.mask[:, -1] = True
    for row, column in islands:
        shown.mask[row, column] = True
    figure, axis = plt.subplots(figsize=(8.5, 9), layout="constrained")
    image = axis.imshow(shown, cmap="YlGnBu", vmin=float(shown.min()), vmax=float(shown.max()))
    for row in range(rows):
        for column in range(columns):
            if (row, column) in islands or column == columns - 1:
                is_exit = column == columns - 1
                axis.add_patch(Rectangle((column - 0.5, row - 0.5), 1, 1,
                                         facecolor="#e1efe5" if is_exit else "#d9dde2",
                                         edgecolor="white"))
                axis.text(column, row, "Exit" if is_exit else "Island",
                          ha="center", va="center", fontsize=11, color="#25394b")
                continue
            colour = "white" if values[row, column] > 60 else "#162736"
            dx, dy = moves[result["policy"][row][column]]
            if dx or dy:
                axis.annotate("", xy=(column + dx, row + dy - 0.10),
                              xytext=(column - dx / 2, row - dy / 2 - 0.10),
                              arrowprops={"arrowstyle": "-|>", "color": colour, "lw": 2})
            else:
                axis.plot(column, row - 0.10, "o", color=colour)
            axis.text(column, row + 0.29, f"{values[row, column]:.1f}",
                      ha="center", va="center", fontsize=10, color=colour)
            if (row, column) == start:
                axis.add_patch(Rectangle((column - 0.47, row - 0.47), 0.94, 0.94,
                                         fill=False, edgecolor="#e4a11e", linewidth=3))
                axis.text(column, row - 0.35, "Start", ha="center", fontsize=9, color=colour)
    axis.set_xticks(range(columns), labels=[
        f"{column}\npush {strength:.2f}"
        for column, strength in enumerate(result["current_by_column"])
    ])
    axis.set_yticks(range(rows))
    axis.set_xticks(np.arange(-0.5, columns), minor=True)
    axis.set_yticks(np.arange(-0.5, rows), minor=True)
    axis.grid(which="minor", color="white", linewidth=2)
    axis.tick_params(which="both", length=0)
    axis.set_xlabel("Column and probability of downward current")
    axis.set_ylabel("Row")
    axis.set_title(
        f"River policy · layout {result['layout_seed']}\n"
        f"Saved Bellman result after {result['iterations']} updates",
        fontsize=15, fontweight="bold", pad=18,
    )
    figure.colorbar(image, ax=axis, label="Saved state value", shrink=0.75)
    figure.supxlabel(
        "Arrows: selected actions · numbers: values · terminal values are zero; rewards are paid on entry",
        fontsize=9,
    )
    output = root / "docs/images/river-policy.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=140, facecolor="white", bbox_inches="tight")
    plt.close(figure)
    print(f"Saved {output.relative_to(root)} from results/river_37.json")


if __name__ == "__main__":
    main()

