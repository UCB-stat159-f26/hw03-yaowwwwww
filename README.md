# HW3

STAT 159 — James Wang

This package gets career matches from [Tennis Abstract](https://www.tennisabstract.com/)
and plots player age against the age gap to the opponent, with wins and losses
in different colors.

## Run

From this repository's folder:

```bash
python -m pip install '.[test]'
python -m pytest -q
```

Tests use the small samples from [HW3](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html)
and mocked requests. They do not access the website.

To make a plot, run this in Python:

```python
import matplotlib.pyplot as plt
from tennis_career import get_career_matches, plot_career_matches

data = get_career_matches("Serena Williams")
plot_career_matches(data)
plt.show()
```

## Reflection

The same column needs different treatment in the two sample files: one has
opponent birth dates and the other already has ages. This is a useful reminder
for me to check the data before trusting a plot. Small functions, as discussed
in the [clear-code lecture](https://stat159.berkeley.edu/fall-2026/lectures/23-code/23-clear-code-slides.html),
make each step easier to follow. I want more practice checking one match by hand
and comparing it with the test result.

AI use is recorded in [ai_documentation.txt](ai_documentation.txt).

## License

Package code is available under the [MIT License](LICENSE). Course materials
and Tennis Abstract data retain their original terms.
