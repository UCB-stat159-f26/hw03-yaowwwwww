"""Plot a cleaned career table without making any network requests."""

import warnings

import matplotlib.pyplot as plt
import pandas as pd


def _prepare_plot(matches):
    """Treat NaN, pandas.NA, infinite and nonnumeric ages consistently."""
    columns = ["player_age", "age_difference"]
    required = set(columns + ["result"])
    if not isinstance(matches, pd.DataFrame) or not required.issubset(matches):
        raise ValueError("Expected player_age, age_difference and result columns.")
    if not matches["result"].isin(["W", "L"]).all():
        raise ValueError("Match results must be W or L.")
    numeric = matches[columns].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([float("inf"), -float("inf")], float("nan"))
    valid = numeric.notna().all(axis=1)
    if not valid.all():
        warnings.warn("Matches with missing or invalid ages are omitted.",
                      UserWarning, stacklevel=2)
    return matches.assign(**numeric).loc[valid]


def _format_axes(ax, player_name):
    """Label the sign of the difference explicitly."""
    ax.set_title(f"{player_name}: career matches")
    ax.set_xlabel("Player age (years)")
    ax.set_ylabel("Player age − opponent age (years)")
    ax.axhline(0, color="gray", linewidth=0.8, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)


def plot_career_matches(matches):
    """Return a matplotlib Axes; warn and omit matches with unknown ages."""
    data = _prepare_plot(matches)
    if data.empty:
        raise ValueError("No matches with valid ages to plot.")
    fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")
    fig.set_facecolor("#f7f5f0")
    ax.set_facecolor("#f7f5f0")
    for result, color, label in [("W", "#76b7c5", "Win"), ("L", "#c84648", "Loss")]:
        points = data.loc[data["result"] == result]
        ax.scatter(points["player_age"], points["age_difference"],
                   s=15, color=color, label=label, alpha=0.75)
    name = data["player_name"].iloc[0] if "player_name" in data else "Player"
    _format_axes(ax, name)
    fig.supxlabel("Source: Tennis Abstract · Ages use source match dates", fontsize=9)
    return ax
