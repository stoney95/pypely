"""
This script will apply the pypely approach the code of the referenced guide
that can be found in the section: Data Cleaning -> Outlier Detection
"""


from pypely import pipeline, fork, merge, identity
import seaborn as sns
from collections import namedtuple

Fences = namedtuple('Fences', ['lower', 'upper'])

def main():
    fill_with_fences = fill_outliers(
        fill_lower=lambda df, fences: fences.lower,
        fill_upper=lambda df, fences: fences.upper,
    )

    fill_with_mean = fill_outliers(
        fill_lower=lambda df, fences: df.mean,
        fill_upper=lambda df, fences: df.mean,
    )

    pipe = pipeline(
        load_data,
        select_numeric_columns,
        fork(
            identity,
            calculate_fences
        ),
        fork(
            merge(delete_outliers),
            merge(fill_with_fences),
            merge(fill_with_mean),
        ),
        merge(print_results)
    )

    pipe()


def print_results(no_outliers, outliers_as_fences, outliers_as_mean):
    print(f"No outliers shape: {no_outliers.shape}")
    print(f"Outliers as fences shape: {outliers_as_fences.shape}")
    print(f"Outliers as mean shape: {outliers_as_mean.shape}")


def calculate_fences(df):
    quantile_1 = df.quantile(0.25)
    quantile_3 = df.quantile(0.75)
    IQR = quantile_3 - quantile_1

    return Fences(
        lower=quantile_1 - 1.5 * IQR,
        upper=quantile_3 + 1.5 * IQR
    )


def load_data():
    return sns.load_dataset('diamonds')


def select_numeric_columns(df):
    return df\
        .select_dtypes(include=["float64","int64"])\
        .dropna()


def delete_outliers(df, fences: Fences):
    return df[~(
        (df < fences.lower) | 
        (df > fences.upper)
    ).any(axis=1)]


def fill_outliers(fill_lower, fill_upper):
    def __fill_outliers(df, fences, fill_lower, fill_upper):
        df[(df < fences.lower).any(axis=1)] = fill_lower(df, fences)
        df[(df > fences.upper).any(axis=1)] = fill_upper(df, fences)

        return df

    return lambda df, fences: __fill_outliers(df, fences, fill_lower, fill_upper)


"""
Less readable stuff
"""

def calculate_fences_hard(df):
    def __fences(lower_fence, upper_fence):
        return lambda quantiles, IQR: Fences(
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
            __fences(
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