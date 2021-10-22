from preprocessing.src.feature_engineering import load_data, rename_columns
from pytest import fixture
from functools import lru_cache
from pypely import pipeline


@fixture()
@lru_cache(maxsize=32)
def data_snippet():
    data = pipeline(
        load_data,
        rename_columns
    )()
    
    return data.iloc[:10000]