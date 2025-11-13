import pandas as pd


def _remove_consecutive_duplicates_keep_fist(dfs: pd.Series) -> pd.Series:
    dfs_diff: pd.Series = dfs.diff()
    return dfs[dfs_diff != 0]


def _remove_consecutive_duplicates_keep_last(dfs: pd.Series) -> pd.Series:
    dfs_diff: pd.Series = dfs.diff(-1)
    return dfs[dfs_diff != 0]


def _remove_consecutive_duplicates_keep_first_last(
    dfs: pd.Series,
) -> pd.Series:
    dfs_diff_1: pd.Series = dfs.diff()
    dfs_diff_2: pd.Series = dfs.diff(-1)
    return dfs[(dfs_diff_2 != 0) | (dfs_diff_1 != 0)]


def remove_consecutive_duplicates(
    dfs: pd.Series,
    keep: str = "first",
) -> pd.Series:
    if keep == "first":
        return _remove_consecutive_duplicates_keep_fist(dfs)
    elif keep == "last":
        return _remove_consecutive_duplicates_keep_last(dfs)
    elif keep == "first_last":
        return _remove_consecutive_duplicates_keep_first_last(dfs)
    else:
        raise ValueError(f"Unsupported keep method: {keep}")
