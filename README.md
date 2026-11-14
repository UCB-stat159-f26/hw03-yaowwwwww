# HW3

STAT 159 — James Wang

This package gets career matches from [Tennis Abstract](https://www.tennisabstract.com/)
and plots player age against the age gap to the opponent, with wins and losses
in different colors.

## Run

Open a terminal in this repository's folder. On macOS or Linux, run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install '.[test]'
python -m pytest -q
```

`.[test]` installs this package and its test tools. The `.venv` folder stays
on your computer and is ignored by Git.

Tests use the small samples from [HW3](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html)
and mocked requests. They do not access the website.

Start Python in the same terminal:

```bash
python
```

Then run:

```python
import matplotlib.pyplot as plt
from tennis_career import get_career_matches, plot_career_matches

data = get_career_matches("Serena Williams")
print(data.head())
plot_career_matches(data)
plt.show()
```

Change the name to try another player, such as `"Rafael Nadal"`.
Downloading data needs internet access. Type `exit()` to leave Python.
Next time, activate the environment with `source .venv/bin/activate`.

## Reflection

Creating a library and building a wheel make code easier for many people to
reuse, so I need to take responsibility for how it works. This connects to the
[Python package lecture](https://stat159.berkeley.edu/fall-2026/lectures/26-packages3/26-python-packages.pdf).
I need to declare the dependencies and check installation in a fresh virtual
environment, instead of assuming the package will run on another computer.
The environment itself stays local; others recreate it from the instructions.

I also learned that offline tests help separate code errors from temporary
network problems. Player names need cleaning too: lowercasing handles case
differences, and a regular expression splits names like `SerenaWilliams`
before searching. The sample files also use different age formats, so I need
to check what the data means before trusting the plot.

AI use is recorded in [ai_documentation.txt](ai_documentation.txt).

## License

Package code is available under the [MIT License](LICENSE). Course materials
and Tennis Abstract data retain their original terms.
