import numpy as np
import pandas as pd


def datetimeindex_to_seconds_array(index: pd.Index) -> np.ndarray:
    index_seconds = np.array(
        pd.DatetimeIndex(index).to_pydatetime(),
        dtype=np.datetime64,
    )

    index_seconds_zero: np.ndarray = (
        index_seconds - index_seconds[0]
    ) / np.timedelta64(1, "s")

    index_seconds_zero: np.ndarray = index_seconds_zero.astype(float)
    return index_seconds_zero
