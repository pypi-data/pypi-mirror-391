#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td

TD_COLL_0 = os.getenv("TD_COLL_0")
TD_COLL_1 = os.getenv("TD_COLL_1")
TD_COLL_2 = os.getenv("TD_COLL_2")
TD_COLL_3 = os.getenv("TD_COLL_3")
TD_COLL_4 = os.getenv("TD_COLL_4")


@td.transformer(
    input_tables=[
        f"{TD_COLL_1}/persons_1_10",
        f"{TD_COLL_1}/persons_11_20",
        f"{TD_COLL_1}/persons_21_30",
        f"{TD_COLL_1}/persons_31_40",
        f"{TD_COLL_1}/persons_41_50",
        f"{TD_COLL_2}/persons_51_60",
        f"{TD_COLL_2}/persons_61_70",
        f"{TD_COLL_2}/persons_71_80",
        f"{TD_COLL_2}/persons_81_90",
        f"{TD_COLL_2}/persons_91_100",
    ],
    output_tables="persons",
)
def aggregate(
    persons_1_10: td.TableFrame,
    persons_11_20: td.TableFrame,
    persons_21_30: td.TableFrame,
    persons_31_40: td.TableFrame,
    persons_41_50: td.TableFrame,
    persons_51_60: td.TableFrame,
    persons_61_70: td.TableFrame,
    persons_71_80: td.TableFrame,
    persons_81_90: td.TableFrame,
    persons_91_100: td.TableFrame,
) -> td.TableFrame:
    return td.concat(
        [
            persons_1_10,
            persons_11_20,
            persons_21_30,
            persons_31_40,
            persons_41_50,
            persons_51_60,
            persons_61_70,
            persons_71_80,
            persons_81_90,
            persons_91_100,
        ]
    )


@td.transformer(
    input_tables="persons",
    output_tables=["_ages_under_30", "_ages_over_30"],
)
def split_by_age(df: td.TableFrame) -> (td.TableFrame, td.TableFrame):
    under_30 = df.filter(td.col("age") < 30)
    over_30 = df.filter(td.col("age") >= 30)
    return under_30, over_30


@td.transformer(
    input_tables="persons",
    output_tables=["_zips_13", "_zips_46", "_zips_79"],
)
def split_by_zip_code(
    df: td.TableFrame,
) -> (td.TableFrame, td.TableFrame, td.TableFrame):
    zip_str = td.col("zip").cast(str)
    group_1 = df.filter(
        zip_str.str.starts_with("1")
        | zip_str.str.starts_with("2")
        | zip_str.str.starts_with("3")
    )
    group_2 = df.filter(
        zip_str.str.starts_with("4")
        | zip_str.str.starts_with("5")
        | zip_str.str.starts_with("6")
    )
    group_3 = df.filter(
        zip_str.str.starts_with("7")
        | zip_str.str.starts_with("8")
        | zip_str.str.starts_with("9")
    )
    return group_1, group_2, group_3


@td.transformer(
    input_tables=["_zips_13", "_zips_46", "_zips_79"],
    output_tables=["persons_in_zips_13", "persons_in_zips_46", "persons_in_zips_79"],
)
def strip_zip_code(
    df_13: td.TableFrame, df_46: td.TableFrame, df_79: td.TableFrame
) -> (td.TableFrame, td.TableFrame, td.TableFrame):
    group_1 = df_13.drop("zip")
    group_2 = df_46.drop("zip")
    group_3 = df_79.drop("zip")
    return group_1, group_2, group_3


@td.transformer(
    input_tables=["persons_in_zips_13", "_ages_under_30"],
    output_tables="persons_under_30_in_zips_13",
)
def merge_under_30_with_1_3_zip_codes(
    df_zip: td.TableFrame, df_under_30: td.TableFrame
) -> td.TableFrame:
    filtered_zip = df_zip.filter(td.col("age") < 30)
    return filtered_zip.join(df_under_30, on="seq", how="inner")
