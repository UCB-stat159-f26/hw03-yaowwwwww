# Tennis career matches

STAT 159, Fall 2026, HW3 — James Wang

A small Python package that retrieves singles matches from Tennis Abstract and
plots player age against **player age minus opponent age**, colored by win/loss.

## Install and use

Requires Python 3.10 or newer and access to this course repository.

```bash
python -m pip install git+https://github.com/UCB-stat159-f26/hw03-yaowwwwww.git
```

```python
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
from tennis_career import get_career_matches, plot_career_matches

matches = get_career_matches("Serena Williams")
ax = plot_career_matches(matches)
output = Path("outputs")
output.mkdir(exist_ok=True)
ax.figure.savefig(output / f"{date.today()}_serena_williams.png", dpi=160)
plt.show()
```

`get_career_matches()` returns a pandas DataFrame sorted by source match date.
It accepts `"serena williams"`, `"Serena Williams"`, or `"SerenaWilliams"`;
other full names such as `"Rafael Nadal"` work too. It raises `ValueError` for
unknown names such as `"GastonSanchez"` and `RuntimeError` for download failures.

`plot_career_matches()` returns a matplotlib Axes and does not access the web.
Positive y-values mean the player is older than the opponent. Wins are blue;
losses are red. Annotations from the NYT graphic are omitted, as HW3 allows.

## Data and limitations

Data comes from [Tennis Abstract](https://www.tennisabstract.com/). Retrieval
combines the career archive with the current profile: WTA profile JavaScript
or the ATP classic page. Overlapping date/tournament/round/opponent records
keep the profile version. The parser reads JSON arrays without executing JS.

| Columns | Meaning and type |
| --- | --- |
| `match_date` | Source date, pandas datetime; sometimes a tournament start date |
| `tournament`, `surface`, `round` | Event information, strings |
| `opponent`, `player_name` | Names, strings |
| `result` | `W` or `L`, from the player's perspective |
| `player_age`, `opponent_age` | Age in years, numeric |
| `age_difference` | Player age minus opponent age, numeric |

Birth dates are converted using days / 365.25. Decimal opponent ages already
provided by the source are retained. Invalid or missing opponent ages become
`NaN`: retrieval warns and keeps those rows; plotting warns and omits them.
Invalid dates/results and matches before the player's birth date raise errors.

The DataFrame's `attrs` records `source_urls` and a UTC `retrieved_at` timestamp.
These attributes are not preserved by CSV export. Source coverage and dates
can change, and ages are approximate. This is the career data available from
the site, not an independently verified record of every match.

## Structure and checks

- `tennis_career/data.py`: download, parse and clean.
- `tennis_career/plot.py`: validate and plot.
- `tennis_career/__init__.py`: expose the two public functions.
- `tests/`: offline tests and the two small JS fixtures from the
  [HW3 instructions](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html).
- `pyproject.toml`: installation metadata and dependencies.
- `ai_documentation.txt`: brief assistance record.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

All 36 tests run without live servers; the test setup blocks network access.
They check both age formats, overlap, malformed data, missing values, HTTP
failures through mocks, name variants and actual plotted coordinates.
A separate manual check on November 13, 2026 retrieved and plotted Serena
Williams, Rafael Nadal, Roger Federer and Naomi Osaka. All package functions
are at most 20 nonblank lines, even counting their docstrings.

## Course connections and reflections

Makefiles are still the part I need most practice with, especially deciding
what belongs in a target's prerequisites. The
[Make lecture](https://stat159.berkeley.edu/fall-2026/lectures/14-make1/14-make-intro-slides.html)
connects an output to the files needed to rebuild it. In this assignment,
`pyproject.toml` declares the libraries needed to install the package. These
are different kinds of dependencies. HW3 does not require a Makefile, so I
want to understand that distinction before adding more automation.

The first two weeks' [file naming](https://stat159.berkeley.edu/fall-2026/lectures/02-files/02-files-slides.html)
and [project organization](https://stat159.berkeley.edu/fall-2026/lectures/04-unix2/04-unix2-slides.html)
slides give me concrete habits to follow: descriptive names, dated outputs,
and separate code and data. The package keeps that structure small, following
the [Python package lecture](https://stat159.berkeley.edu/fall-2026/lectures/26-packages3/26-python-packages.pdf):
two modules, an `__init__.py`, installation metadata and tests.

The [clear-code lecture](https://stat159.berkeley.edu/fall-2026/lectures/23-code/23-clear-code-slides.html)
is useful here because a plot can look plausible even when cleaning is wrong.
This rebuild caught missing pandas values passing a plotting filter and dates
before a player's birth being accepted. Small functions and tests with known
ages make those cases easier to inspect. The
[data lecture](https://stat159.berkeley.edu/fall-2026/lectures/21-data/21-data-slides.html)
also explains why the same source field needs documentation: it can hold a
birth date or a decimal age. I still need practice tracing those transformations
and understanding the tests, rather than judging the result only by the plot.
