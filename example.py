#!/usr/bin/env python3

import placement_postprocessing as pp
data = pp.Data("example_data/")
pp.mailbox_loading_histogram(data).savefig("mailbox_loading.pdf")
pp.core_loading_histogram(data,
                          plotArgs={"bins": 4}).savefig("core_loading.pdf")
pp.mailbox_edge_loading_histogram(data,
                                  plotArgs={"bins": 8}).savefig("edge_loading.pdf")
pp.application_edge_cost_histogram(data).savefig("app_edge_costs.pdf")
pp.draw_map(data, outPath="map.pdf", cleanup=False)
