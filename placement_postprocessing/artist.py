# A class that draws nice pictures given placement data.

from .keys import *  # Sorry
from .data import Data

import matplotlib as mpl
import matplotlib.pyplot as plt

def node_loading_histogram(data: Data, node: str="mailbox",
                           figArgs: dict={}, plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """
    Draws a node loading histogram - either for cores or for
    mailboxes. Arguments:

    - data: A placement_processing Data object with loaded data.
    - node: String, either "mailbox" or "core"
    - figArgs: Keyword arguments to be passed to the figure constructor
          (subplots).
    - plotArgs: Plotting arguments to be passed to the histogram plot (hist).

    Returns a matplotlib figure object that you can view/save/modify as you
    like.
    """

    loadings = data.frames[keyNodeLoadingCore if node == "core" else
                           keyNodeLoadingMbox]["load"]

    # Process figure arguments (adding our defaults). We modify inplace because
    # we're monsters.
    defaultFigArgs = {"figsize": (4, 3)}
    for item in defaultFigArgs.items():
        if item[0] not in figArgs.keys():
            figArgs[item[0]] = item[1]

    # Process plot arguments (adding our defaults), as before.
    defaultPlotArgs = {"bins": 6,
                       "color": "r",
                       "edgecolor": "#550000"}
    for item in defaultPlotArgs.items():
        if item[0] not in plotArgs.keys():
            plotArgs[item[0]] = item[1]

    # Actually do some work
    figure, axes = plt.subplots(**figArgs)
    axes.hist(loadings, **plotArgs)

    # This weird approach suppresses a UserWarning raised when limits are set
    # to the same value.
    axes.set_xlim(min(loadings), max(loadings +
                  (0 if min(loadings) != max(loadings) else 1e-2)))

    # The formatting continues...
    axes.set_ylim(0, len(loadings))
    axes.xaxis.get_major_locator().set_params(integer=True)
    axes.yaxis.get_major_locator().set_params(integer=True)
    axes.set_xlabel("Number of application nodes placed on " +
                    ("cores" if node == "core" else "mailboxes"))
    axes.set_ylabel("Occurences (total={})".format(len(loadings)))
    axes.set_title("{} Loading"
                   .format("Core" if node == "core" else "Mailbox"))
    axes.spines["right"].set_visible(False)
    axes.spines["top"].set_visible(False)
    axes.yaxis.set_ticks_position("left")
    axes.xaxis.set_ticks_position("bottom")
    figure.tight_layout()

    return figure


# Aliases
def mailbox_loading_histogram(data: Data, figArgs: dict={},
                              plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for node_loading_histogram."""
    return node_loading_histogram(data, "mailbox", figArgs, plotArgs)


def core_loading_histogram(data: Data, figArgs: dict={},
                           plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for node_loading_histogram."""
    return node_loading_histogram(data, "core", figArgs, plotArgs)
