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
