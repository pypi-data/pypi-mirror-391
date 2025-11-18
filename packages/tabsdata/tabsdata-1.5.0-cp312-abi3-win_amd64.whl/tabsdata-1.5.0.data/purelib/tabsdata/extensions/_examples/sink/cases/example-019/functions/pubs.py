#
#  Copyright 2025. Tabs Data Inc.
#

import os
from datetime import datetime

from utils import example_data_dir

import tabsdata as td
import tabsdata.tableframe as tdf

# IMPORTANT: This example assumes that the server and the client are running
#            in the same host.
data_dir = example_data_dir()


@td.publisher(
    source=td.LocalFileSource(os.path.join(data_dir, "dummy.csv")),
    tables="trigger_table",
)
def main_trigger(_df: tdf.TableFrame) -> tdf.TableFrame:
    current_time = datetime.now()
    return tdf.TableFrame(
        {
            "timestamp": [current_time],
        },
    )


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_1_10.csv")),
    tables="persons_1_10",
)
def pub_1_10(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_11_20.csv")),
    tables="persons_11_20",
)
def pub_11_20(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_21_30.csv")),
    tables="persons_21_30",
)
def pub_21_30(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_31_40.csv")),
    tables="persons_31_40",
)
def pub_31_40(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_41_50.csv")),
    tables="persons_41_50",
)
def pub_41_50(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_51_60.csv")),
    tables="persons_51_60",
)
def pub_51_60(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_61_70.csv")),
    tables="persons_61_70",
)
def pub_61_70(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_71_80.csv")),
    tables="persons_71_80",
)
def pub_71_80(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_81_90.csv")),
    tables="persons_81_90",
)
def pub_81_90(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


@td.publisher(
    trigger_by="trigger_table",
    source=td.LocalFileSource(os.path.join(data_dir, "persons_91_100.csv")),
    tables="persons_91_100",
)
def pub_91_100(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
