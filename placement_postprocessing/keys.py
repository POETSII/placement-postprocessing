# Dictionary keys we use a bunch, across different classes. These keys are
# printer-friendly terse descriptions of files.
keyAppEdgeCosts = "application edge costs"
keyAppToHw = "application to hardware mapping"
keyDiagnostic = "placement diagnostics"
keyHwEdgeLoading = "hardware edge loading"
keyHwToApp = "hardware to application mapping"
keyNodeLoading = "hardware node loading"
keyNodeLoadingCore = "hardware core loading"
keyNodeLoadingMbox = "hardware mailbox loading"

# Headers for dataframes.
headers = {keyAppEdgeCosts: ("from", "to", "cost"),
           keyAppToHw: ("appnode", "hwnode"),
           keyHwEdgeLoading: ("from", "to", "load"),
           keyHwToApp: ("hwnode", "appnode"),
           keyNodeLoading: ("node", "load")}
