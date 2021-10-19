"""
This script will apply the pypely approach to the code 
in the section: Data Cleaning -> Outlier Detection
of the referenced guide
"""

from pypely import pipeline, fork, merge, identity
import seaborn as sns
from collections import namedtuple

Boundaries = namedtuple('Boundaries', ['lower', 'upper'])

def main():
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
        fork(
            identity,
            outlier_boundaries
        ),
        fork(
            merge(delete_outliers),
            merge(fill_with_boundary_value),
            merge(fill_with_mean),
        ),
        merge(print_results)
    )

    pipe()


def print_results(no_outliers, outliers_as_boundaries, outliers_as_mean):
    print(f"No outliers shape: {no_outliers.shape}")
    print(f"Outliers as boundaries shape: {outliers_as_boundaries.shape}")
    print(f"Outliers as mean shape: {outliers_as_mean.shape}")


def outlier_boundaries(df):
    quantile_1 = df.quantile(0.25)
    quantile_3 = df.quantile(0.75)
    IQR = quantile_3 - quantile_1

    return Boundaries(
        lower=quantile_1 - 1.5 * IQR,
        upper=quantile_3 + 1.5 * IQR
    )


def load_data():
    return sns.load_dataset('diamonds')


def select_numeric_columns(df):
    return df\
        .select_dtypes(include=["float64","int64"])\
        .dropna()


def delete_outliers(df, boundaries: Boundaries):
    return df[~(
        (df < boundaries.lower) | 
        (df > boundaries.upper)
    ).any(axis=1)]


def fill_outliers(fill_lower, fill_upper):
    def __fill_outliers(df, boundaries, fill_lower, fill_upper):
        df[(df < boundaries.lower).any(axis=1)] = fill_lower(df, boundaries)
        df[(df > boundaries.upper).any(axis=1)] = fill_upper(df, boundaries)

        return df

    return lambda df, boundaries: __fill_outliers(df, boundaries, fill_lower, fill_upper)


"""
Less readable stuff
"""

def oulier_boundaries_hard(df):
    def __boundaries(lower_fence, upper_fence):
        return lambda quantiles, IQR: Boundaries(
            lower=lower_fence(quantiles[0], IQR), 
            upper=upper_fence(quantiles[1], IQR)
        )

    pipe = pipeline(
        fork(
            calculate_quantile(0.25),
            calculate_quantile(0.75)
        ),
        fork(
            identity,
            lambda x: x[1] - x[0]
        ),
        merge(
            __boundaries(
                calculate_fence(aggregation=lambda x, y: x - y, factor=1.5),
                calculate_fence(aggregation=lambda x, y: x + y, factor=1.5),
            )
        )
    )

    return pipe(df)


def calculate_quantile(quantile):
    return lambda df: df.quantile(quantile)


def calculate_fence(aggregation, factor):
    return lambda quantile, _range: aggregation(quantile,  factor * _range)


if __name__ == "__main__":
    main()