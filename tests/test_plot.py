"""Verify plotted values and regression cases, using no live data."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from tennis_career.plot import plot_career_matches


@pytest.fixture
def matches():
    return pd.DataFrame({"player_age": [20., 21.], "age_difference": [-3., 2.],
                         "result": ["W", "L"], "player_name": ["Example"] * 2})


def test_axes_points_and_legend(matches):
    ax = plot_career_matches(matches)
    assert ax.collections[0].get_offsets().tolist() == [[20., -3.]]
    assert ax.collections[1].get_offsets().tolist() == [[21., 2.]]
    assert [text.get_text() for text in ax.legend_.texts] == ["Win", "Loss"]
    assert ax.get_xlabel() == "Player age (years)"
    assert ax.get_ylabel() == "Player age − opponent age (years)"
    assert ax.get_title() == "Example: career matches"
    plt.close(ax.figure)


@pytest.mark.parametrize("dtype", ["float64", "Float64"])
def test_missing_values_for_numpy_and_pandas_types(matches, dtype):
    matches["player_age"] = pd.Series([20, float("nan")], dtype=dtype)
    original = matches.copy(deep=True)
    with pytest.warns(UserWarning, match="omitted"):
        ax = plot_career_matches(matches)
    assert sum(len(c.get_offsets()) for c in ax.collections) == 1
    pd.testing.assert_frame_equal(matches, original)
    plt.close(ax.figure)


@pytest.mark.parametrize("value", ["unknown", "inf", "-inf"])
def test_invalid_numeric_values_are_not_plotted(matches, value):
    matches["player_age"] = [value, "21"]
    with pytest.warns(UserWarning, match="omitted"):
        ax = plot_career_matches(matches)
    assert ax.collections[1].get_offsets().tolist() == [[21., 2.]]
    assert len(ax.collections[0].get_offsets()) == 0
    plt.close(ax.figure)


def test_invalid_input_and_empty_data(matches):
    with pytest.raises(ValueError, match="Expected"):
        plot_career_matches(pd.DataFrame())
    with pytest.raises(ValueError, match="No matches"):
        plot_career_matches(matches.iloc[:0])
    matches.loc[0, "result"] = "unknown"
    with pytest.raises(ValueError, match="W or L"):
        plot_career_matches(matches)
