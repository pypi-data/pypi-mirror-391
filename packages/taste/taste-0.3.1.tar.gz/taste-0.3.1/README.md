# Taste: Creating plots fast

[![GitHub version](https://badge.fury.io/gh/keyweeusr%2Ftaste.svg)
](https://badge.fury.io/gh/keyweeusr%2Ftaste)
[![PyPI version](https://img.shields.io/pypi/v/taste.svg)
](https://pypi.org/project/taste/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/taste.svg)
](https://pypi.org/project/taste/)
[![Latest release deps](https://img.shields.io/librariesio/release/pypi/taste.svg)
](https://libraries.io/pypi/taste)
[![GitHub repo deps](https://img.shields.io/librariesio/github/keyweeusr/taste.svg)
](https://libraries.io/pypi/taste)

[![Downloads total](https://pepy.tech/badge/taste)
](https://pepy.tech/project/taste)
[![Downloads month](https://pepy.tech/badge/taste/month)
](https://pepy.tech/project/taste)
[![Downloads week](https://pepy.tech/badge/taste/week)
](https://pepy.tech/project/taste)
[![All Releases](https://img.shields.io/github/downloads/keyweeusr/taste/total.svg)
](https://github.com/KeyWeeUsr/taste/releases)
[![Code bytes](https://img.shields.io/github/languages/code-size/keyweeusr/taste.svg)
](https://github.com/KeyWeeUsr/taste)
[![Repo size](https://img.shields.io/github/repo-size/keyweeusr/taste.svg)
](https://github.com/KeyWeeUsr/taste)

Taste is a [Python][python] package wrapping [Matplotlib][mpl] APIs into a set
of common most used plots across multiple various applications or reporting
tools via clean and intuitive classes adhering to [The Zen of Python][zen].

It tries to completely isolate itself from the global [Matplotlib][mpl] context
which can be hard to understand for a complete newbie and can cause too much
unnecessary struggle.

It is easy and intuitive to use:

```python
from taste.plots import HorizontalBarPlot

# create a plot with desired properties
plot = HorizontalBarPlot(
    caption="Plot caption",
    title="Figure title",
    bars=[0, 1, 2, 3, 4],
    values=[9, 9, 5, 8, 2],
    bar_label="Here I can label the bars",
    value_label="And here I label the values",
    bar_axis_labels=["Tom", "Dick", "Harry", "Slim", "Jim"],
    value_axis_labels=["L0", "L1", "L2", "L3", "L4"]
)

# explicitly ask to draw the plot in Jupyter notebook
plot.figure  # MPL figure object
```

![](./doc/source/_static/example-index.png)

> [!NOTE]
> Although it doesn't explicitly forbid Python 3.6 due to compatibility with
> some older [Jupyter][jpy] notebooks, it aspires to run on higher versions
> (3.7+). Updating is *highly* recommended.

## Quick Installation

Taste is available on [PyPI][pypi], simply issue this command in your terminal
and you're good to go:

```
pip install taste
```

For more descriptive steps in various environments check
[Installation][install].

[python]: https://python.org
[mpl]: https://matplotlib.org
[zen]: https://www.python.org/dev/peps/pep-0020/#the-zen-of-python
[pypi]: https://pypi.org/project/taste
[install]: https://taste.readthedocs.io/en/latest/install.html
[jpy]: https://jupyter.org
