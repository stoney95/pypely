"""This example script showcases how pypely can be used for outlier handling."""

from dataclasses import dataclass
from typing import Callable

import pandas as pd
import seaborn as sns

from pypely import fork, identity, merge, pipeline


@dataclass
class Boundaries:
    """noqa: D101."""

    lower: pd.Series
    upper: pd.Series


def main():
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    fill_with_boundary_value = fill_outliers(
        fill_lower=lambda df, boundaries: boundaries.lower,
        fill_upper=lambda df, boundaries: boundaries.upper,
    )

    fill_with_mean = fill_outliers(
        fill_lower=lambda df, boundaries: df.mean,
        fill_upper=lambda df, boundaries: df.mean,
    )

    pipe = pipeline(
        load_data,
        select_numeric_columns,
        fork(identity, outlier_boundaries),
        fork(
            merge(delete_outliers),
            merge(fill_with_boundary_value),
            merge(fill_with_mean),
        ),
        merge(print_results),
    )

    pipe()


def print_results(
    no_outliers: pd.DataFrame, outliers_as_boundaries: pd.DataFrame, outliers_as_mean: pd.DataFrame
) -> None:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    print(f"No outliers shape: {no_outliers.shape}")
    print(f"Outliers as boundaries shape: {outliers_as_boundaries.shape}")
    print(f"Outliers as mean shape: {outliers_as_mean.shape}")


def outlier_boundaries(df: pd.DataFrame) -> Boundaries:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    quantile_1 = df.quantile(0.25)
    quantile_3 = df.quantile(0.75)
    IQR = quantile_3 - quantile_1

    return Boundaries(lower=quantile_1 - 1.5 * IQR, upper=quantile_3 + 1.5 * IQR)


def load_data() -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return sns.load_dataset("diamonds")


def select_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return df.select_dtypes(include=["float64", "int64"]).dropna()


def delete_outliers(df: pd.DataFrame, boundaries: Boundaries) -> pd.DataFrame:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return df[~((df < boundaries.lower) | (df > boundaries.upper)).any(axis=1)]


def fill_outliers(
    fill_lower: Callable[[pd.DataFrame, Boundaries], pd.Series],
    fill_upper: Callable[[pd.DataFrame, Boundaries], pd.Series],
) -> Callable[[pd.DataFrame, Boundaries], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def __fill_outliers(df: pd.DataFrame, boundaries: Boundaries) -> pd.DataFrame:
        df[(df < boundaries.lower).any(axis=1)] = fill_lower(df, boundaries)
        df[(df > boundaries.upper).any(axis=1)] = fill_upper(df, boundaries)

        return df

    return __fill_outliers


def calculate_quantile(quantile: float) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """

    def __inner(df: pd.DataFrame) -> pd.DataFrame:
        return df.quantile(quantile)

    return __inner


if __name__ == "__main__":
    main()
