#
#  Copyright 2025. Tabs Data Inc.
#

import os

from utils import example_data_dir

import tabsdata as td

# IMPORTANT: This example assumes that the server and the client are running
#            in the same host.
data_dir = example_data_dir()


#
# Publisher that loads CSV data from a single file into a TabsData table.
#
@td.publisher(
    source=td.LocalFileSource(path=os.path.join(data_dir, "persons.csv")),
    tables="persons",
)
def pub(persons: td.TableFrame):
    return persons
