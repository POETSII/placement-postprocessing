import placement_postprocessing as pp
data = pp.Data("/home/mark/repos/orchestrator/Output/Placement")
print(data.frames["hardware node loading"].iloc[0])  # Oh dear
