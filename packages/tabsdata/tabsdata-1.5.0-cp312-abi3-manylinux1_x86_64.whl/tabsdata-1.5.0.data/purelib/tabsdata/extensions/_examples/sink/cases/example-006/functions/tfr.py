#
#  Copyright 2025. Tabs Data Inc.
#
from typing import Tuple

import tabsdata as td
import tabsdata.tableframe as tdf
import tabsdata.tableframe.selectors as cs


#
# The current table keeps a copy of thhe
#
@td.transformer(
    input_tables=["persons_current@HEAD", "persons"],
    output_tables=["persons_current", "persons_cdc"],
)
def tfr(
    current: tdf.TableFrame, new: tdf.TableFrame
) -> Tuple[tdf.TableFrame, tdf.TableFrame]:

    # First execution, we make current to have the schema of new
    if not current:
        current = new.clear()

    # new came empty, no data, no changes for current, no cdc
    if not new:
        return current, tdf.TableFrame.empty()

    added = (
        new.join(current, on="id", how="left", suffix="_old")
        .filter(tdf.col("first_old").is_null())
        .drop(cs.matches(".*_old"))
        .with_columns(tdf.lit("INS").alias("operation"))
    )

    deleted = (
        current.join(new, on="id", how="left", suffix="_new")
        .filter(tdf.col("first_new").is_null())
        .drop(cs.matches(".*_new"))
        .with_columns(tdf.lit("DEL").alias("operation"))
    )
    print("\n added:", added)
    print("\n deleted:", deleted)

    cdc = tdf.concat([deleted, added]).sort(by="id")

    return new, cdc
