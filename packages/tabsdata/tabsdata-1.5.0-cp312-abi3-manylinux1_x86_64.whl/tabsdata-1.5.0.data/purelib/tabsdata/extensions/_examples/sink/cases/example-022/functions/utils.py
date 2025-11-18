#
#  Copyright 2025. Tabs Data Inc.
#

import os


def example_data_dir() -> str:
    """
    Asserts the example's data directory exists and returns its full path.
    """
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.isdir(data_dir):
        raise EnvironmentError(
            f"The example data directory '{data_dir}' does not exist.Please run the"
            " example command(s) from the `examples/examples-022` directory"
        )
    return data_dir
