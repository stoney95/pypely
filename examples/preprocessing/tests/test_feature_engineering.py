from pandas.api.types import CategoricalDtype
from preprocessing.src.feature_engineering import (
    add_first_time_user,
    clean_data,
    hips_to_bins,
    main,
    remove_unrequired_entries,
)

from pypely import pipeline


def test_main(mocker, data_snippet):
    mocker.patch("preprocessing.src.feature_engineering.load_data", return_value=data_snippet)

    main()


def test_clean_data(data_snippet):
    to_test = clean_data(data_snippet)

    expected_category_columns = ["bra_size", "category", "cup_size", "fit", "quality", "shoe_size", "shoe_width"]
    category_type = [is_type_category(to_test, col) for col in expected_category_columns]
    assert all(category_type)


def test_add_first_time_user(data_snippet):
    to_test = pipeline(
        clean_data,
        add_first_time_user,
    )(data_snippet)

    assert "first_time_user" in to_test.columns


def test_hips_to_bins(data_snippet):
    to_test = hips_to_bins(data_snippet)

    assert is_type_category(to_test, "hips")
    assert has_no_NaN_entries(to_test, "hips")


def test_remove_unrequired_entries(data_snippet):
    to_test = remove_unrequired_entries(data_snippet)
    expected_removed_columns = ["waist", "bust", "user_name"]
    column_not_in_to_test = [not has_column(to_test, col) for col in expected_removed_columns]

    assert has_no_NaN_entries(to_test, "height")
    assert has_no_NaN_entries(to_test, "length")
    assert has_no_NaN_entries(to_test, "quality")
    assert all(column_not_in_to_test)


def has_column(df, col):
    return col in df.columns


def has_no_NaN_entries(to_test, col):
    return sum(to_test[col].isnull()) == 0


def is_type_category(df, column):
    return type(df[column].dtype) == CategoricalDtype
