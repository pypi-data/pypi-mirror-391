import pandas as pd

from atptools.dataframe.series import remove_consecutive_duplicates


def forward_fill(
    dfs: pd.Series,
    delta: pd.Timedelta = pd.Timedelta(milliseconds=1),
) -> pd.Series:
    dfs_shifted: pd.Series = dfs.shift(1)
    dfs_shifted.dropna(inplace=True)
    dfs_shifted.index = dfs_shifted.index - delta
    return pd.concat([dfs, dfs_shifted]).sort_index()


def back_fill(
    dfs: pd.Series,
    delta: pd.Timedelta = pd.Timedelta(milliseconds=1),
) -> pd.Series:
    dfs_shifted: pd.Series = dfs.shift(-1)
    dfs_shifted.dropna(inplace=True)
    dfs_shifted.index = dfs_shifted.index + delta
    return pd.concat([dfs, dfs_shifted]).sort_index()


def remove_duplicates_and_fill(dfs: pd.Series, method: str = "ffill") -> pd.Series:
    # TODO: #36 First remove duplicates, then fill (speed up the process)
    if method == "ffill":
        dfs = forward_fill(dfs=dfs)
    elif method == "bfill":
        dfs = back_fill(dfs=dfs)
    else:
        raise ValueError(f"Unsupported fill method: {method}")

    dfs = remove_consecutive_duplicates(dfs, keep="first_last")
    return dfs
