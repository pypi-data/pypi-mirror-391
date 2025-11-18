#
#  Copyright 2025. Tabs Data Inc.
#

import os

from utils import example_data_dir

import tabsdata as td

# IMPORTANT: This example assumes that the server and the client are running
#            in the same host.
data_dir = example_data_dir()


@td.subscriber(
    tables="persons",
    destination=td.LocalFileDestination(
        os.path.join(data_dir, "output", "persons.csv")
    ),
)
def sub(df: td.TableFrame) -> td.TableFrame:
    return df
