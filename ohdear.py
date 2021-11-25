import placement_postprocessing as pp
data = pp.Data("/home/mark/repos/orchestrator/Output/Placement")
print(data.frames["hardware core loading"])
print("and")
print(data.frames["hardware mailbox loading"])
# It works!
