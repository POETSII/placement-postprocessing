# A class that manages the reading and containment of placement data from the
# Orchestrator.

import os
import pandas as pd
import re

# Regular expressions for common capture groups in data file handles.
reAppname = ".+"
reTimestamp = "[0-9]{4}(?:-[0-9]{2}){2}T[0-9]{2}(?:-[0-9]{2}){2}"

# Regular expressions for expected data file handles.
reAppEdgeCosts = ("placement_gi_edges_({})_({})\.csv"
                  .format(reAppname, reTimestamp))
reAppToHw = ("placement_gi_to_hardware_({})_({})\.csv"
             .format(reAppname, reTimestamp))
reDiagnostic = ("placement_diagnostics_({})_({})\.txt"
                .format(reAppname, reTimestamp))
reHwEdgeLoading = ("placement_edge_loading_({})\.csv"
                   .format(reTimestamp))
reHwToApp = ("placement_hardware_to_gi_({})_({})\.csv"
             .format(reAppname, reTimestamp))
reNodeLoading = ("placement_node_loading_({})\.csv"
                 .format(reTimestamp))

# Dictionary keys (printer-friendly terse descriptions of files)
keyAppEdgeCosts = "application edge costs"
keyAppToHw = "application to hardware mapping"
keyDiagnostic = "placement diagnostics"
keyHwEdgeLoading = "hardware edge loading"
keyHwToApp = "hardware to application mapping"
keyNodeLoading = "hardware node loading"

# Headers for dataframes
headers = {keyAppEdgeCosts: ("from", "to", "cost"),
           keyAppToHw: ("appnode", "hwnode"),
           keyHwEdgeLoading: ("from", "to", "load"),
           keyHwToApp: ("hwnode", "appnode"),
           keyNodeLoading: ("core", "load")}

portfolio = {keyAppEdgeCosts: reAppEdgeCosts,
             keyAppToHw: reAppToHw,
             keyDiagnostic: reDiagnostic,
             keyHwEdgeLoading: reHwEdgeLoading,
             keyHwToApp: reHwToApp,
             keyNodeLoading: reNodeLoading}


class Data:

    # Fields for each file, to be populated with strings in self.detect_files.
    files = {key: None for key in portfolio.keys()}

    # Dataframes for each CSV, to be populated in self.read_files.
    frames = {item[0]: None for item in
              filter(lambda x: x[1].split(".")[-1] == "csv",
                     portfolio.items())}

    # The directory holding the files we're processing.
    dataDir = None

    def __init__(self, path: str) -> None:
        """
        Constructs a placement data object from the data found within the
        directory at `path`.
        """
        self.dataDir = path
        self.detect_files()
        self.read_files()


    def detect_files(self) -> None:
        """
        Checks `dataDir` for placement files. Raises a RuntimeError if:

         - The path is not a directory.
         - Any of the expected files is not found, or is found more than once.
         - Any of the files have conflicting application names.
         - Any of the files have conflicting timestamps.

        Sets the values for each key in `self.files`, if there were no
        errors. If there were errors, the values in `self.files` are all set to
        None.

        Note that any other miscellaneous files (like readme.md) are simply
        ignored.

        The expected files correspond to the items in the module-level
        `portfolio` dictionary, and their meaning is described in the
        Orchestrator documentation.
        """

        # Sanity
        if (not os.path.isdir(self.dataDir)):
            tmp = self.dataDir
            self.dataDir = None
            raise ValueError("Could not find a directory at '{}.".format(tmp))

        # Check every file is there. Throw a wobbly if:
        #  - there is not exactly one match per expected file
        #  - appnames are inconsistent
        #  - timestamps are inconsistent
        appname = None
        timestamp = None

        try:

            # Check every file against every regex
            for handle in os.listdir(self.dataDir):
                for index in portfolio.keys():

                    # The actual work
                    match = re.fullmatch(portfolio[index], handle)

                    # Only one file should match each type of regex.
                    if match:
                        if self.files[index]:
                            raise RuntimeError(
                                "Files '{}' and '{}' are both {} "
                                "files. Ensure only one placement run is in "
                                "the target directory."
                                .format(handle, self.files[index], index))
                        self.files[index] = handle
                    else:
                        continue  # We'll be back, probably

                    # If there are two captured groups (the parentheses), the
                    # first is the appname and the second is the timestamp. If
                    # there is one group, it is the timestamp. If there are
                    # more than two groups, something's gone horribly wrong.
                    groups = match.groups()
                    if len(groups) > 2:
                        raise RuntimeError(
                            "Unknown error when matching expression '{}' to "
                            "file '{}'. Not really sure what to say to "
                            "this. There were {} matches."
                            .format(portfolio[index], handle, len(groups)))
                    elif len(groups) == 2:
                        appnameGroup = groups[0]
                        timestampGroup = groups[1]
                    else:  # We've already checked zero.
                        appnameGroup = None
                        timestampGroup = groups[0]

                    # Are timestamps consistent?
                    if timestamp and timestampGroup != timestamp:
                        raise RuntimeError(
                            "File '{}' has a different timestamp. Ensure only "
                            "one placement run is in the target directory."
                            .format(handle))
                    timestamp = timestampGroup

                    # Are appnames consistent? (not all expressions...)
                    if appnameGroup and appname and appnameGroup != appname:
                        raise RuntimeError(
                            "File '{}' has a different appname. Ensure only "
                            "one placement run is in the target directory."
                            .format(handle))
                        appname = appnameGroup

            # Check that all files were found at least once.
            if None in self.files.values():
                raise RuntimeError(
                    "Files '{}' missing from target directory."
                    .format(", ".join(
                        [item[0] for item in filter(lambda x: x[1] is None,
                                                    self.files.items())])))

        # Reset self.files on error.
        except RuntimeError:
            self.files = {key: None for key in portfolio.keys()}
            raise

    def read_files(self):
        """
        Opens each detected CSV file as a pandas dataframe. Raises a
        RuntimeError if:

         - Any files have not been detected yet.

        Sets the values for each key in `self.frames`, if there were no
        errors. If there were errors, the values in `self.files` are all set to
        None.

        Also see `self.detect_files`.
        """

        try:
            # Sanity
            if None in self.files.values():
                raise RuntimeError(
                    "Files '{}' have not been detected. Have you called "
                    "`detect_files` yet?"
                    .format(", ".join(
                        [item[0] for item in filter(lambda x: x[1] is None,
                                                    self.files.items())])))

            # Load 'em up.
            for key in self.frames.keys():
                self.frames[key] = pd.read_csv(
                    os.path.join(self.dataDir, self.files[key]),
                    names=headers[key])

        except RuntimeError:
            self.frames = {key: None for key in self.frames.keys()}
            raise
