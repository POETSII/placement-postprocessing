import placement_postprocessing as pp
data = pp.Data("/home/mark/repos/orchestrator/Output/Placement")
pp.mailbox_loading_histogram(data).savefig("mailbox_loading.pdf")
pp.core_loading_histogram(data).savefig("core_loading.pdf")
pp.edge_loading_histogram(data).savefig("edge_loading.pdf")
