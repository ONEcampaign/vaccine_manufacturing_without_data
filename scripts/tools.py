import json
import os

import pandas as pd


def df_to_key_number_dict(
    df: pd.DataFrame,
    indicator_name: str,
    id_column: str,
    value_columns: str | list[str],
) -> dict:
    """Convert values in a column to a dictionary of key numbers."""
    if isinstance(value_columns, str):
        value_columns = [value_columns]

    return (
        df.assign(indicator=indicator_name)
        .filter(["indicator", id_column] + value_columns, axis=1)
        .groupby(["indicator"], observed=True, dropna=False)
        .apply(
            lambda x: x.set_index(id_column)[value_columns]
            .astype(str)
            .to_dict(orient="index")
        )
        .to_dict()
    )


def update_key_number(path: str, new_dict: dict) -> None:
    """Update a key number json by updating it with a new dictionary"""

    # Check if the file exists, if not create
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

    with open(path, "r") as f:
        data = json.load(f)

    for k in new_dict.keys():
        data[k] = new_dict[k]

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
