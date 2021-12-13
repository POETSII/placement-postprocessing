#!/usr/bin/env python3
import placement_postprocessing as pp
import sys

def main(path: str="example_data/") -> None:
    data = pp.Data(path)
    pp.mailbox_loading_histogram(data)\
        .savefig("mailbox_loading.pdf")
    pp.core_loading_histogram(data, plotArgs={"bins": 4})\
        .savefig("core_loading.pdf")
    pp.mailbox_edge_loading_histogram(data, plotArgs={"bins": 8})\
        .savefig("edge_loading.pdf")
    pp.application_edge_cost_histogram(data)\
        .savefig("app_edge_costs.pdf")
    pp.draw_map(data, outPath="map.pdf")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
