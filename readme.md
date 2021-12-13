What's This?
===

A Python (3.6+) library that, given placement dumps from the Orchestrator, can
be used to draw maps and histograms describing the placement. It uses
matplotlib and graphviz to do this.

Requirements
===

You'll need the following Python packages (and their dependencies).

 - Pandas (I use 1.3.4), for holding and manipulating data.
 - Matplotlib (I use 3.4.3), for drawing graphs.
 - graphviz (I use 0.18.2), for creating dotfiles for Graphviz to render into
   maps.

You will also need an installation of Graphviz itself, from your package
manager or from https://www.graphviz.org/, because the graphviz Python package
does not install a renderer for you. I use 2.49.3.

Library
===

Need a quick start? Check `example.py`.

This library (`placement_postprocessing`) takes a dump of placement data from
the POETS Orchestrator (https://github.com/poetsii/orchestrator), and produces
histograms and maps presenting that data. It's a simple tool that produces
simple pictures.

Load in your data:

```python
import placement_postprocessing as pp  # hohoho
data = pp.Data("example_data/")
```

where the following files are present (and are described by the Orchestrator's
placement documentation) in `"example_data/"`:

 - `placement_gi_edges_<APPNAME>_<TIMESTAMP>.csv`
 - `placement_gi_to_hardware_<APPNAME>_<TIMESTAMP>.csv`
 - `placement_diagnostics_<APPNAME>_<TIMESTAMP>.csv`
 - `placement_edge_loading_<TIMESTAMP>.csv`
 - `placement_hardware_to_gi_<APPNAME>_<TIMESTAMP>.csv`
 - `placement_node_loading_<TIMESTAMP>.csv`

Note that the `Data` constructor will raise `RuntimeError` if there are
multiple files in the directory with different `<APPNAME>`s and `<TIMESTAMP>`s.

Once you've loaded your data, you can draw histograms using the methods:

```python
pp.mailbox_loading_histogram
pp.core_loading_histogram
pp.mailbox_edge_loading_histogram
pp.application_edge_cost_histogram
```

which you'll then need to save. You can also draw maps with:

```python
pp.draw_map
```

If you want to know more about these drawing methods, they all have
docstrings. Feel free to `help(pp.draw_map)`.
