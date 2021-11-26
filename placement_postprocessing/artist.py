# A class that draws nice pictures given placement data.

from .keys import *  # Sorry
from .data import Data

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def _common_formatting(figure: mpl.figure.Figure) -> mpl.figure.Figure:
    """
    Take a figure and apply sensible formatting to to it.
    """
    axes = figure.gca()
    try:
        axes.xaxis.get_major_locator().set_params(integer=True)
    except TypeError:
        pass
    axes.yaxis.get_major_locator().set_params(integer=True)
    axes.spines["right"].set_visible(False)
    axes.spines["top"].set_visible(False)
    axes.yaxis.set_ticks_position("left")
    axes.xaxis.set_ticks_position("bottom")
    figure.tight_layout()
    return figure


def _histogram(data: Data, what: str="mailbox", figArgs: dict={},
               plotArgs: dict={}) -> mpl.figure.Figure:
    """
    Draws a histogram - either for cores (node), for mailboxes (node), for
    edges connecting mailboxes (hwedge), or for the cost associated with each
    application edge (appedge). Arguments:

    - data: A placement_processing Data object with loaded data.
    - what: String, either "mailbox", "core", "hwedge", or "appedge".
    - figArgs: Keyword arguments to be passed to the figure constructor
          (subplots).
    - plotArgs: Plotting arguments to be passed to the histogram plot (hist).

    Returns a matplotlib figure object that you can view/save/modify as you
    like.
    """

    if what == "core":
        loadings = data.frames[keyNodeLoadingCore]["load"]
    elif what == "mailbox":
        loadings = data.frames[keyNodeLoadingMbox]["load"]
    elif what == "hwedge":
        loadings = data.frames[keyHwEdgeLoading]["load"]
    elif what == "appedge":
        loadings = data.frames[keyAppEdgeCosts]["cost"]
    else:  # Sanity
        raise RuntimeError("Argument 'what' must be either 'mailbox', 'core', "
                           "'hwedge', or 'appedge'.")

    # Process figure arguments (adding our defaults). We modify inplace because
    # we're monsters.
    defaultFigArgs = {"figsize": (4, 3)}
    for item in defaultFigArgs.items():
        if item[0] not in figArgs.keys():
            figArgs[item[0]] = item[1]

    # Process plot arguments (adding our defaults), as before.
    defaultPlotArgs = {"bins": 6}
    if what == "hwedge":
        defaultPlotArgs["color"] = "b"
        defaultPlotArgs["edgecolor"] = "#000055"
    elif what == "appedge":
        defaultPlotArgs["color"] = "g"
        defaultPlotArgs["edgecolor"] = "#005500"
    else:
        defaultPlotArgs["color"] = "r"
        defaultPlotArgs["edgecolor"] = "#550000"
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

    # Line up ticks with bins, formatting them as integers if possible.
    desiredTicks = np.linspace(min(loadings), max(loadings),
                               plotArgs["bins"] + 1)
    if (desiredTicks == desiredTicks.astype(int)).all():
        axes.set_xticks(desiredTicks.astype(int))
    else:
        axes.set_xticks(desiredTicks)

    # The formatting continues...
    axes.set_ylim(0, len(loadings))
    axes.set_ylabel("Occurences (total={})".format(len(loadings)))
    if what == "core":
        axes.set_xlabel("Number of application nodes placed on cores")
        axes.set_title("Core Loading")
    elif what == "mailbox":
        axes.set_xlabel("Number of application nodes placed on mailboxes")
        axes.set_title("Mailbox Loading")
    elif what == "hwedge":
        axes.set_xlabel("Number of application edges overlaying\n "
                        "mailbox edges (in hardware)")
        axes.set_title("Mailbox Edge Loading")
    elif what == "appedge":
        axes.set_xlabel("Edge cost")
        axes.set_title("'Hardware cost' of application edges")
    return _common_formatting(figure)


# Alias
def application_edge_cost_histogram(data: Data, figArgs: dict={},
                                    plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for _histogram."""
    return _histogram(data, "appedge", figArgs, plotArgs)


# Alias
def core_loading_histogram(data: Data, figArgs: dict={},
                           plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for _histogram."""
    return _histogram(data, "core", figArgs, plotArgs)


# Alias
def mailbox_edge_loading_histogram(data: Data, figArgs: dict={},
                                   plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for _histogram."""
    return _histogram(data, "hwedge", figArgs, plotArgs)


# Alias
def mailbox_loading_histogram(data: Data, figArgs: dict={},
                              plotArgs: dict={}) \
    -> mpl.figure.Figure:
    """See documentation for _histogram."""
    return _histogram(data, "mailbox", figArgs, plotArgs)
