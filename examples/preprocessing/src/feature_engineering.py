"""This example demonstrates how pypely can be used for feature engineering tasks."""

from pathlib import Path
from typing import Any, Callable, Iterable

import pandas as pd

from pypely import pipeline

HERE = Path(__file__).parent.resolve()
PATH = HERE.parent / "data/modcloth_final_data.json"


def main():
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    process = pipeline(
        load_data,
        rename_columns,
        sort_columns,
        clean_data,
        add_first_time_user,
        hips_to_bins,
        remove_unrequired_entries,
    )

    df = process()

    print()
    print("================================")
    print("Resulting DataFrame Info:")
    print(df.info())


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return pipeline(
        height_to_centimeter,
        column_to_category("bra_size"),
        column_to_category("shoe_size"),
        column_to_category("shoe_width"),
        column_to_category("cup_size"),
        cast_column_to_type("quality", "category"),
        cast_column_to_type("category", "category"),
        cast_column_to_type("fit", "category"),
        fill_na_in_column("review_summary", "Unknown"),
        fill_na_in_column("review_text", "Unknown"),
    )(df)


def remove_unrequired_entries(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return pipeline(
        drop_columns(["waist", "bust", "user_name"]),
        remove_missing_rows("height"),
        remove_missing_rows("length"),
        remove_missing_rows("quality"),
    )(df)


def sort_columns(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return df.reindex(sorted(df.columns), axis=1)


def column_to_category(column: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return pipeline(fill_na_in_column(column, "Unknown"), cast_column_to_type(column, "category"))


def hips_to_bins(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    bins = [-5, 0, 31, 37, 40, 44, 75]
    labels = ["Unknown", "XS", "S", "M", "L", "XL"]

    def set_labels(df: pd.DataFrame) -> pd.DataFrame:
        return pd.cut(df.hips, bins, labels=labels)

    bin_hips = pipeline(fill_na_in_column("hips", -1), set_labels)

    print("Bin hips column")
    df.hips = bin_hips(df)
    return df


def drop_columns(columns: Iterable[str]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def _inner(df: pd.DataFrame) -> pd.DataFrame:
        print(f"Removing columns {columns}")
        return df.drop(columns, axis=1)

    return _inner


def remove_missing_rows(column: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def _inner(df: pd.DataFrame) -> pd.DataFrame:
        print(f"Remove rows with empty value in column {column}")
        return df.drop(df[df[column].isnull()].index, axis=0)

    return _inner


def fill_na_in_column(column: str, value: Any) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def _inner(df: pd.DataFrame) -> pd.DataFrame:
        print(f"Fill Na in {column} with value {value}")
        return df.fillna({column: value})

    return _inner


def cast_column_to_type(column: str, _type: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def _inner(df: pd.DataFrame) -> pd.DataFrame:
        print(f"Casting {column} to  {_type}")
        return df.astype({column: _type})

    return _inner


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return df.rename(columns=lambda name: name.replace(" ", "_"))


def height_to_centimeter(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def get_cms(x):
        if type(x) == type(1.0):
            return

        try:
            return (int(x[0]) * 30.48) + (int(x[4:-2]) * 2.54)
        except:
            return int(x[0]) * 30.48

    print("Change height to centimeters")
    df.height = df.height.apply(get_cms)
    return df


def add_first_time_user(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    lingerie_cond = (
        ((df.bra_size != "Unknown") | (df.cup_size != "Unknown"))
        & (df.height.isnull())
        & (df.hips.isnull())
        & (df.shoe_size.isnull())
        & (df.shoe_width.isnull())
        & (df.waist.isnull())
    )
    shoe_cond = (
        (df.bra_size == "Unknown")
        & (df.cup_size == "Unknown")
        & (df.height.isnull())
        & (df.hips.isnull())
        & ((df.shoe_size.notnull()) | (df.shoe_width.notnull()))
        & (df.waist.isnull())
    )
    dress_cond = (
        (df.bra_size == "Unknown")
        & (df.cup_size == "Unknown")
        & (df.height.isnull())
        & ((df.hips.notnull()) | (df.waist.notnull()))
        & (df.shoe_size.isnull())
        & (df.shoe_width.isnull())
    )

    print("Calculate feature 'first_time_user'")
    df["first_time_user"] = lingerie_cond | shoe_cond | dress_cond
    return df


def load_data() -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    print(f"Load data from {PATH}")
    return pd.read_json(PATH, lines=True)


if __name__ == "__main__":
    main()
