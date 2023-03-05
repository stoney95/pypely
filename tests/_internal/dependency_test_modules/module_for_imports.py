import json

import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal as equal_frame

from .helper_module import try_request


def add(x: int, y: int) -> int:
    try_request()
    return x + y


def process(df: pd.DataFrame) -> np.ndarray:
    json.dumps(dict(test=2))

    arr = df.to_numpy()
    ones = np.ones(arr.shape)

    assert_array_equal(ones, ones)
    equal_frame(df, df)

    return arr + ones
