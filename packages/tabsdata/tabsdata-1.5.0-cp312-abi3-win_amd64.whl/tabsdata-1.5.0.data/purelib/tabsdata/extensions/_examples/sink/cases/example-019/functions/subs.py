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
    tables="persons_under_30_in_zips_13",
    destination=td.LocalFileDestination(
        os.path.join(data_dir, "output", "persons_under_30_in_zips_13.csv")
    ),
)
def sub(df: td.TableFrame) -> td.TableFrame:
    return df
