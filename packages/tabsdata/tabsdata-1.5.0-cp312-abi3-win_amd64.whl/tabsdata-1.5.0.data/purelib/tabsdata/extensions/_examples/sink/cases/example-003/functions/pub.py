#
#  Copyright 2025. Tabs Data Inc.
#

import os
from typing import List

from utils import example_data_dir

import tabsdata as td
import tabsdata.tableframe as tdf

# IMPORTANT: This example assumes that the server and the client are running
#            in the same host.
data_dir = example_data_dir()


#
# Publisher that loads CSV data from a multiple files keeping track of the last
# loaded file (using the files' last_modified time) into a TabsData table.
#
@td.publisher(
    source=td.LocalFileSource(
        path=os.path.join(data_dir, "persons-*.csv"),
        initial_last_modified="2024-05-07T00:00:00Z",
    ),
    tables="persons",
)
def pub(persons: List[tdf.TableFrame]) -> tdf.TableFrame | None:
    # If there are no files matching the pattern, the publisher function
    # receives an empty list for the 'persons' parameter.

    if persons:
        # Concatenate all the TableFrames in the list into a single
        # TableFrame.
        return tdf.concat(persons)

    else:
        # If the publisher returns a None, the new version of the
        # Tabsdata table 'persons' is empty and without columns.
        return None
