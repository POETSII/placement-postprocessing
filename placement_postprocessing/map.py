# A class that draws maps using one of graphviz' rendering engines.

from .keys import *  # Still sorry, but not enough to learn from my ways.
from .data import Data

import graphviz as gv
import numpy as np
import os
import typing


def node_position_from_name(name: str) -> typing.Tuple[int, int]:
    """
    Given a node (mailbox) name, infer its positional co-ordinate in the
    map. Makes a lot of assumptions.

    We should really be parsing a hardware description file to do this, but
    life is short, and interfaces are plentiful.

    Expect nodes in the form:

      O_.<ENGINE_FILE_ROOT>.<ENGINE_FILE_EXTENSION>.<BOX>.<BOARD>.<MBOX>

    where:

      - <ENGINE_FILE_ROOT>, <BOX>, and <ENGINE_FILE_EXTENSION> all contain no
        whitespace or '.'s.

      - <BOARD> is of the form B<X><Y>, where <X> and <Y> are box-relative
        positional integer co-ordinates for the board. Here, <X> must be in
        [0,2] and <Y> must be in [0,1].

      - <MBOX> is of the form M<X><Y>, where <X> and <Y> are board-relative
        positional co-ordinates for the mailbox. Here, <X> and <Y> must both be
        in [0,3].

    Mailboxes are assumed to exist in a 4x4 grid, and boards are assumed to
    exist in a 2x3 grid.

    Returns the co-ordinate, with both components zero or positive, as a tuple
    if it can be understood. If not, returns (-1, -1) and prints a message.
    """

    out = (-1, -1)  # Error output.
    errMsg = ("Not sure how to decode name '{}'. Not positioning any nodes "
              "explicitly.".format(name))

    # Constants
    boardSpacing = 4
    boxSpacingX = 3
    boxSpacingY = 2

    # Verify node length input.
    splitName = name.split(".")
    if len(splitName) != 6:
        print(errMsg)
        return out

    # Grab components
    try:
        box, board, mbox = splitName[3:]
        mx = int(mbox[1])
        my = int(mbox[2])
        bx = int(board[1])
        by = int(board[2])
    except ValueError:
        print(errMsg)
        return out

    # See if we can determine base co-ordinates for the box, given its
    # name. If we can't, just don't try.
    boxPositions = {"LoneBox": (0, 0),
                    "Ay": (0, 0),
                    "By": (0, 0),
                    "Co": (1, 0),
                    "De": (0, 1),
                    "El": (1, 1),
                    "Fi": (0, 2),
                    "Go": (1, 2),
                    "He": (0, 3),
                    "Ib": (1, 3)}
    if box not in boxPositions.keys():
        print(errMsg)
        return out

    # gogogo!
    return (boxPositions[box][0] * boxSpacingX +
            bx * boardSpacing +
            mx,
            boxPositions[box][1] * boxSpacingY +
            by * boardSpacing +
            my)



def draw_map(data: Data, cleanup: bool=True, drawHwEdges: bool=False,
             maxNodeHLoad: float=np.inf,
             maxEdgeHLoad: float=np.inf, outPath: str="" ) -> None:
    """
    Draws a map showing device placement on a hardware graph using
    graphviz, where:

     - Hardware nodes (mailboxes) are colored more strongly the more
       heavily-loaded they are.
     - Edges in the application graph are drawn if they do not directly overlay
       with a single edge in the hardware model.
     - Edges in the hardware graph are thicker if they are more heavily loaded
       with application edges.

    Arguments:

     - data: A placement_processing Data object with loaded data.
     - cleanup: If False, leaves a source file describing the graph. Useful
           for debugging.
     - drawHwEdges: If True, draws hardware edges that are used in black.
     - maxNodeHLoad: If not default, forces a maximum node loading on the
           map. If infinite (default), impose no maximum.
     - maxEdgeHLoad: As above, but for edges.
     - outPath: Path (absolute or relative) to write the map
           to. Extension determines the type of file written.

    Returns nothing, but writes the graph to `outPath`.
    """

    # A little bit of sanity. We'll refer to these headers by name because
    # using the headers accessor makes for illegible code. Expected definitions
    # can (probably) be found in keys.py.
    assert headers[keyNodeLoading][0] == "node"
    assert headers[keyNodeLoading][1] == "load"
    assert headers[keyHwEdgeLoading][0] == "from"
    assert headers[keyHwEdgeLoading][1] == "to"
    assert headers[keyHwEdgeLoading][2] == "load"
    assert headers[keyAppToHw][0] == "appnode"
    assert headers[keyAppToHw][1] == "hwnode"

    # Compute positional data for mailboxes, if known a priori.
    explicitPositions = True
    positions = {}
    for _, record in data.frames[keyNodeLoadingMbox].iterrows():  # Sorry purists
        nodePos = node_position_from_name(record["node"])
        if (nodePos[0] == -1):
            explicitPositions = False
            break
        positions[record["node"]] = "{},{}!".format(*nodePos)

    # Derive colors from hardware node loading, respecting `maxNodeHLoad` if
    # it's set. We do this not by changing the colour, but by adding two
    # hexidecimal places of alpha information.
    maxNodeLoad = data.frames[keyNodeLoadingMbox]["load"].max() \
        if maxNodeHLoad == np.inf else maxNodeHLoad
    baseColour = "#4444ff"  # String addition incoming
    nodeLoading = {}
    for _, record in data.frames[keyNodeLoadingMbox].iterrows():  # Sorry purists
        nodeLoading[record["node"]] = \
            baseColour + hex(int(record["load"] / maxNodeLoad * 255))[2:]

    # Derive thicknesses for hardware node edges in the graph, respecting
    # `maxEdgeHLoad` if it's set.
    maxEdgeLoad = data.frames[keyHwEdgeLoading]["load"].max() \
        if maxEdgeHLoad == np.inf else maxEdgeHLoad
    maxThicc = 5  # Totally arbitrary
    edgeLoading = {}
    for _, record in data.frames[keyHwEdgeLoading].iterrows():
        load = record["load"]
        edgeLoading[(record["from"], record["to"])] = \
            load / maxEdgeLoad * maxThicc \
            if load / maxEdgeLoad < 1 else maxThicc

    # Compute application node edges. Do this by going through each application
    # edge, then making a connection between their hardware nodes.
    extraEdges = []
    hwEdgesDf = data.frames[keyHwEdgeLoading]  # Convenience
    for _, record in data.frames[keyAppEdgeCosts].iterrows():
        appEdge = tuple(record)
        hwFrom = ".".join(data.frames[keyAppToHw][data.frames[keyAppToHw]["appnode"] == appEdge[0]]["hwnode"].values[0].split(".")[:-2])
        hwTo = ".".join(data.frames[keyAppToHw][data.frames[keyAppToHw]["appnode"] == appEdge[1]]["hwnode"].values[0].split(".")[:-2])
        if hwFrom != hwTo:
            extraEdges.append([hwFrom, hwTo])

    # Draw graph...
    graph = gv.Graph("G", strict=True, engine="neato")
    graph.attr(margin="0")
    graph.attr("node", shape="square", style="filled", label="",
               fillcolor="#000000", margin="0")

    # Hardware nodes, with their loading colours.
    for node, colour in nodeLoading.items():
        if explicitPositions:
            graph.node(node, fillcolor=colour, pos=positions[node])
        else:
            graph.node(node, fillcolor=colour)

    # Hardware edges, with their loading thicknesses. Note these come before
    # application-hardware edges because the graph is strict (i.e. edges after
    # the first are ignored).
    if drawHwEdges:
        for edge, thickness in edgeLoading.items():
            graph.edge(*edge, color="#000000", penwidth=str(thickness))

    # Application-hardware edges.
    for edge in extraEdges:
        graph.edge(*edge, color="#ff0000")

    # All you wanna do is drag me down, all I wanna do is stamp you out.
    fileName, extension = os.path.splitext(os.path.basename(outPath))
    graph.render(filename=fileName, directory=os.path.dirname(outPath),
                 cleanup=cleanup, format=extension.split(".")[-1])
