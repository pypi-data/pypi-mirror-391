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
# Publisher that loads CSV data from a multiple files into multiple tables
# keeping track of the last loaded file(s) into a TabsData table (using
# the files' last_modified time).
#
@td.publisher(
    source=td.LocalFileSource(
        path=[
            os.path.join(data_dir, "persons.csv"),
            os.path.join(data_dir, "cities.csv"),
        ],
        initial_last_modified="2024-05-07T00:00:00Z",
    ),
    tables=["persons", "cities"],
)
def pub(
    persons: tdf.TableFrame, cities: tdf.TableFrame
) -> (tdf.TableFrame, tdf.TableFrame):

    # If there is no new file(s) when the publisher is executed, the publisher
    # function receives a None value for the corresponding parameter.

    # If the publisher returns a None, the new version of the
    # corresponding Tabsdata table is empty and without columns.
    return persons, cities
