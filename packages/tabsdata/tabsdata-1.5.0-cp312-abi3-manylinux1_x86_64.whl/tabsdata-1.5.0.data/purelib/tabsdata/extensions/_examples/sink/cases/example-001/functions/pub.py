#
#  Copyright 2025. Tabs Data Inc.
#

import os

from utils import example_data_dir

import tabsdata as td
import tabsdata.tableframe as tdf

# IMPORTANT: This example assumes that the server and the client are running
#            in the same host.
data_dir = example_data_dir()


#
# Publisher that loads CSV data from a fixed file into a TabsData table.
#
@td.publisher(
    source=td.LocalFileSource(os.path.join(data_dir, "persons.csv")),
    tables="persons",
)
def pub(persons: tdf.TableFrame | None) -> tdf.TableFrame | None:

    # If there is no file when the publisher is executed, the publisher
    # function receives a None value for the 'persons' parameter.

    # If the publisher returns a None, the new version of the
    # Tabsdata table 'persons' is empty and without columns.
    return persons
