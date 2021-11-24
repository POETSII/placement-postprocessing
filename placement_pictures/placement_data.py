# A class that manages the reading and containment of placement data from the
# Orchestrator.

import os
import pandas as pd
import re

class PlacementData:

    # Fields for each file, populated with strings
    fileDiagnostics = None
    fileGiToHardware = None
    fileNodeLoading = None

    def __init__(self, str: path) -> None:
        """
        Constructs a placement data object from the data found within the
        directory at `path`.
        """

        # Sanity
        if (not os.path.isdir(path)):
            raise ValueError("Could not find a directory at '{}.".format(path))

        # Does the path contain a diagnostics file? If so, grab it.
