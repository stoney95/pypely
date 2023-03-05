import pandas as pd
from preprocessing.src.outlier_handling import (
    calculate_quantile,
    delete_outliers,
    fill_outliers,
    load_data,
    main,
    outlier_boundaries,
    select_numeric_columns,
)

DF = pd.DataFrame.from_dict({"test": [-100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]})


def test_calculate_quantile():
    quantile_25 = calculate_quantile(0.25)
    quantile_75 = calculate_quantile(0.75)

    df_quantile_50 = quantile_25(DF)
    df_quantile_75 = quantile_75(DF)

    assert df_quantile_50["test"] == 2.75
    assert df_quantile_75["test"] == 8.25


def test_outlier_boundaries():
    boundaries = outlier_boundaries(DF)

    assert boundaries.lower["test"] == -5.5
    assert boundaries.upper["test"] == 16.5


def test_select_numeric_columns():
    numeric_only = select_numeric_columns(DF)
    assert numeric_only.columns == DF.columns


def test_delete_outliers():
    boundaries = outlier_boundaries(DF)
    to_test = delete_outliers(DF, boundaries)
    to_test = to_test.reset_index(drop=True)

    expected = pd.DataFrame.from_dict({"test": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}).reset_index(drop=True)

    print(to_test)
    print()
    print(expected)

    assert to_test.equals(expected)


def test_fill_outliers():
    boundaries = outlier_boundaries(DF)
    fill_with_boundaries = fill_outliers(
        lambda _, boundaries: boundaries.lower, lambda _, boundaries: boundaries.upper
    )

    to_test = fill_with_boundaries(DF, boundaries).reset_index(drop=True)
    expected = pd.DataFrame.from_dict({"test": [-5.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16.5]})

    assert to_test.equals(expected)


def test_load_data():
    test_df = load_data()

    expected_columns = ["carat", "cut", "color", "clarity", "depth", "table", "price", "x", "y", "z"]
    assert list(test_df.columns) == expected_columns


def test_main(mocker):
    mocker.patch("preprocessing.src.outlier_handling.load_data", return_value=DF)

    main()
