#
#  Copyright 2025. Tabs Data Inc.
#

import tabsdata as td
import tabsdata.tableframe as tdf


#
# Transformer that appends the new_persons table to the persons table.
#
@td.transformer(
    input_tables=["persons@HEAD", "new_persons"],
    output_tables="persons",
)
def tfr(current_persons: tdf.TableFrame, new_persons: tdf.TableFrame) -> tdf.TableFrame:

    # No new persons, return current persons
    if not new_persons:
        return current_persons

    # No current persons, return new persons
    if not current_persons:
        return new_persons

    # Append current persons with new persons
    return tdf.concat([new_persons, current_persons])
