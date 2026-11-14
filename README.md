# Tennis career matches

STAT 159, Fall 2026, HW3 — James Wang

A Python package for retrieving Tennis Abstract matches and plotting player
age against player age minus opponent age, colored by win/loss.

## Install and use

Requires Python 3.10+ and access to this course repository.

```bash
python -m pip install git+https://github.com/UCB-stat159-f26/hw03-yaowwwwww.git
```

```python
from datetime import date
from pathlib import Path
from tennis_career import get_career_matches, plot_career_matches

matches = get_career_matches("Serena Williams")
ax = plot_career_matches(matches)
output = Path("outputs")
output.mkdir(exist_ok=True)
ax.figure.savefig(output / f"{date.today()}_serena_williams.png", dpi=160)
```

- `get_career_matches(name)` returns a pandas DataFrame. Names such as
  `"serena williams"`, `"SerenaWilliams"` and `"Rafael Nadal"` work.
  Unknown names raise `ValueError`; download failures raise `RuntimeError`.
- `plot_career_matches(matches)` returns a matplotlib Axes. Wins are blue and
  losses are red. Positive y-values mean the player is older than the opponent.

## Data

Data comes from [Tennis Abstract](https://www.tennisabstract.com/). The package
combines career and profile records, removes overlap and sorts by date.
The table includes match date, event details, player/opponent names, result,
both ages and `age_difference` (player age minus opponent age).
Birth dates are converted to years using days / 365.25; decimal ages are kept.
Missing opponent ages produce a warning and are omitted from the plot.
Source dates may be tournament start dates, so calculated ages are approximate.
Source URLs and retrieval time are stored in `matches.attrs`.

## Tests and files

From a clone of this repository:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

The 36 tests use local examples and mocked requests; network access is blocked.
The male/female fixtures come from the [HW3 instructions](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html).

`tennis_career/data.py` handles retrieval and cleaning; `plot.py` handles plotting.
`pyproject.toml` defines installation dependencies. AI assistance is described
in [ai_documentation.txt](ai_documentation.txt).

## Reflection

One point I want to remember is that the same field can mean different things.
The female-player examples contain opponent birth dates, while the male-player
examples already contain ages. Treating both as ages would give a misleading
plot. This connects to the [clear-code lecture](https://stat159.berkeley.edu/fall-2026/lectures/23-code/23-clear-code-slides.html):
small functions and explicit handling of missing values make the steps easier
to inspect. The small test examples also make the calculations easier to check.
I still want to practice tracing a row from the raw data to the plotted point.
